#!/usr/bin/env python3
"""Audit en lecture seule : années prouvées par le lien VIN -> ECU -> portée -> entrée.

Les périodes non directement justifiées sont des candidats distincts.
Ne modifie et ne publie jamais les SQLite ni les packs d'origine.
"""
import argparse
from collections import Counter, defaultdict
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_published_model_years import decrypt_pack

VIN = re.compile(r"(\d{5,8})$")
YEAR_ARROW = re.compile(r"(?<!\d)((?:19|20)\d{2})\s*(?:->|→)")

def rows(db, table):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone():
        return []
    db.row_factory=sqlite3.Row
    return [dict(r) for r in db.execute('SELECT * FROM "'+table+'"')]

def vin_tail(v):
    m=VIN.search(str(v or "").strip())
    return str(int(m.group(1))) if m else ""

def source_year(start,variant):
    v=str(start or "").strip()
    if v.isdigit() and 1980<=int(v)<=2035:
        return int(v)
    m=YEAR_ARROW.search(str(variant or ""))
    return int(m.group(1)) if m else None

def reference_db(root):
    from build_rave_fr_documentary import decode_qz64
    parts=sorted(root.glob("mems_reference_seed_*.qz64"))
    if len(parts)!=4:
        raise RuntimeError("FOUR_REFERENCE_SEED_FILES_REQUIRED")
    sql=decode_qz64(b"".join(p.read_bytes().strip() for p in parts))
    db=sqlite3.connect(":memory:")
    for line in sql.splitlines():
        if line.strip():
            db.execute(line.strip())
    return db

def ecu_fitments(reference):
    grouped=defaultdict(list)
    for r in rows(reference,"ecu_fitment"):
        if str(r.get("model") or "").lower()!="mini":
            continue
        vin=vin_tail(r.get("vin_from"))
        y=source_year(r.get("year_from"),r.get("variant"))
        if not vin or not y:
            continue
        end=source_year(r.get("year_to"),"")
        period=f"{y%100:02d}-{end%100:02d}" if end and end>=y else f"{y%100:02d}+"
        grouped[vin].append((period,str(r.get("part_number") or "")))
    unique={}
    rejected={}
    for vin,records in grouped.items():
        kinds={p for p,_ in records}
        if len(kinds)==1:
            unique[vin]={"period":next(iter(kinds)),"sources":len(records),
                         "parts":sorted({p for _,p in records})}
        else:
            rejected[vin]=sorted(kinds)
    return unique,rejected

def native_pack(zip_data,language):
    with zipfile.ZipFile(io.BytesIO(zip_data)) as arc:
        name=f"mems_documentary_{language}.sqlite"
        if name not in arc.namelist() or arc.testzip() is not None:
            raise RuntimeError("AUTHENTICATED_NATIVE_DOCUMENTARY_ZIP_INVALID")
        with tempfile.TemporaryDirectory(prefix="mems-year-evidence-") as tmp:
            destination=Path(tmp)/name
            destination.write_bytes(arc.read(name))
            db=sqlite3.connect("file:"+str(destination)+"?mode=ro",uri=True)
            try:
                if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
                    raise RuntimeError("NATIVE_DATABASE_INTEGRITY_FAILED")
                entries=rows(db,"documentary_entries")
                source=rows(db,"documentary_source_rows")
            finally:
                db.close()
    data=defaultdict(list)
    for item in source:
        try:
            value=json.loads(item["row_json"])
            if isinstance(value,dict):
                data[item["table_name"]].append(value)
        except (ValueError,TypeError,KeyError):
            continue
    return entries,data,len(source)

def year_scopes(source,fitments):
    direct={}
    potential={}
    baselines=defaultdict(set)
    for item in source["mems_applicability_scope"]+source["mems_scope_constraint"]:
        key=str(item.get("scope_key") or "")
        if not key or str(item.get("model") or "").lower()!="mini":
            continue
        vin=vin_tail(item.get("vin_from"))
        evidence=fitments.get(vin)
        if evidence:
            direct[key]={"years":evidence["period"],"scope":key,
                         "vin":vin,"sources":evidence["sources"]}
            caption=str(item.get("source_scope_text") or "").lower()
            if "-mini-vin" in key.lower() and any(
                flag in caption for flag in ("depuis","à partir","a partir","from vin")
            ):
                parts=key.split("-")
                if len(parts)>1:
                    baselines[parts[1]].add(evidence["period"])
    for item in source["mems_applicability_scope"]:
        key=str(item.get("scope_key") or "")
        if not key or key in direct or str(item.get("model") or "").lower()!="mini":
            continue
        parts=key.split("-")
        edition=parts[1] if len(parts)>1 else ""
        periods=baselines.get(edition,set())
        if len(periods)==1 and edition.lower() in str(item.get("source_scope_text") or "").lower():
            potential[key]={"years":next(iter(periods)),"scope":key}
    return direct,potential,{k:sorted(v) for k,v in baselines.items()}

def linked_years(entries,source,direct,potential):
    scopes=defaultdict(set)
    for row in source["mems_knowledge_scope"]:
        key=row.get("knowledge_key")
        scope=row.get("scope_key")
        if key and scope:
            scopes[str(key)].add(str(scope))
    proc={str(x["procedure_key"]):str(x["knowledge_key"])
          for x in source["mems_procedure"] if x.get("procedure_key") and x.get("knowledge_key")}
    spec={str(x["spec_key"]):str(x["knowledge_key"])
          for x in source["mems_specification"] if x.get("spec_key") and x.get("knowledge_key")}
    verified=[]
    review=[]
    missing=Counter()
    for entry in entries:
        try:
            raw=json.loads(entry.get("raw_json") or "{}")
        except (ValueError,TypeError):
            raw={}
        if not isinstance(raw,dict):
            raw={}
        knowledge=str(raw.get("knowledge_key") or "")
        if not knowledge:
            knowledge=proc.get(str(raw.get("procedure_key") or ""),"")
        if not knowledge:
            knowledge=spec.get(str(raw.get("spec_key") or ""),"")
        if not knowledge:
            missing["no_knowledge_key"]+=1
            continue
        related=scopes.get(knowledge,set())
        if not related:
            missing["no_knowledge_scope"]+=1
            continue
        yes=[direct[x] for x in related if x in direct]
        maybe=[potential[x] for x in related if x in potential]
        confirmed={x["years"] for x in yes}
        candidates={x["years"] for x in maybe}
        row={"document_id":entry.get("document_id"),
             "source_revision":entry.get("source_revision"),
             "entry_id":entry.get("entry_id"),
             "source_page":entry.get("source_page"),
             "knowledge_key":knowledge}
        if len(confirmed)==1 and (not candidates or confirmed==candidates):
            row.update({"model_years":next(iter(confirmed)),
                        "basis":"exact_ecu_fitment_vin",
                        "scope_keys":sorted(x["scope"] for x in yes)})
            verified.append(row)
        elif not confirmed and len(candidates)==1:
            row.update({"candidate_years":next(iter(candidates)),
                        "basis":"same_edition_requires_review",
                        "scope_keys":sorted(x["scope"] for x in maybe)})
            review.append(row)
        else:
            missing["no_unique_year_evidence"]+=1
    return verified,review,dict(missing)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True,type=Path)
    p.add_argument("--directory",required=True,type=Path)
    p.add_argument("--source-reference",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    secret=os.environ.get("MEMS_DOCUMENTARY_PUBLISH_PASSWORD","")
    if len(secret)<12:
        raise SystemExit("SECRET_UNAVAILABLE")
    m=json.loads(args.manifest.read_text(encoding="utf-8"))["documentary_bases"]
    packs=[("FR-AKM12","fr",m["fr"]),("FR-RAVE6","fr",m["fr"]["previous_packs"][0]),("EN-RAVE48","en",m["en"])]
    ref=reference_db(args.source_reference)
    fitments,rejected=ecu_fitments(ref)
    ref.close()
    if fitments.get("134455",{}).get("period")!="96+":
        raise RuntimeError("KNOWN_VIN_134455_YEAR_NOT_CONFIRMED")
    report={"purpose":"Read-only manufacturer/ECU VIN model-year evidence; not a published database",
            "reference":{"confirmed_vin":len(fitments),"conflicting_vin":len(rejected),
                         "vin_134455_years":fitments["134455"]["period"],
                         "vin_134455_sources":fitments["134455"]["sources"]},
            "packs":[],"verified_entry_mappings":[],"review_candidates":[]}
    for label,language,desc in packs:
        filename=desc["release_url"].rsplit("/",1)[-1]
        clear=decrypt_pack(args.directory/filename,desc["sha256"],secret)
        entries,sources,native_count=native_pack(clear,language)
        del clear
        direct,potential,manual=year_scopes(sources,fitments)
        verified,review,reasons=linked_years(entries,sources,direct,potential)
        stats=defaultdict(lambda:{"entries":0,"verified":0,"needs_review":0})
        for row in entries:
            stats[str(row.get("document_id") or "")]["entries"]+=1
        for row in verified:
            stats[str(row["document_id"])]["verified"]+=1
        for row in review:
            stats[str(row["document_id"])]["needs_review"]+=1
        report["packs"].append({"pack":label,"entries":len(entries),"source_rows":native_count,
                                "direct_scopes":len(direct),"manual_scopes_needing_review":len(potential),
                                "manual_baseline_years":manual,
                                "verified_entries":len(verified),"review_candidates":len(review),
                                "unmapped_causes":reasons,"documents":dict(sorted(stats.items()))})
        report["verified_entry_mappings"].extend(verified)
        report["review_candidates"].extend(review)
        print("YEAR_MAPPING",label,"entries",len(entries),"verified",len(verified),
              "review",len(review),"exact_vin_scopes",len(direct))
        print("YEAR_MAPPING_DOCUMENTS",label,json.dumps(dict(sorted(stats.items())),ensure_ascii=False))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("YEAR_MAPPING_AUDIT_COMPLETE_NO_PACK_CHANGED_NO_SETUP")

if __name__=="__main__":
    main()
