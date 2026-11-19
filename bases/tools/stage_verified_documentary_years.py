#!/usr/bin/env python3
"""Create a staging copy of native SESSION SQLite with verified vehicle years.

Never changes a source database, published pack, title, AI text, image, or
existing documentary table. The added table is optional in schema v1.
Only exact VIN/ECU evidence from the authenticated audit is accepted;
review candidates are excluded.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sqlite3

PERIOD = re.compile(r"(?:[0-9]{2}-[0-9]{2}|[0-9]{2}\+|pré [0-9]{2}|post [0-9]{2})\Z", re.I)
REQUIRED = {"documentary_database", "documentary_documents",
            "documentary_entries", "documentary_pages", "documentary_fts"}
ADDITIVE = "documentary_model_years"

def integrity(db):
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise ValueError("SQLITE_INTEGRITY_FAILED")
    if db.execute("PRAGMA foreign_key_check").fetchall():
        raise ValueError("SQLITE_FOREIGN_KEYS_FAILED")

def table_names(db):
    return {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}

def stage(source, report_file, output):
    if source.resolve() == output.resolve():
        raise ValueError("SOURCE_AND_OUTPUT_MUST_DIFFER")
    if output.exists():
        raise ValueError("STAGING_DESTINATION_ALREADY_EXISTS")
    evidence = json.loads(report_file.read_text(encoding="utf-8"))
    if evidence.get("reference", {}).get("vin_134455_years") != "96+":
        raise ValueError("REFERENCE_VIN_134455_AUDIT_MISMATCH")
    verified = evidence.get("verified_entry_mappings")
    if not isinstance(verified, list) or not verified:
        raise ValueError("NO_VERIFIED_PERIOD_MAPPING")
    if any(r.get("model_years") != "96+" for r in verified):
        # Additional years need independent source review before acceptance.
        raise ValueError("UNREVIEWED_MODEL_YEAR_PERIOD")
    if any(r.get("basis") != "exact_ecu_fitment_vin" for r in verified):
        raise ValueError("UNVERIFIED_YEAR_MAPPING_BASIS")
    for entry in verified:
        if not PERIOD.fullmatch(str(entry.get("model_years", ""))):
            raise ValueError("MALFORMED_YEAR_VALUE")
        allowed_scopes = {"SCOPE-RCL0193FRE-MINI-VIN134455",
                          "SCOPE-RCL0193FRE-MPI-VIN134455"}
        if (len(entry.get("scope_keys", [])) != 1 or
                entry["scope_keys"][0] not in allowed_scopes):
            raise ValueError("UNVERIFIED_SOURCE_SCOPE")

    with sqlite3.connect("file:" + str(source.resolve()) + "?mode=ro", uri=True) as original:
        integrity(original)
        tables = table_names(original)
        if not REQUIRED.issubset(tables) or ADDITIVE in tables:
            raise ValueError("SOURCE_SCHEMA_UNEXPECTED")
        language = original.execute(
            "SELECT language FROM documentary_database WHERE singleton=1").fetchone()
        if not language or language[0] != "fr":
            raise ValueError("SOURCE_MUST_BE_FRENCH")
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with sqlite3.connect(output) as staging:
                original.backup(staging)
                staging.execute("PRAGMA foreign_keys=ON")
                staging.executescript("""
                    CREATE TABLE documentary_model_years(
                      document_id TEXT NOT NULL,
                      source_revision TEXT NOT NULL,
                      entry_id TEXT NOT NULL,
                      vehicle_years TEXT NOT NULL,
                      evidence_basis TEXT NOT NULL
                        CHECK(evidence_basis IN (
                          'exact_ecu_fitment_vin','manufacturer_manual_vin_start')),
                      vin_from TEXT NOT NULL,
                      scope_key TEXT NOT NULL,
                      PRIMARY KEY(document_id,source_revision,entry_id),
                      FOREIGN KEY(document_id,source_revision,entry_id)
                        REFERENCES documentary_entries(
                          document_id,source_revision,entry_id)
                    );
                    CREATE INDEX idx_documentary_years_period
                        ON documentary_model_years(vehicle_years);
                """)
                q = staging.cursor()
                added = Counter()
                seen = set()
                for row in verified:
                    key=(row["document_id"],row["source_revision"],row["entry_id"])
                    if key in seen:
                        raise ValueError("DUPLICATE_SOURCE_ENTRY_MAPPING")
                    seen.add(key)
                    found=q.execute(
                        "SELECT 1 FROM documentary_entries "
                        "WHERE document_id=? AND source_revision=? AND entry_id=?",
                        key).fetchone()
                    if not found:
                        raise ValueError("ENTRY_NOT_IN_STAGING_SOURCE_" + str(key))
                    q.execute(
                        "INSERT INTO documentary_model_years VALUES (?,?,?,?,?,?,?)",
                        (*key,row["model_years"],row["basis"],"134455",
                         row["scope_keys"][0]))
                    added[row["document_id"]] += 1
                staging.commit()
                integrity(staging)
                if sum(added.values()) != len(verified):
                    raise ValueError("INCOMPLETE_APPLICABILITY_STAGING")
                if table_names(staging) - table_names(original) != {ADDITIVE}:
                    raise ValueError("UNEXPECTED_ADDITIVE_SCHEMA")
                for table in REQUIRED - {"documentary_fts"}:
                    source_count=original.execute(
                        'SELECT COUNT(*) FROM "' + table + '"').fetchone()[0]
                    staged_count=staging.execute(
                        'SELECT COUNT(*) FROM "' + table + '"').fetchone()[0]
                    if source_count != staged_count:
                        raise ValueError("EXISTING_DATA_COUNT_CHANGED_" + table)
            return dict(added)
        except BaseException:
            output.unlink(missing_ok=True)
            raise

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--evidence",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    added=stage(args.source,args.evidence,args.output)
    print("STAGING_YEAR_METADATA_ONLY",json.dumps(added,ensure_ascii=False))
    print("SOURCE_UNCHANGED_NO_PACK_NO_RELEASE_NO_SETUP")

if __name__=="__main__":
    main()
