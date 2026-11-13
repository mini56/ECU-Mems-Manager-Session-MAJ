#!/usr/bin/env python3
"""Rotate FR/EN documentary installation password without touching source DBs.

Old key: MEMS_DOCUMENTARY_PUBLISH_PASSWORD (existing GitHub secret).
New key: MEMS_DOCUMENTARY_INSTALL_PASSWORD (chosen by the owner, GitHub secret).
The new key must NEVER be passed via CLI, in a GitHub workflow input, or
written to a manifest/release/workflow log. Only encrypted bytes are published.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from verify_licensed_release_and_enable import validate_encrypted, validate_zip

MAX_BYTES = 256 * 1024 * 1024
TAG_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,43}$")
REPOSITORY = "mini56/ECU-Mems-Manager-Session-MAJ"


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def decrypt(data: bytes, password: str) -> bytes:
    ensure(data[:8] == b"MEMSDOC1" and data[8:9] == b"\x01",
           "PUBLISHED_ENCRYPTED_FORMAT_INVALID")
    ensure(62 <= len(data) <= MAX_BYTES and
           struct.unpack_from("<Q", data, 37)[0] == len(data) - 61,
           "PUBLISHED_ENCRYPTED_LENGTH_INVALID")
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), data[9:25], 210000, 32)
    return AESGCM(key).decrypt(data[25:37], data[45:], data[:45])


def encrypt(plaintext: bytes, password: str) -> bytes:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    header = b"MEMSDOC1" + b"\x01" + salt + nonce + struct.pack("<Q", len(plaintext))
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 210000, 32)
    return header + AESGCM(key).encrypt(nonce, plaintext, header)


def rotate(
    previous: dict, source_folder: Path, output_folder: Path,
    tag: str, old_password: str, new_password: str
) -> dict:
    ensure(TAG_RE.fullmatch(tag) is not None, "INVALID_RELEASE_TAG")
    ensure(len(old_password) >= 12 and len(new_password) >= 12,
           "PUBLISH_AND_NEW_INSTALL_SECRETS_REQUIRED")
    ensure(old_password != new_password, "NEW_INSTALL_PASSWORD_MUST_DIFFER")
    ensure(previous.get("schema_version") == 2 and
           previous.get("documentary_schema") == "mems-documentary-multisource-v1",
           "CATALOG_SCHEMA_INVALID")
    future = json.loads(json.dumps(previous))
    output_folder.mkdir(parents=True, exist_ok=True)
    for language in ("fr", "en"):
        entry = future["documentary_bases"][language]
        ensure(entry.get("available") is True and
               entry.get("installation_password_required") is True,
               "PUBLISHED_LANGUAGE_MISSING_" + language.upper())
        source_name = "original-" + language + ".encrypted"
        path = source_folder / source_name
        ensure(path.is_file() and not path.is_symlink(), "ORIGINAL_PACK_NOT_FOUND")
        data = path.read_bytes()
        ensure(hashlib.sha256(data).hexdigest() == entry.get("sha256"),
               "ORIGINAL_PUBLISHED_SHA256_MISMATCH_" + language.upper())
        _, old_docs = validate_encrypted(path, language, old_password)
        plaintext = decrypt(data, old_password)
        ensure(plaintext.startswith(b"PK\x03\x04"), "DECRYPTED_CONTENT_NOT_ZIP")
        ensure(old_docs == validate_zip(plaintext, language),
               "REKEY_INCONSISTENT_DOCUMENTS")
        new_name = f"MEMS-DOC-{language.upper()}-INSTALLKEY-{tag}.encrypted"
        destination = output_folder / new_name
        destination.write_bytes(encrypt(plaintext, new_password))
        new_hash, new_docs = validate_encrypted(destination, language, new_password)
        ensure(old_docs == new_docs, "DOCUMENT_CHANGE_DURING_REKEY")
        new_version = f"{language}-{tag}"
        ensure(len(new_version) <= 50, "NEW_VERSION_TOO_LONG")
        entry.update({
            "version": new_version,
            "release_url":
                f"https://github.com/{REPOSITORY}/releases/download/{tag}/{new_name}",
            "sha256": new_hash,
            "published_documents": new_docs,
            "document_count": len(new_docs),
            "installation_password_required": True,
            "encrypted_package_required": True,
        })
        print(f"PASSWORD_ROTATION_VERIFIED_{language.upper()}_DOCUMENTS={len(new_docs)}")
    return future


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--originals", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--result-manifest", required=True, type=Path)
    args = parser.parse_args()
    old_password = os.environ.get("MEMS_DOCUMENTARY_PUBLISH_PASSWORD", "")
    new_password = os.environ.get("MEMS_DOCUMENTARY_INSTALL_PASSWORD", "")
    previous = json.loads(args.manifest.read_text(encoding="utf-8"))
    future = rotate(
        previous, args.originals, args.output, args.tag,
        old_password, new_password)
    args.result_manifest.write_text(
        json.dumps(future, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("NEW_PASSWORD_ENCRYPTED_PACKS_AND_MANIFEST_VERIFIED")


if __name__ == "__main__":
    main()
