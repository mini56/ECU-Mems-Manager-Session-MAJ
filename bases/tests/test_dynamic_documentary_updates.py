#!/usr/bin/env python3
"""No manufacturer files: regression tests for repeated multi-document updates."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sqlite3
import struct
import sys
import tempfile
import unittest
import zipfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

TOOL = Path(__file__).resolve().parents[1] / "tools" / "verify_licensed_release_and_enable.py"
SPEC = importlib.util.spec_from_file_location("validator", TOOL)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)
PASSWORD = "private-test-only-secret-12345"


def make_archive(language: str, documents: tuple[str, ...], broken_image=False) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"mems_documentary_{language}.sqlite"
        db = sqlite3.connect(path)
        db.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE documentary_database(
                singleton INTEGER PRIMARY KEY,schema_version INTEGER,
                language TEXT,publication_status TEXT);
            CREATE TABLE documentary_documents(
                document_id TEXT,source_revision TEXT,language TEXT,
                edition_code TEXT,source_sha256 TEXT,source_pages INTEGER,
                publisher TEXT,PRIMARY KEY(document_id,source_revision));
            CREATE TABLE documentary_pages(
                document_id TEXT,source_revision TEXT,physical_page INTEGER,
                PRIMARY KEY(document_id,source_revision,physical_page));
            CREATE TABLE documentary_entries(
                document_id TEXT,source_revision TEXT,entry_id TEXT,
                verification_status TEXT,source_page INTEGER,title TEXT,source_text TEXT);
            CREATE TABLE documentary_images(
                relative_path TEXT,asset_sha256 TEXT,asset_bytes INTEGER);
            CREATE VIRTUAL TABLE documentary_fts USING fts5(
                title,source_text,content='documentary_entries',content_rowid='rowid');
        """)
        db.execute("INSERT INTO documentary_database VALUES(1,1,?,'validated')", (language,))
        for i, doc in enumerate(documents):
            db.execute("INSERT INTO documentary_documents VALUES(?,?,?,?,?,?,?)",
                       (doc, "revision-1", language, doc, "a"*64, 2, "Synthetic test"))
            for p in (1, 2):
                db.execute("INSERT INTO documentary_pages VALUES(?,?,?)",
                           (doc, "revision-1", p))
            db.execute("INSERT INTO documentary_entries VALUES(?,?,?,?,?,?,?)",
                       (doc, "revision-1", "entry", "source_checked", 1,
                        "Synthetic", f"content {i}"))
            rowid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute("INSERT INTO documentary_fts(rowid,title,source_text) VALUES(?,?,?)",
                       (rowid, "Synthetic", f"content {i}"))
        image = b"\x89PNG\r\n\x1a\nFAKE-TEST-ONLY"
        imgname = "images/third_manual_002.png"
        digest = "b"*64 if broken_image else hashlib.sha256(image).hexdigest()
        db.execute("INSERT INTO documentary_images VALUES(?,?,?)",
                   (imgname, digest, len(image)))
        db.commit()
        db.close()
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as out:
            out.write(path, path.name)
            out.writestr(imgname, image)
        return payload.getvalue()


def encrypt(payload: bytes) -> bytes:
    salt, nonce = bytes(range(16)), bytes(range(12))
    header = b"MEMSDOC1" + b"\x01" + salt + nonce + struct.pack("<Q", len(payload))
    key = hashlib.pbkdf2_hmac("sha256", PASSWORD.encode(), salt, 210000, 32)
    return header + AESGCM(key).encrypt(nonce, payload, header)


class DynamicUpdates(unittest.TestCase):
    def test_three_documents_and_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "MEMS-DOC-FR-next.encrypted"
            path.write_bytes(encrypt(make_archive("fr", ("MANUAL-1","MANUAL-2","MANUAL-3"))))
            digest, documents = validator.validate_encrypted(path, "fr", PASSWORD)
            self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(len(documents), 3)
            self.assertEqual(documents[2]["document_id"], "MANUAL-3")

    def test_updates_can_repeat_and_preserve_existing_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            filename = root / "manifest.json"
            source = {
                "schema_version": 2, "application": "ECU MEMS Manager SESSION",
                "documentary_schema": "mems-documentary-multisource-v1",
                "documentary_bases": {
                    "fr": {
                        "database_file": "mems_documentary_fr.sqlite",
                        "published_documents": [{"document_id":"MANUAL-1"}],
                        "version":"fr-old"
                    }
                }
            }
            filename.write_text(json.dumps(source))
            pack = root / "MEMS-DOC-FR-next.encrypted"
            pack.write_bytes(encrypt(make_archive("fr", ("MANUAL-1","MANUAL-2"))))
            argv = sys.argv
            previous = os.environ.get("MEMS_DOCUMENTARY_PUBLISH_PASSWORD")
            try:
                os.environ["MEMS_DOCUMENTARY_PUBLISH_PASSWORD"] = PASSWORD
                for tag in ("doc-update-001", "doc-update-002"):
                    if tag.endswith("002"):
                        pack.write_bytes(encrypt(make_archive(
                            "fr", ("MANUAL-1","MANUAL-2","MANUAL-3"))))
                    sys.argv = [str(TOOL), "--manifest", str(filename),
                                "--asset-dir", str(root), "--tag", tag,
                                "--language", "fr", "--rights-confirmed",
                                "--rights-reference", "SYNTHETIC-TEST-ONLY"]
                    validator.main()
                actual = json.loads(filename.read_text())["documentary_bases"]["fr"]
                self.assertEqual(actual["version"], "fr-doc-update-002")
                self.assertEqual(actual["document_count"], 3)
                self.assertEqual(len(actual["published_documents"]), 3)
            finally:
                sys.argv = argv
                if previous is None:
                    os.environ.pop("MEMS_DOCUMENTARY_PUBLISH_PASSWORD", None)
                else:
                    os.environ["MEMS_DOCUMENTARY_PUBLISH_PASSWORD"] = previous

    def test_english_native_two_documents_is_valid(self):
        docs = validator.validate_zip(
            make_archive("en", ("EN-MANUAL-1","EN-MANUAL-2")), "en")
        self.assertEqual(len(docs), 2)

    def test_document_image_mismatch_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "DOCUMENT_IMAGE_HASH_INVALID"):
            validator.validate_zip(make_archive("fr", ("MANUAL-1",), True), "fr")

    def test_removed_document_rejected_without_manifest_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            state = {
                "schema_version": 2, "application":"ECU MEMS Manager SESSION",
                "documentary_schema":"mems-documentary-multisource-v1",
                "documentary_bases":{"fr":{
                    "database_file":"mems_documentary_fr.sqlite",
                    "published_documents":[{"document_id":"MANUAL-TO-KEEP"}]
                }}
            }
            manifest.write_text(json.dumps(state))
            pack = root / "MEMS-DOC-FR-next.encrypted"
            pack.write_bytes(encrypt(make_archive("fr", ("OTHER-MANUAL",))))
            old_argv = sys.argv
            old_secret = os.environ.get("MEMS_DOCUMENTARY_PUBLISH_PASSWORD")
            try:
                os.environ["MEMS_DOCUMENTARY_PUBLISH_PASSWORD"] = PASSWORD
                sys.argv = [str(TOOL), "--manifest", str(manifest),
                            "--asset-dir", str(root), "--tag", "next-release",
                            "--language", "fr", "--rights-confirmed",
                            "--rights-reference", "SYNTHETIC-TEST-ONLY"]
                with self.assertRaisesRegex(RuntimeError, "PREVIOUS_DOCUMENT_MISSING"):
                    validator.main()
                self.assertEqual(json.loads(manifest.read_text()), state)
            finally:
                sys.argv = old_argv
                if old_secret is None:
                    os.environ.pop("MEMS_DOCUMENTARY_PUBLISH_PASSWORD", None)
                else:
                    os.environ["MEMS_DOCUMENTARY_PUBLISH_PASSWORD"] = old_secret

    def test_encrypted_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"MEMS-DOC-FR-next.encrypted"
            data = bytearray(encrypt(make_archive("fr", ("MANUAL-1",))))
            data[-1] ^= 1
            path.write_bytes(data)
            with self.assertRaisesRegex(RuntimeError, "TAMPERED_PACK"):
                validator.validate_encrypted(path, "fr", PASSWORD)


if __name__ == "__main__":
    unittest.main()
