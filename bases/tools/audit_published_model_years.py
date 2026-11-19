#!/usr/bin/env python3
"""Read-only audit of real authenticated SESSION documentary SQLite packs.

No source texts, images, decrypted files, passwords, or entire databases are
included in the report. A date found in prose is not proof of model-year scope.
"""
import argparse
import collections
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import struct
import tempfile
import zipfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

YEAR_RANGE = re.compile(r"(?<!\d)((?:19[89]|20[0-2])\d)\s*[-–—/àto]+\s*((?:19[89]|20[0-2])\d)(?!\d)", re.I)
SHORT_RANGE = re.compile(r"(?<!\d)([89]\d|0\d)\s*[-–—/]\s*([89]\d|0\d)(?!\d)")
OPEN_YEAR = re.compile(r"(?<!\d)((?:19[89]|20[0-2])\d)\s*(?:->|→|et après|et suivantes)", re.I)
KEY_YEAR = re.compile(r"year|ann[eé]e|mill[eé]sime|model.?years?|production.?years?", re.I)
KEY_SCOPE = re.compile(r"applicab|vehicle|v[eé]hicule|mod[eè]le|model|scope|variant|g[eé]n[eé]ration|p[eé]riode", re.I)
BRAKE = re.compile(r"frein|brake", re.I)


def has_table(db, name):
    return db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None


def columns(db, name):
    return [item[1] for item in db.execute("PRAGMA table_info('" + name + "')")]


def year_value(value):
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip()
    if not text.isdigit():
        return None
    number = int(text)
    if 1980 <= number <= 2035:
        return number
    if len(text) == 2 and (80 <= number <= 99 or 0 <= number <= 35):
        return 1900 + number if number >= 80 else 2000 + number
    return None


def periods_from_record(record):
    """Only fields explicitly about vehicle years/applicability can make a claim."""
    found = set()
    if not isinstance(record, dict):
        return found
    lowered = {str(k).casefold(): v for k, v in record.items()}
    beginnings = ("year_from", "year_start", "model_year_from", "start_year", "annee_debut")
    endings = ("year_to", "year_end", "model_year_to", "end_year", "annee_fin")
    start = next((year_value(lowered[k]) for k in beginnings if k in lowered and year_value(lowered[k]) is not None), None)
    end = next((year_value(lowered[k]) for k in endings if k in lowered and year_value(lowered[k]) is not None), None)
    if start is not None and end is not None and start <= end:
        found.add(f"{start % 100:02d}-{end % 100:02d}")
    elif start is not None and end is None:
        found.add(f"{start % 100:02d}+")
    for key, value in lowered.items():
        if not (KEY_YEAR.search(key) or KEY_SCOPE.search(key)):
            continue
        values = value if isinstance(value, list) else [value]
        for candidate in values:
            if isinstance(candidate, dict):
                found.update(periods_from_record(candidate))
                continue
            if not isinstance(candidate, (str, int)):
                continue
            text = str(candidate)
            for a, b in YEAR_RANGE.findall(text):
                if int(a) <= int(b):
                    found.add(f"{int(a) % 100:02d}-{int(b) % 100:02d}")
            for a, b in SHORT_RANGE.findall(text):
                found.add(a + "-" + b)
            for a in OPEN_YEAR.findall(text):
                found.add(f"{int(a) % 100:02d}+")
            if KEY_YEAR.search(key) and not found:
                year = year_value(candidate)
                if year is not None:
                    found.add(f"{year % 100:02d}")
    return found


def text_date_mentions(text):
    """Possible year-range mentions in prose: NOT attributed to vehicles."""
    return {f"{int(a)%100:02d}-{int(b)%100:02d}"
            for a, b in YEAR_RANGE.findall(text or "") if int(a) <= int(b)}


def decrypt_pack(path, expected_hash, password):
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_hash:
        raise ValueError("PUBLISHED_PACK_SHA256_MISMATCH: " + path.name)
    if len(payload) <= 61 or payload[:8] != b"MEMSDOC1" or payload[8] != 1:
        raise ValueError("PUBLISHED_PACK_ENCRYPTION_FORMAT_INVALID: " + path.name)
    length = struct.unpack_from("<Q", payload, 37)[0]
    if length <= 0 or len(payload) != length + 61:
        raise ValueError("PUBLISHED_PACK_LENGTH_INVALID: " + path.name)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), payload[9:25], 210000, 32)
    clear = AESGCM(key).decrypt(payload[25:37], payload[45:], payload[:45])
    if len(clear) != length:
        raise ValueError("PUBLISHED_PACK_DECRYPTED_LENGTH_INVALID: " + path.name)
    return clear


def summarize_db(db, label, language):
    db.row_factory = sqlite3.Row
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise ValueError("SQLITE_INTEGRITY_FAILED_" + label)
    info = {"pack": label, "language": language, "documents": [],
            "entry_count": 0, "entries_explicit_years": 0,
            "entry_brake_count": 0, "brake_entries_explicit_years": 0,
            "entries_year_mentions_without_explicit_field": 0,
            "source_rows": 0, "source_rows_explicit_years": 0,
            "source_scope_rows": 0, "source_scope_rows_explicit_years": 0,
            "periods_in_entry_metadata": {}, "periods_in_source_metadata": {},
            "metadata_year_keys": [], "metadata_period_examples": []}
    docs = collections.defaultdict(lambda: {
        "entries": 0, "entries_explicit_years": 0, "brake_entries": 0,
        "brake_entries_explicit_years": 0, "periods": collections.Counter()})
    if has_table(db, "documentary_documents"):
        for row in db.execute("SELECT * FROM documentary_documents"):
            d = dict(row)
            doc_id = str(d.get("document_id", ""))
            identified = periods_from_record(d)
            docs[doc_id]["document_metadata_periods"] = sorted(identified)
            docs[doc_id]["edition"] = str(d.get("edition_code") or "")
            docs[doc_id]["pages"] = d.get("source_pages")
        info["document_count"] = len(docs)
    else:
        raise ValueError("PUBLISHED_PACK_NOT_NATIVE_SQLITE_" + label)
    if not has_table(db, "documentary_entries"):
        raise ValueError("MISSING_DOCUMENTARY_ENTRIES_" + label)
    entry_cols = set(columns(db, "documentary_entries"))
    required = {"document_id", "title", "source_text"}
    if not required.issubset(entry_cols):
        raise ValueError("MISSING_ENTRY_PROVENANCE_" + label)
    fields = ["document_id", "title", "source_text"]
    if "raw_json" in entry_cols:
        fields.append("raw_json")
    for row in db.execute("SELECT " + ",".join(fields) + " FROM documentary_entries"):
        record = dict(row)
        docid = record["document_id"]
        doc = docs[docid]
        info["entry_count"] += 1
        doc["entries"] += 1
        raw = record.get("raw_json") or ""
        try:
            raw_obj = json.loads(raw) if raw else {}
        except (json.JSONDecodeError, TypeError):
            raw_obj = {}
        identified = periods_from_record(raw_obj)
        if identified:
            info["entries_explicit_years"] += 1
            doc["entries_explicit_years"] += 1
            doc["periods"].update(identified)
        elif text_date_mentions(record["source_text"]):
            info["entries_year_mentions_without_explicit_field"] += 1
        is_brake = bool(BRAKE.search((record["title"] or "") + " " + (record["source_text"] or "")))
        if is_brake:
            info["entry_brake_count"] += 1
            doc["brake_entries"] += 1
            if identified:
                info["brake_entries_explicit_years"] += 1
                doc["brake_entries_explicit_years"] += 1
    source_counts = collections.Counter()
    keys_seen = set()
    if has_table(db, "documentary_source_rows"):
        for name, raw_json in db.execute("SELECT table_name,row_json FROM documentary_source_rows"):
            info["source_rows"] += 1
            try:
                data = json.loads(raw_json)
            except (TypeError, json.JSONDecodeError):
                continue
            if not isinstance(data, dict):
                continue
            for key in data:
                if KEY_YEAR.search(key) or KEY_SCOPE.search(key):
                    keys_seen.add(str(key))
            periods = periods_from_record(data)
            if "scope" in str(name).lower():
                info["source_scope_rows"] += 1
                if periods:
                    info["source_scope_rows_explicit_years"] += 1
            if periods:
                info["source_rows_explicit_years"] += 1
                source_counts.update(periods)
    for doc_id, value in sorted(docs.items()):
        if not doc_id:
            continue
        info["documents"].append({
            "document_id": doc_id, "edition": value.get("edition", ""),
            "pages": value.get("pages"), "entries": value["entries"],
            "entries_explicit_years": value["entries_explicit_years"],
            "brake_entries": value["brake_entries"],
            "brake_entries_explicit_years": value["brake_entries_explicit_years"],
            "document_metadata_periods": value.get("document_metadata_periods", []),
            "entry_periods": dict(value["periods"].most_common(12))})
    info["periods_in_entry_metadata"] = dict(collections.Counter(
        p for item in docs.values() for p, n in item["periods"].items() for _ in range(n)).most_common(25))
    info["periods_in_source_metadata"] = dict(source_counts.most_common(25))
    info["metadata_year_keys"] = sorted(keys_seen)[:45]
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--directory", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    password = os.environ.get("MEMS_DOCUMENTARY_PUBLISH_PASSWORD", "")
    if len(password) < 12:
        raise SystemExit("MAJ_AUDIT_SECRET_UNAVAILABLE")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    catalog = manifest["documentary_bases"]
    packs = [("FR-12-AKM", "fr", catalog["fr"]),
             ("FR-6-RAVE", "fr", catalog["fr"]["previous_packs"][0]),
             ("EN-48-RAVE", "en", catalog["en"])]
    report = {"audit": "MAJ real SQLite model-year evidence; no data modification",
              "edition_applicability": "only explicit per-entry metadata is strong evidence",
              "packs": []}
    for label, language, desc in packs:
        filename = desc["release_url"].rsplit("/", 1)[-1]
        path = args.directory / filename
        if not path.is_file():
            raise SystemExit("MISSING_PUBLISHED_PACK_" + label)
        clear = decrypt_pack(path, desc["sha256"], password)
        with zipfile.ZipFile(io.BytesIO(clear)) as archive:
            sqlite_name = "mems_documentary_" + language + ".sqlite"
            if sqlite_name not in archive.namelist() or archive.testzip() is not None:
                raise ValueError("PUBLISHED_PACK_ZIP_INTEGRITY_INVALID_" + label)
            with tempfile.TemporaryDirectory(prefix="year-audit-") as temp:
                target = Path(temp) / sqlite_name
                target.write_bytes(archive.read(sqlite_name))
                with sqlite3.connect("file:" + str(target) + "?mode=ro", uri=True) as db:
                    info = summarize_db(db, label, language)
        del clear
        if info["document_count"] != desc["document_count"]:
            raise ValueError("DOCUMENT_COUNT_MISMATCH_" + label)
        report["packs"].append(info)
        print("AUDIT_PACK", label, "documents", info["document_count"],
              "entries", info["entry_count"],
              "with_explicit_years", info["entries_explicit_years"],
              "brake_entries", info["entry_brake_count"],
              "brake_with_explicit_years", info["brake_entries_explicit_years"],
              "source_rows_with_years", info["source_rows_explicit_years"])
        print("AUDIT_YEAR_FIELDS", label, ",".join(info["metadata_year_keys"][:24]) or "none")
        print("AUDIT_PERIODS_FROM_SOURCE", label, json.dumps(info["periods_in_source_metadata"], ensure_ascii=False))
        print("AUDIT_PERIODS_FROM_ENTRIES", label, json.dumps(info["periods_in_entry_metadata"], ensure_ascii=False))
        for d in info["documents"]:
            if d["entries_explicit_years"] or d["document_metadata_periods"]:
                print("AUDIT_DOC_WITH_YEAR", label, d["document_id"],
                      d["entries_explicit_years"], d["document_metadata_periods"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("AUDIT_COMPLETE_3_REAL_ENCRYPTED_PACKS_NO_PUBLICATION_NO_SETUP")


if __name__ == "__main__":
    main()
