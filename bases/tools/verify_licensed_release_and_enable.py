#!/usr/bin/env python3
"""Verify already-hosted AES-GCM documentary Releases before enabling MAJ.

NEVER run on source files outside an administrator-authorized publication.
The only accepted assets, contents and versions are pinned below.
The publisher's secret is read from a GitHub Actions secret; never printed.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sqlite3
import struct
import tempfile
import zipfile
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

REPO = "mini56/ECU-Mems-Manager-Session-MAJ"
EXPECTED_TAG = "mems-documentary-fr-en-20261113"
EXPECTED = {
    "fr": {
        "name": "MEMS-DOC-FR-RCL0193FRE-AKM7169FRE-SPI-20261113-MAJ.encrypted",
        "sha256": "1686e3f7a8432751695d000897ad6b2412293444444ae983e44d84b083aeda04",
        "size": 28098898,
        "version": "fr-2026.11.13-RCL0193FRE-AKM7169FRE-SPI",
        "doc_count": 2,
        "published_documents": [
            {"document_id": "RCL0193FRE", "edition": "RCL0193FRE",
             "source_pages": 371},
            {"document_id": "AKM7169FRE-SPI", "edition": "AKM7169FRE",
             "source_pages": 20},
        ],
    },
    "en": {
        "name": "MEMS-DOC-EN-AKM7169ENG-20261113-MAJ.encrypted",
        "sha256": "10164258b6f8780d7e2249ef5ffa00cb9784f99cab1991cdb640e7833e9954ab",
        "size": 6731477,
        "version": "en-2026.11.13-AKM7169ENG",
        "doc_count": 1,
        "published_documents": [
            {"document_id": "AKM7169ENG", "edition": "AKM7169ENG",
             "source_pages": 482},
        ],
    },
}
DOC_SHA = {
    "RCL0193FRE": "0c7fef28d0d0f0673ba321d6625a019c005823103caa98afb3258114e1fec713",
    "AKM7169FRE": "37cd0434347fe4009963d075e4b91b0b21ebc905bae5657519a8080c3026d4f5",
    "AKM7169ENG": "c8bbb30d7d5a52932e7f92723ba5dc70520012ac3ceac21d19ab0a39b4d4c4e0",
}
MAX_UNPACKED = 700 * 1024 * 1024
MAX_FILES = 1000


def insist(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_plaintext_zip(plaintext: bytes, language: str) -> None:
    expected_db = f"mems_documentary_{language}.sqlite"
    with zipfile.ZipFile(io.BytesIO(plaintext)) as archive:
        files = [f for f in archive.infolist() if not f.is_dir()]
        names = [f.filename for f in files]
        insist(len(files) <= MAX_FILES and len(names) == len(set(names)),
               "ZIP_DUPLICATE_OR_TOO_MANY_FILES")
        insist(expected_db in names, "ZIP_WRONG_LANGUAGE_SQLITE")
        insist(len(plaintext) < 256 * 1024 * 1024, "ZIP_SIZE_LIMIT")
        insist(sum(f.file_size for f in files) <= MAX_UNPACKED,
               "ZIP_DECOMPRESSION_LIMIT")
        insist(not any(
            f.filename.startswith("/") or "\\" in f.filename or
            any(part in ("", ".", "..") for part in f.filename.split("/")) or
            ((f.external_attr >> 16) & 0o170000) == 0o120000
            for f in files), "ZIP_UNSAFE_PATH")
        insist(archive.testzip() is None, "ZIP_CHECKSUM_FAILED")
        if language == "fr":
            insist(len(files) == 346, "FRENCH_ASSET_FILE_COUNT")
        else:
            insist(names == [expected_db], "ENGLISH_UNEXPECTED_FILES")
        with tempfile.TemporaryDirectory() as temporary:
            sqlite_path = Path(temporary) / expected_db
            sqlite_path.write_bytes(archive.read(expected_db))
            uri = f"file:{sqlite_path.as_posix()}?mode=ro"
            # close() matters on Windows; sqlite3 context manager does not close.
            db = sqlite3.connect(uri, uri=True)
            try:
                insist(db.execute("PRAGMA integrity_check").fetchone()[0] == "ok",
                       "SQLITE_INTEGRITY_FAILED")
                insist(not db.execute("PRAGMA foreign_key_check").fetchall(),
                       "SQLITE_FOREIGN_KEYS_FAILED")
                if language == "fr":
                    rows = db.execute(
                        "SELECT document_id,source_pages,source_sha256 "
                        "FROM documentary_documents ORDER BY document_id"
                    ).fetchall()
                    insist(rows == [
                        ("AKM7169FRE", 20, DOC_SHA["AKM7169FRE"]),
                        ("RCL0193FRE", 371, DOC_SHA["RCL0193FRE"]),
                    ], "FRENCH_DOCUMENT_IDENTITIES_INVALID")
                    counts = db.execute(
                        "SELECT (SELECT COUNT(*) FROM documentary_pages), "
                        "(SELECT COUNT(*) FROM documentary_entries), "
                        "(SELECT COUNT(*) FROM documentary_fts), "
                        "(SELECT COUNT(*) FROM documentary_images)"
                    ).fetchone()
                    insist(counts == (391, 6387, 6387, 345),
                           "FRENCH_PAGE_ENTRY_FTS_IMAGE_COUNTS_FAILED")
                    insist(db.execute(
                        "SELECT COUNT(*) FROM documentary_entries "
                        "WHERE verification_status <> 'source_checked'"
                    ).fetchone()[0] == 0, "UNREVIEWED_FRENCH_ROWS")
                    insist(db.execute(
                        "SELECT COUNT(*) FROM documentary_entries "
                        "WHERE document_id='AKM7169FRE' AND entry_type='step'"
                    ).fetchone()[0] == 267, "SPi_STEPS_INCOMPLETE")
                    insist(db.execute(
                        "SELECT COUNT(*) FROM documentary_entries "
                        "WHERE document_id='AKM7169FRE' "
                        "AND entry_type='technical_value'"
                    ).fetchone()[0] == 22, "SPi_VALUES_INCOMPLETE")
                    insist(db.execute(
                        "SELECT COUNT(*) FROM documentary_entries "
                        "WHERE document_id='AKM7169FRE' "
                        "AND source_table='akm7169fre_description_relie'"
                    ).fetchone()[0] == 19, "SPi_DESCRIPTIONS_INCOMPLETE")
                    insist(db.execute(
                        "SELECT COUNT(*) FROM documentary_page_visual_status "
                        "WHERE document_id='RCL0193FRE' AND is_blank=0"
                    ).fetchone()[0] == 325, "RCL_VISUAL_SOURCE_INCOMPLETE")
                    for path, sha, byte_size in db.execute(
                        "SELECT relative_path,asset_sha256,asset_bytes "
                        "FROM documentary_images"
                    ).fetchall():
                        insist(re.fullmatch(
                            r"images/(?:RCL0193FRE|AKM7169FRE)_PDF_\d{3}\.png",
                            path) is not None, "UNEXPECTED_IMAGE_PATH")
                        insist(path in names and
                               archive.getinfo(path).file_size == byte_size,
                               "MISSING_MANUFACTURER_IMAGE")
                        insist(hashlib.sha256(archive.read(path)).hexdigest() == sha,
                               "MANUFACTURER_IMAGE_SHA_INVALID")
                else:
                    docs = db.execute(
                        "SELECT original_pdf_sha256,total_pages FROM source_documents"
                    ).fetchall()
                    insist(docs == [(DOC_SHA["AKM7169ENG"], 482)],
                           "ENGLISH_MANUFACTURER_PDF_INVALID")
                    counters = db.execute(
                        "SELECT (SELECT COUNT(*) FROM procedures),"
                        "(SELECT COUNT(*) FROM procedure_steps),"
                        "(SELECT COUNT(*) FROM technical_values),"
                        "(SELECT COUNT(*) FROM illustrations)"
                    ).fetchone()
                    insist(counters == (336, 5055, 630, 316),
                           "ENGLISH_CONTENT_COUNTS_INVALID")
            finally:
                db.close()


def decrypt_and_verify(asset: Path, language: str, secret: str) -> None:
    info = EXPECTED[language]
    insist(asset.is_file() and asset.stat().st_size == info["size"],
           "ASSET_MISSING_OR_WRONG_SIZE")
    data = asset.read_bytes()
    insist(hashlib.sha256(data).hexdigest() == info["sha256"],
           "ASSET_SHA256_DOES_NOT_MATCH_VERIFIED_CANDIDATE")
    insist(data[:8] == b"MEMSDOC1" and data[8] == 1,
           "ENCRYPTION_FORMAT_UNSUPPORTED")
    length = struct.unpack_from("<Q", data, 37)[0]
    insist(length > 0 and len(data) == length + 61,
           "ENCRYPTED_HEADER_OR_LENGTH_INVALID")
    salt, nonce = data[9:25], data[25:37]
    key = hashlib.pbkdf2_hmac(
        "sha256", secret.encode("utf-8"), salt, 210000, 32)
    try:
        plaintext = AESGCM(key).decrypt(nonce, data[45:], data[:45])
    except InvalidTag as error:
        raise RuntimeError("ADMIN_SECRET_OR_GCM_AUTHENTICATION_FAILURE") from error
    insist(len(plaintext) == length, "DECRYPTED_ZIP_WRONG_LENGTH")
    validate_plaintext_zip(plaintext, language)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--asset-dir", type=Path, required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--language", choices=("fr", "en", "both"), default="both")
    parser.add_argument("--rights-confirmed", action="store_true")
    parser.add_argument("--rights-reference", required=True)
    args = parser.parse_args()
    insist(args.rights_confirmed and len(args.rights_reference.strip()) >= 8,
           "WRITTEN_MANUFACTURER_REDISTRIBUTION_AUTHORIZATION_REQUIRED")
    insist(args.tag == EXPECTED_TAG, "RELEASE_TAG_DOES_NOT_MATCH_PIN")
    secret = os.environ.get("MEMS_DOCUMENTARY_PUBLISH_PASSWORD", "")
    insist(len(secret) >= 12, "MAJ_OWNER_PASSWORD_SECRET_MISSING")
    selected = ["fr", "en"] if args.language == "both" else [args.language]
    document = json.loads(args.manifest.read_text(encoding="utf-8"))
    insist(document.get("schema_version") == 2 and
           document.get("application") == "ECU MEMS Manager SESSION",
           "MANIFEST_SCHEMA_MISMATCH")
    for language in selected:
        item = EXPECTED[language]
        decrypt_and_verify(args.asset_dir / item["name"], language, secret)
        entry = document["documentary_bases"][language]
        insist(entry["database_file"] == f"mems_documentary_{language}.sqlite",
               "MANIFEST_DATABASE_LANGUAGE_ERROR")
        entry.update({
            "available": True,
            "version": item["version"],
            "release_url": (f"https://github.com/{REPO}/releases/"
                            f"download/{EXPECTED_TAG}/{item['name']}"),
            "sha256": item["sha256"],
            "document_count": item["doc_count"],
            "published_documents": item["published_documents"],
            "installation_password_required": True,
            "encrypted_package_required": True,
        })
        print(f"VERIFIED_PUBLISHABLE_{language.upper()}_MAJ_PACKAGE")
    # Rights reference is an authorization reference only; avoid publishing
    # personally identifying or confidential license contents in the manifest.
    args.manifest.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("AUTHORIZED_DOCUMENTARY_PACKS_VERIFIED_MANIFEST_READY")


if __name__ == "__main__":
    main()
