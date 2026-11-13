#!/usr/bin/env python3
"""Validate a versioned encrypted documentary snapshot before enabling MAJ.

There is deliberately NO fixed list of source manuals, page counts, dates or
asset hashes. Every publication is a NEW encrypted full snapshot per language.
A new document is accepted only after SQLite provenance, page coverage, image
integrity, source checks and explicit redistribution rights are verified.

This command never uploads copyrighted files or publishes a release.
"""
from __future__ import annotations

import argparse
from contextlib import closing
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

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

REPO = "mini56/ECU-Mems-Manager-Session-MAJ"
LANGUAGES = ("fr", "en", "pt", "es", "it", "de")
ASSET_RE = re.compile(r"^MEMS-DOC-(FR|EN|PT|ES|IT|DE)-[A-Za-z0-9._-]+\.encrypted$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
TAG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,43}$")
VERSION_RE = re.compile(r"^[A-Za-z0-9._-]{1,50}$")
IMAGE_RE = re.compile(r"^images/[A-Za-z0-9._/-]+\.(?:png|jpg|jpeg|webp|svg)$", re.I)
MAX_ZIP = 256 * 1024 * 1024
MAX_FILES = 1000
MAX_EXPANDED = 700 * 1024 * 1024


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


def safe_hash(value: object) -> bool:
    return isinstance(value, str) and SHA_RE.fullmatch(value) is not None


def table_exists(db: sqlite3.Connection, name: str) -> bool:
    return db.execute(
        "SELECT 1 FROM sqlite_master WHERE name=? AND type IN ('table','view')",
        (name,)).fetchone() is not None


def validate_native(db: sqlite3.Connection, language: str, archive: zipfile.ZipFile,
                    names: set[str]) -> list[dict]:
    """Common multi-document schema used by French and future native languages."""
    required = ("documentary_database", "documentary_documents",
                "documentary_pages", "documentary_entries",
                "documentary_images", "documentary_fts")
    require(all(table_exists(db, t) for t in required), "NATIVE_SCHEMA_MISSING")
    status = db.execute(
        "SELECT schema_version,language,publication_status "
        "FROM documentary_database WHERE singleton=1").fetchall()
    require(len(status) == 1 and status[0][0] == 1 and
            status[0][1] == language and
            status[0][2] in ("source_inventory", "validated"),
            "NATIVE_LANGUAGE_OR_STATUS_INVALID")
    rows = db.execute(
        "SELECT document_id,source_revision,language,edition_code,"
        "source_sha256,source_pages,publisher "
        "FROM documentary_documents ORDER BY document_id,source_revision").fetchall()
    require(len(rows) > 0, "NO_DOCUMENTS")
    documents: list[dict] = []
    for doc_id, revision, doc_lang, edition, sha, page_count, publisher in rows:
        require(all(isinstance(x, str) and x.strip() for x in
                    (doc_id, revision, edition, publisher)) and
                doc_lang == language and safe_hash(sha) and
                isinstance(page_count, int) and 1 <= page_count <= 50000,
                "DOCUMENT_PROVENANCE_INVALID")
        pages = db.execute(
            "SELECT COUNT(*),COUNT(DISTINCT physical_page),"
            "MIN(physical_page),MAX(physical_page) FROM documentary_pages "
            "WHERE document_id=? AND source_revision=?",
            (doc_id, revision)).fetchone()
        require(pages == (page_count, page_count, 1, page_count),
                "DOCUMENT_PAGES_INCOMPLETE")
        documents.append({
            "document_id": doc_id, "source_revision": revision,
            "edition": edition, "source_sha256": sha,
            "source_pages": page_count
        })
    totals = db.execute(
        "SELECT (SELECT COUNT(*) FROM documentary_pages),"
        "(SELECT COUNT(*) FROM documentary_entries),"
        "(SELECT COUNT(*) FROM documentary_fts),"
        "(SELECT COUNT(*) FROM documentary_images)").fetchone()
    require(totals[0] == sum(d["source_pages"] for d in documents) and
            totals[1] > 0 and totals[1] == totals[2],
            "INDEX_OR_PAGE_COUNTS_INVALID")
    require(db.execute(
        "SELECT COUNT(*) FROM documentary_entries "
        "WHERE verification_status!='source_checked'").fetchone()[0] == 0,
        "DOCUMENT_ROWS_NOT_SOURCE_CHECKED")
    require(db.execute(
        "SELECT COUNT(*) FROM documentary_entries e "
        "WHERE e.source_page IS NOT NULL AND NOT EXISTS "
        "(SELECT 1 FROM documentary_pages p "
        "WHERE p.document_id=e.document_id "
        "AND p.source_revision=e.source_revision "
        "AND p.physical_page=e.source_page)").fetchone()[0] == 0,
        "ENTRY_REFERENCES_UNKNOWN_PAGE")
    # A documentary snapshot may contain no images; every referenced image
    # must be present and its exact bytes checked.
    image_names: set[str] = set()
    for relative, expected, size in db.execute(
            "SELECT relative_path,asset_sha256,asset_bytes "
            "FROM documentary_images"):
        require(isinstance(relative, str) and
                IMAGE_RE.fullmatch(relative) is not None and
                ".." not in relative.split("/") and
                relative in names and relative not in image_names and
                safe_hash(expected) and isinstance(size, int) and
                0 < size <= 15 * 1024 * 1024,
                "DOCUMENT_IMAGE_PATH_OR_METADATA_INVALID")
        require(archive.getinfo(relative).file_size == size and
                hashlib.sha256(archive.read(relative)).hexdigest() == expected,
                "DOCUMENT_IMAGE_HASH_INVALID")
        image_names.add(relative)
    require(names == image_names | {f"mems_documentary_{language}.sqlite"},
            "UNDECLARED_FILES_IN_PACK")
    return documents


def validate_legacy_english(db: sqlite3.Connection) -> list[dict]:
    """Existing AKM7169ENG format: preserve and validate, without pinning 482p."""
    require(all(table_exists(db, table) for table in
                ("source_documents", "source_page_discovery",
                 "procedures", "procedure_steps", "technical_values",
                 "illustrations")), "LEGACY_ENGLISH_SCHEMA_MISSING")
    docs = db.execute(
        "SELECT document_id,total_pages,original_pdf_sha256 "
        "FROM source_documents ORDER BY document_id").fetchall()
    require(len(docs) > 0, "ENGLISH_NO_DOCUMENTS")
    published = []
    for doc_id, pages, sha in docs:
        require(isinstance(doc_id, str) and doc_id and
                isinstance(pages, int) and 1 <= pages <= 50000 and
                safe_hash(sha), "ENGLISH_DOCUMENT_PROVENANCE_INVALID")
        coverage = db.execute(
            "SELECT COUNT(DISTINCT physical_page),MIN(physical_page),"
            "MAX(physical_page) FROM source_page_discovery WHERE document_id=?",
            (doc_id,)).fetchone()
        require(coverage == (pages, 1, pages),
                "ENGLISH_PAGES_INCOMPLETE")
        published.append({
            "document_id": doc_id, "edition": doc_id,
            "source_pages": pages, "source_sha256": sha
        })
    require(db.execute("SELECT COUNT(*) FROM procedures").fetchone()[0] > 0 and
            db.execute("SELECT COUNT(*) FROM procedure_steps").fetchone()[0] > 0,
            "ENGLISH_PROCEDURES_MISSING")
    return published


def validate_zip(plaintext: bytes, language: str) -> list[dict]:
    require(0 < len(plaintext) <= MAX_ZIP, "ZIP_SIZE_INVALID")
    with zipfile.ZipFile(io.BytesIO(plaintext)) as archive:
        items = [entry for entry in archive.infolist() if not entry.is_dir()]
        names = [item.filename for item in items]
        require(0 < len(names) <= MAX_FILES and len(set(names)) == len(names),
                "DUPLICATE_OR_TOO_MANY_FILES")
        require(sum(item.file_size for item in items) <= MAX_EXPANDED,
                "ZIP_EXPANSION_LIMIT")
        for item in items:
            path = item.filename
            require(not path.startswith("/") and "\\" not in path and
                    all(segment not in ("", ".", "..") for segment in path.split("/")) and
                    ((item.external_attr >> 16) & 0o170000) != 0o120000,
                    "ZIP_UNSAFE_PATH")
        sqlite_name = f"mems_documentary_{language}.sqlite"
        require(sqlite_name in names, "SQLITE_FOR_LANGUAGE_NOT_FOUND")
        require(archive.testzip() is None, "ZIP_CRC_FAILED")
        with tempfile.TemporaryDirectory() as tmp:
            dbpath = Path(tmp) / sqlite_name
            dbpath.write_bytes(archive.read(sqlite_name))
            with closing(sqlite3.connect(f"file:{dbpath}?mode=ro", uri=True)) as db:
                require(db.execute("PRAGMA integrity_check").fetchone()[0] == "ok",
                        "SQLITE_CORRUPT")
                require(not db.execute("PRAGMA foreign_key_check").fetchall(),
                        "SQLITE_FOREIGN_KEYS_INVALID")
                if table_exists(db, "documentary_database"):
                    return validate_native(db, language, archive, set(names))
                require(language == "en" and names == [sqlite_name],
                        "UNKNOWN_LANGUAGE_SCHEMA_OR_EXTRA_FILES")
                return validate_legacy_english(db)


def validate_encrypted(asset: Path, language: str, password: str) -> tuple[str, list[dict]]:
    require(asset.is_file() and 61 < asset.stat().st_size < MAX_ZIP + 61,
            "ENCRYPTED_ASSET_MISSING_OR_OVERSIZED")
    data = asset.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    require(data[:8] == b"MEMSDOC1" and data[8] == 1,
            "ENCRYPTED_FORMAT_INVALID")
    plain_length = struct.unpack_from("<Q", data, 37)[0]
    require(0 < plain_length <= MAX_ZIP and
            len(data) == plain_length + 61, "ENCRYPTED_SIZE_INVALID")
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), data[9:25], 210000, 32)
    try:
        plaintext = AESGCM(key).decrypt(data[25:37], data[45:], data[:45])
    except InvalidTag as error:
        raise RuntimeError("WRONG_PUBLISHER_PASSWORD_OR_TAMPERED_PACK") from error
    require(len(plaintext) == plain_length, "PLAINTEXT_LENGTH_INVALID")
    return sha, validate_zip(plaintext, language)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--asset-dir", required=True, type=Path)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--language", choices=("fr", "en", "pt", "es", "it", "de", "both"),
                        default="both")
    parser.add_argument("--rights-confirmed", action="store_true")
    parser.add_argument("--rights-reference", required=True)
    args = parser.parse_args()
    require(args.rights_confirmed and len(args.rights_reference.strip()) >= 8,
            "WRITTEN_DISTRIBUTION_RIGHTS_REQUIRED")
    require(TAG_RE.fullmatch(args.tag) is not None, "UNSAFE_RELEASE_TAG")
    secret = os.environ.get("MEMS_DOCUMENTARY_PUBLISH_PASSWORD", "")
    require(len(secret) >= 12, "PUBLISHER_SECRET_MISSING")
    selected = ("fr", "en") if args.language == "both" else (args.language,)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    require(manifest.get("schema_version") == 2 and
            manifest.get("application") == "ECU MEMS Manager SESSION" and
            manifest.get("documentary_schema") == "mems-documentary-multisource-v1",
            "MANIFEST_SCHEMA_INVALID")

    # All selected languages must pass before touching manifest.json.
    changes = {}
    for language in selected:
        candidates = [p for p in args.asset_dir.iterdir() if
                      p.is_file() and ASSET_RE.fullmatch(p.name) and
                      p.name.startswith(f"MEMS-DOC-{language.upper()}-")]
        require(len(candidates) == 1, "ONE_ENCRYPTED_SNAPSHOT_REQUIRED_PER_LANGUAGE")
        asset = candidates[0]
        hash_value, documents = validate_encrypted(asset, language, secret)
        entry = manifest["documentary_bases"].get(language)
        require(isinstance(entry, dict) and
                entry.get("database_file") == f"mems_documentary_{language}.sqlite",
                "MANIFEST_TARGET_NOT_SUPPORTED")
        # Incremental documentary updates are full snapshots. They must
        # preserve existing document IDs and revisions, never silently erase
        # previously published manuals.
        old_docs = entry.get("published_documents") or []
        old_ids = {d.get("document_id") for d in old_docs}
        new_ids = {d["document_id"] for d in documents}
        require(old_ids.issubset(new_ids), "PREVIOUS_DOCUMENT_MISSING_FROM_UPDATE")
        version = f"{language}-{args.tag}"
        require(VERSION_RE.fullmatch(version) is not None and
                version != entry.get("version"), "VERSION_MUST_CHANGE")
        changes[language] = {
            "available": True,
            "version": version,
            "release_url": f"https://github.com/{REPO}/releases/download/{args.tag}/{asset.name}",
            "sha256": hash_value,
            "document_count": len(documents),
            "published_documents": documents,
            "installation_password_required": True,
            "encrypted_package_required": True
        }
        print(f"VALIDATED_{language.upper()}_{len(documents)}_DOCUMENTS")
    for language, change in changes.items():
        manifest["documentary_bases"][language].update(change)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("NEW_DOCUMENTARY_SNAPSHOTS_ENABLED_AFTER_VERIFICATION")


if __name__ == "__main__":
    main()
