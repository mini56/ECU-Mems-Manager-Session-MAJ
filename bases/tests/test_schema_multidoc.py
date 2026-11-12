#!/usr/bin/env python3
"""SQLite multi-document contract tests; stdlib only, no manufacturer documents.

These synthetic tests do not certify the actual Rover corpus or MEMS Manager
integration. They validate isolation and safe cumulative import semantics.
"""
from __future__ import annotations
import hashlib
import sqlite3
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema_multidoc_v1.sql"


def fake_sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def insert_document(db: sqlite3.Connection, doc: str, revision: str,
                    language: str, edition: str) -> None:
    db.execute(
        "INSERT INTO documentary_documents "
        "(document_id,source_revision,language,publisher,edition_code,"
        "source_filename,source_format,source_sha256,source_pages) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (doc, revision, language, "Example manufacturer (TEST ONLY)",
         edition, edition + ".pdf", "PDF", fake_sha(edition), 10),
    )


def insert_entry(db: sqlite3.Connection, doc: str, revision: str,
                 entry_id: str, reference: str, text: str) -> None:
    db.execute(
        "INSERT INTO documentary_entries "
        "(document_id,source_revision,entry_id,entry_type,"
        "manufacturer_reference,source_page,source_text) "
        "VALUES(?,?,?,?,?,?,?)",
        (doc, revision, entry_id, "step", reference, 3, text),
    )


def must_reject(action, label: str) -> None:
    try:
        action()
    except sqlite3.IntegrityError:
        return
    raise AssertionError("MUST_REJECT_" + label)


def test_main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        french_file = Path(temp) / "mems_documentary_fr.sqlite"
        english_file = Path(temp) / "mems_documentary_en.sqlite"
        schema = SCHEMA.read_text(encoding="utf-8")

        with sqlite3.connect(french_file) as french:
            french.executescript(schema)
            french.execute(
                "INSERT INTO documentary_database(singleton,schema_version,"
                "language,collection_revision) VALUES(1,1,'fr',1)"
            )
            with french:
                insert_document(french, "rover-akm7169", "r1", "fr", "AKM7169FRE")
                insert_entry(french, "rover-akm7169", "r1", "step001",
                             "12.65.12", "Dépose de la culasse.")
            first_snapshot = french.execute(
                "SELECT source_text FROM documentary_entries WHERE document_id=?",
                ("rover-akm7169",),
            ).fetchall()

            # Add a completely unrelated document without replacing Rover.
            with french:
                insert_document(french, "manual-other-maker", "rev-a", "fr",
                                "OTHER-FR")
                insert_entry(french, "manual-other-maker", "rev-a", "step001",
                             "12.65.12", "Instruction du second manuel.")

            references = french.execute(
                "SELECT document_id,source_text FROM documentary_entries "
                "WHERE manufacturer_reference=? ORDER BY document_id",
                ("12.65.12",),
            ).fetchall()
            assert len(references) == 2, "different manuals can share operation numbers"
            assert references[0][0] != references[1][0], "references are document-scoped"
            assert french.execute(
                "SELECT source_text FROM documentary_entries WHERE document_id=?",
                ("rover-akm7169",),
            ).fetchall() == first_snapshot, "original contents preserved"

            # A newer edition coexists with its old source and provenance.
            with french:
                insert_document(french, "rover-akm7169", "r2", "fr", "AKM7169FRE-REV2")
                insert_entry(french, "rover-akm7169", "r2", "step001",
                             "12.65.12", "Nouvelle édition française contrôlée.")
            count = french.execute(
                "SELECT COUNT(*) FROM documentary_documents"
            ).fetchone()[0]
            assert count == 3, "two manuals and two revisions coexist"

            must_reject(
                lambda: insert_document(french, "manual-english", "r1",
                                        "en", "OTHER-ENG"),
                "FOREIGN_LANGUAGE_INSIDE_FRENCH_DATABASE",
            )
            must_reject(
                lambda: french.execute(
                    "UPDATE documentary_documents SET source_sha256=? "
                    "WHERE document_id=? AND source_revision=?",
                    (fake_sha("different"), "rover-akm7169", "r1"),
                ),
                "SILENT_MANUFACTURER_SOURCE_REPLACEMENT",
            )
            must_reject(
                lambda: french.execute(
                    "UPDATE documentary_database SET language='en'"
                ),
                "CHANGING_DATABASE_LANGUAGE",
            )

            # A rejected import is atomic, not a partly installed document.
            try:
                with french:
                    insert_document(french, "third-document", "r1", "fr", "THIRD-FR")
                    insert_entry(french, "nonexistent-document", "r1",
                                 "step001", "1.1", "Ligne sans source.")
            except sqlite3.IntegrityError:
                pass
            else:
                raise AssertionError("BROKEN_IMPORT_MUST_FAIL")
            assert french.execute(
                "SELECT COUNT(*) FROM documentary_documents"
            ).fetchone()[0] == 3, "failed addition must roll back entirely"
            assert french.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert not french.execute("PRAGMA foreign_key_check").fetchall()

            table_names = {
                row[0] for row in french.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            assert "ecu" not in table_names
            assert "ecu_mems_manager" not in table_names

        with sqlite3.connect(english_file) as english:
            english.executescript(schema)
            english.execute(
                "INSERT INTO documentary_database(singleton,schema_version,"
                "language,collection_revision) VALUES(1,1,'en',1)"
            )
            with english:
                insert_document(english, "rover-akm7169", "r1", "en", "AKM7169ENG")
                insert_entry(english, "rover-akm7169", "r1", "step001",
                             "12.65.12", "Remove the cylinder head.")
            assert english.execute(
                "SELECT language FROM documentary_database"
            ).fetchone()[0] == "en"
            assert english.execute(
                "SELECT COUNT(*) FROM documentary_documents"
            ).fetchone()[0] == 1

        # Neither DB contains source rows of the other language.
        with sqlite3.connect(french_file) as fr, \
                sqlite3.connect(english_file) as en:
            assert fr.execute(
                "SELECT COUNT(*) FROM documentary_documents WHERE language!='fr'"
            ).fetchone()[0] == 0
            assert en.execute(
                "SELECT COUNT(*) FROM documentary_documents WHERE language!='en'"
            ).fetchone()[0] == 0
            assert fr.execute(
                "SELECT COUNT(*) FROM documentary_documents"
            ).fetchone()[0] == 3
            assert en.execute(
                "SELECT COUNT(*) FROM documentary_documents"
            ).fetchone()[0] == 1
    print("PASS_MULTI_SOURCE_SAME_LANGUAGE_ADDITIVE_NON_DESTRUCTIVE")
    print("PASS_SOURCE_REVISION_AND_DUPLICATE_REFERENCE_ISOLATION")
    print("PASS_CROSS_LANGUAGE_REJECTED_AND_FK_ROLLBACK")
    print("PASS_NO_ECU_PERSONAL_OR_EXPERT_DATABASE_IN_DOCUMENTARY_SCHEMA")


if __name__ == "__main__":
    test_main()
