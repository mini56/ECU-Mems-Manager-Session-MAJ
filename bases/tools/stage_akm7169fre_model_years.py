#!/usr/bin/env python3
"""Add original AKM7169FRE's verified VIN start to a TEMPORARY SQLite copy.

The manufacturer's French Mini manual is valid from VIN 049349, whose
production-series start is 1992. This is "92+" (1992 included), not
"post 92" (strictly after 1992). Motorization is SPi; no ECU end year
is inferred. No original / published database or document is altered.
"""
from pathlib import Path
import hashlib
import json
import sqlite3

DOC="AKM7169FRE"
REVISION="MEMS-SPI-20P-ORIGINAL-FR-1993"
SHA256="37cd0434347fe4009963d075e4b91b0b21ebc905bae5657519a8080c3026d4f5"
PERIOD="92+"
VIN="049349"
ENTRIES=429
BASIS="manufacturer_manual_vin_start"
SCOPE="AKM7169FRE-SPi-VIN049349"


def add_akm7169fre_period(original_path, staging_path, metadata_path):
    original_path=Path(original_path)
    staging_path=Path(staging_path)
    metadata_path=Path(metadata_path)
    if original_path.resolve()==staging_path.resolve():
        raise ValueError("STAGING_MUST_NOT_MODIFY_SOURCE")
    if not original_path.is_file() or not staging_path.is_file():
        raise ValueError("MISSING_SOURCE_OR_TEMPORARY_DATABASE")
    record=json.loads(metadata_path.read_text(encoding="utf-8"))
    scope=record.get("applicability",{})
    if (record.get("document_id")!=DOC or
        record.get("source_revision")!=REVISION or
        record.get("source_sha256")!=SHA256 or
        record.get("indexed_entries")!=ENTRIES or
        record.get("original_chapter_pages")!=20 or
        scope.get("model_year_from")!=1992 or
        scope.get("model_year_to") is not None or
        scope.get("vin_from")!=VIN or
        scope.get("period_display")!=PERIOD or
        scope.get("provenance_kind")!=BASIS or
        scope.get("application_level")!="manual_edition_general_scope"):
        raise ValueError("AKM7169FRE_DOCUMENTARY_EVIDENCE_NOT_VERIFIED")

    original_digest=hashlib.sha256(original_path.read_bytes()).hexdigest()
    uri="file:"+str(original_path.resolve())+"?mode=ro"
    with sqlite3.connect(uri,uri=True) as original:
        if original.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("SOURCE_SQLITE_INTEGRITY_FAILED")
        identity=original.execute(
            "SELECT source_sha256,source_pages FROM documentary_documents "
            "WHERE document_id=? AND source_revision=?",
            (DOC,REVISION)).fetchone()
        if identity!=(SHA256,20):
            raise ValueError("ORIGINAL_AKM7169FRE_DOCUMENT_IDENTITY_CHANGED")
        original_keys=original.execute(
            "SELECT entry_id FROM documentary_entries "
            "WHERE document_id=? AND source_revision=?",(DOC,REVISION)
        ).fetchall()
        if len(original_keys)!=ENTRIES or len({row[0] for row in original_keys})!=ENTRIES:
            raise ValueError("ORIGINAL_AKM7169FRE_429_ENTRIES_NOT_FOUND")

    with sqlite3.connect(staging_path) as db:
        db.execute("PRAGMA foreign_keys=ON")
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("STAGING_SQLITE_INTEGRITY_FAILED")
        table=db.execute(
            "SELECT sql FROM sqlite_master "
            "WHERE type='table' AND name='documentary_model_years'"
        ).fetchone()
        if (not table or
            "manufacturer_manual_vin_start" not in table[0]):
            raise ValueError("ADDITIVE_YEAR_TABLE_NOT_READY")
        existing=db.execute(
            "SELECT COUNT(*) FROM documentary_model_years WHERE document_id=?",
            (DOC,)).fetchone()[0]
        if existing:
            raise ValueError("ORIGINAL_AKM7169FRE_ALREADY_HAS_YEAR_MAPPING")
        staging_keys=db.execute(
            "SELECT entry_id FROM documentary_entries "
            "WHERE document_id=? AND source_revision=?", (DOC,REVISION)
        ).fetchall()
        if set(staging_keys)!=set(original_keys):
            raise ValueError("STAGING_AKM7169FRE_ENTRIES_DIFFER")
        source_count=db.execute(
            "SELECT COUNT(*) FROM documentary_model_years WHERE document_id='RCL0193FRE'"
        ).fetchone()[0]
        if source_count!=5694:
            raise ValueError("PREVIOUSLY_VERIFIED_RCL0193FRE_YEARS_CHANGED")
        for (entry_id,) in staging_keys:
            db.execute(
                "INSERT INTO documentary_model_years "
                "(document_id,source_revision,entry_id,vehicle_years,"
                "evidence_basis,vin_from,scope_key) VALUES (?,?,?,?,?,?,?)",
                (DOC,REVISION,entry_id,PERIOD,BASIS,VIN,SCOPE)
            )
        db.commit()
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute(
            "PRAGMA foreign_key_check").fetchall():
            raise ValueError("STAGING_AKM7169FRE_SQLITE_INTEGRITY_FAILED")
        current=db.execute(
            "SELECT vehicle_years,evidence_basis,vin_from,COUNT(*) "
            "FROM documentary_model_years WHERE document_id=? "
            "GROUP BY vehicle_years,evidence_basis,vin_from",(DOC,)
        ).fetchall()
        if current!=[(PERIOD,BASIS,VIN,ENTRIES)]:
            raise ValueError("AKM7169FRE_STAGED_PERIOD_COUNT_INCORRECT")
        if db.execute(
            "SELECT COUNT(*) FROM documentary_model_years WHERE document_id='RCL0193FRE'"
        ).fetchone()[0]!=5694:
            raise ValueError("EXISTING_RCL0193FRE_PERIODS_MODIFIED")
    if hashlib.sha256(original_path.read_bytes()).hexdigest()!=original_digest:
        raise ValueError("ORIGINAL_SQLITE_MODIFIED")
    return ENTRIES
