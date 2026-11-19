#!/usr/bin/env python3
"""AKM7169FRE ORIGINAL french 20-page manufacturer chapter - read-only audit.

The 12 AKM7169ENG_FR_TRANSLATION volumes are intentionally NOT included.
The original 1993 edition year is not an applicability/model year.
Never publishes the source, decrypted files, PDF pages or long quotations.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import zipfile

from audit_published_model_years import decrypt_pack, periods_from_record
from audit_verified_year_links import reference_db

DOCUMENT="AKM7169FRE"
REVISION="MEMS-SPI-20P-ORIGINAL-FR-1993"
YEAR=re.compile(r"(?<!\d)(?:19[89]\d|20[0-3]\d)(?!\d)")
RANGE=re.compile(r"(?<!\d)(?:19[89]\d|20[0-3]\d)\s*[-–—/à]\s*(?:19[89]\d|20[0-3]\d)(?!\d)")
SHORT_RANGE=re.compile(r"(?<!\d)(?:[89]\d|0\d)\s*[-–—/]\s*(?:[89]\d|0\d)(?!\d)")
VIN=re.compile(r"\b(?:SAX[A-Z0-9]{7,15}|VIN[:\s#\-]*[A-Z0-9]{5,17})\b",re.I)
ECU_PART=re.compile(r"\b(?:MNE|MNU|MKC|MFE|MPL|MCS)\d{4,8}\b",re.I)
VERSION=re.compile(r"\b(?:MEMS\s*)?1[.,]\s*[2369]\b",re.I)
VEHICLE=re.compile(r"\b(?:mini|metro|rover|spi|monopoint|injection\s+monopoint|mpi|motorisation)\b",re.I)
KEY_SCOPE=re.compile(r"year|ann[eé]e|mod[eè]le|model|vehicle|vehicule|vin|scope|application|applicab|generation|g[eé]n[eé]ration|variant|ecu",re.I)

def report_source(db):
    db.row_factory=sqlite3.Row
    if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
        raise RuntimeError("CORRUPT_NATIVE_DOCUMENTARY_SQLITE")
    doc=db.execute("SELECT * FROM documentary_documents WHERE document_id=? AND source_revision=?",
        (DOCUMENT,REVISION)).fetchone()
    if doc is None:
        raise RuntimeError("ORIGINAL_AKM7169FRE_SOURCE_NOT_FOUND")
    doc_info=dict(doc)
    if doc_info.get("source_pages")!=20:
        raise RuntimeError("AKM7169FRE_ORIGINAL_PAGE_COUNT_CHANGED")
    rows=[dict(x) for x in db.execute(
        "SELECT document_id,source_revision,entry_id,entry_type,source_page,"
        "title,source_text,source_table,raw_json "
        "FROM documentary_entries WHERE document_id=? AND source_revision=? "
        "ORDER BY source_page,entry_id", (DOCUMENT,REVISION))]
    if len(rows)!=429:
        raise RuntimeError("AKM7169FRE_EXPECTED_429_ENTRIES_FOUND_"+str(len(rows)))
    stats=defaultdict(lambda:{"entries":0,"explicit_years":0,"year_mention":0,
                              "vin_entries":0,"ecu_part_entries":0,"mems_versions":0})
    match_years,part_refs,vin_refs=defaultdict(list),defaultdict(list),defaultdict(list)
    entry_evidence=[]
    raw_keys=Counter()
    model_year_candidates=Counter()
    ecu_versions=Counter()
    entry_types=Counter()
    source_titles=[]
    for row in rows:
        p=row.get("source_page") or 0
        entry_types[row["entry_type"]]+=1
        st=stats[p];st["entries"]+=1
        try:
            raw=json.loads(row.get("raw_json") or "{}")
        except (TypeError,ValueError):
            raw={}
        if not isinstance(raw,dict):
            raw={}
        periods=sorted(periods_from_record(raw))
        if periods:
            st["explicit_years"]+=1
            model_year_candidates.update(periods)
        text=(row.get("title") or "")+"\n"+(row.get("source_text") or "")
        year_set=sorted(set(YEAR.findall(text)))
        short=sorted(set(SHORT_RANGE.findall(text)))
        vin_set=sorted(set(VIN.findall(text)))
        part_set=sorted(set(ECU_PART.findall(text)))
        vers=sorted(set(VERSION.findall(text)))
        if year_set or short:
            st["year_mention"]+=1
            for y in year_set+short:
                match_years[y].append({"page":p,"entry_id":row["entry_id"]})
        if vin_set:
            st["vin_entries"]+=1
            for v in vin_set:vin_refs[v].append(p)
        if part_set:
            st["ecu_part_entries"]+=1
            for part in part_set:part_refs[part.upper()].append(p)
        if vers:
            st["mems_versions"]+=1
            ecu_versions.update(x.upper().replace(",",".") for x in vers)
        for key in raw:
            if KEY_SCOPE.search(key):
                raw_keys[key]+=1
        if periods or year_set or short or vin_set or part_set or vers:
            entry_evidence.append({
                "page":p,"entry_id":row["entry_id"],"type":row["entry_type"],
                "explicit_vehicle_years":periods,
                "year_tokens":year_set,
                "short_year_ranges":short,
                "vin_references":vin_set,
                "ecu_part_numbers":part_set,
                "mems_versions":vers,
                "model_year_scope_fields":{key:str(value)[:110]
                    for key,value in raw.items() if KEY_SCOPE.search(key)}
            })
        if len(source_titles)<30 and VEHICLE.search(row.get("title") or ""):
            source_titles.append({"page":p,"title":(row["title"] or "")[:90]})
    return {
        "source_id":DOCUMENT,"source_revision":REVISION,"pages":doc_info["source_pages"],
        "entries":len(rows),"entry_types":dict(entry_types),
        "year_scope_fields":dict(raw_keys),
        "explicit_application_periods":dict(model_year_candidates),
        "year_tokens_in_source_text":{k:len(v) for k,v in sorted(match_years.items())},
        "vin_references":{k:sorted(set(v)) for k,v in sorted(vin_refs.items())},
        "ecu_part_references":{k:sorted(set(v)) for k,v in sorted(part_refs.items())},
        "mems_version_mentions":dict(ecu_versions),
        "pages":dict(sorted(stats.items())),
        "evidence":entry_evidence,
        "related_titles":source_titles,
        "edition_year_not_model_year":"1993 is the original edition identity only"
    }

def fitment_evidence(reference,original):
    cols=[x[1] for x in reference.execute("PRAGMA table_info(ecu_fitment)")]
    if not cols:return {"error":"no_ecu_fitment"}
    reference.row_factory=sqlite3.Row
    fits=[dict(r) for r in reference.execute("SELECT * FROM ecu_fitment WHERE lower(model)='mini'")]
    part_set=set(original["ecu_part_references"])
    match=[]
    for row in fits:
        part=str(row.get("part_number") or "").upper()
        if part in part_set:
            match.append({"part_number":part,
                          "source_pages":original["ecu_part_references"][part],
                          "model":row.get("model"),"variant":row.get("variant"),
                          "year_from":row.get("year_from"),"year_to":row.get("year_to"),
                          "vin_from":row.get("vin_from"),"vin_to":row.get("vin_to")})
    return {"candidate_fitment_count":len(fits),
            "ecu_parts_exactly_matched":len(match),
            "matched_fitments":match,
            "note":"Only exact ECU part-number matches can prove an entry-specific vehicle period"}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--manifest",type=Path,required=True)
    a.add_argument("--pack-directory",type=Path,required=True)
    a.add_argument("--reference-root",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    m=json.loads(args.manifest.read_text(encoding="utf-8"))
    desc=m["documentary_bases"]["fr"]["previous_packs"][0]
    entries={d["document_id"]:d for d in desc["published_documents"]}
    if entries[DOCUMENT]["source_revision"]!=REVISION:
        raise RuntimeError("ORIGINAL_FRENCH_MANUAL_REVISION_MISMATCH")
    filename=desc["release_url"].rsplit("/",1)[-1]
    original=args.pack_directory/filename
    password=os.environ.get("MEMS_DOCUMENTARY_PUBLISH_PASSWORD","")
    if len(password)<12:raise RuntimeError("SECRET_MISSING")
    encrypted_sha=hashlib.sha256(original.read_bytes()).hexdigest()
    if encrypted_sha!=desc["sha256"]:raise RuntimeError("ORIGINAL_PACK_HASH_MISMATCH")
    clear=decrypt_pack(original,desc["sha256"],password)
    with zipfile.ZipFile(io.BytesIO(clear)) as archive, tempfile.TemporaryDirectory() as tmp:
        native="mems_documentary_fr.sqlite"
        if native not in archive.namelist() or archive.testzip() is not None:
            raise RuntimeError("AUTHENTICATED_ZIP_INVALID")
        path=Path(tmp)/native
        path.write_bytes(archive.read(native))
        with sqlite3.connect("file:"+str(path)+"?mode=ro",uri=True) as db:
            results=report_source(db)
    del clear
    reference=reference_db(args.reference_root)
    try:
        fits=fitment_evidence(reference,results)
    finally:
        reference.close()
    result={"audit":"French original AKM7169FRE only, read-only",
            "manual":results,"ecu_fitment_crosscheck":fits,
            "basis":"Source text mentions are NOT automatically vehicle-year applicability",
            "published_bases_modified":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("AKM7169FRE_ORIGINAL_ENTRIES",results["entries"])
    print("AKM7169FRE_ENTRY_TYPES",json.dumps(results["entry_types"],ensure_ascii=False))
    print("AKM7169FRE_EXPLICIT_YEARS",json.dumps(results["explicit_application_periods"],ensure_ascii=False))
    print("AKM7169FRE_TEXT_YEAR_TOKENS",json.dumps(results["year_tokens_in_source_text"],ensure_ascii=False))
    print("AKM7169FRE_YEAR_SCOPE_KEYS",json.dumps(results["year_scope_fields"],ensure_ascii=False))
    print("AKM7169FRE_MEMS_MENTIONS",json.dumps(results["mems_version_mentions"],ensure_ascii=False))
    print("AKM7169FRE_VIN_REFERENCES",json.dumps(results["vin_references"],ensure_ascii=False))
    print("AKM7169FRE_ECU_PART_REFERENCES",json.dumps(results["ecu_part_references"],ensure_ascii=False))
    print("AKM7169FRE_EXACT_ECU_FITMENT_MATCHES",fits["ecu_parts_exactly_matched"])
    print("AKM7169FRE_PAGES_WITH_YEAR_EVIDENCE",
        [p for p,s in results["pages"].items() if s["explicit_years"] or s["year_mention"]])
    print("ORIGINAL_FRENCH_PACK_UNCHANGED_NO_ENGLISH_NO_SETUP_NO_RELEASE")

if __name__=="__main__":
    main()
