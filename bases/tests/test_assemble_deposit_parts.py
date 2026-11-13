#!/usr/bin/env python3
"""Regression checks for uploading one large encrypted database in two pieces."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "assemble_deposit_parts.py"
spec = importlib.util.spec_from_file_location("parts", TOOL)
parts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parts)


class TwoPartUpload(unittest.TestCase):
    BASENAME = "MEMS-DOC-FR-RCL0193FRE-AKM7169FRE-SPI-20261113-MAJ.encrypted"

    def make_temp(self):
        return tempfile.TemporaryDirectory()

    def test_two_halves_restore_exact_28_mb_original(self):
        with self.make_temp() as tmp:
            root = Path(tmp)
            depot, target = root / "depot", root / "output"
            depot.mkdir()
            # Only the framing is inspected in this unit; AES-GCM authentication,
            # database and licensing checks are performed by the publisher.
            original = b"MEMSDOC1" + b"\x01" + b"x" * (28_098_898 - 9)
            midpoint = (len(original) + 1) // 2
            (depot / (self.BASENAME + ".part1")).write_bytes(original[:midpoint])
            (depot / (self.BASENAME + ".part2")).write_bytes(original[midpoint:])
            result = parts.collect_deposits(
                depot,
                ["bases/depot/" + self.BASENAME + ".part1",
                 "bases/depot/" + self.BASENAME + ".part2"],
                target,
            )
            self.assertEqual(len(result), 1)
            self.assertEqual(result["fr"]["source_parts"], 2)
            self.assertEqual(result["fr"]["size"], 28_098_898)
            self.assertEqual(result["fr"]["sha256"], hashlib.sha256(original).hexdigest())
            self.assertEqual((target / self.BASENAME).read_bytes(), original)

    def test_first_part_alone_is_not_published(self):
        with self.make_temp() as tmp:
            root = Path(tmp)
            depot = root / "depot"
            depot.mkdir()
            (depot / (self.BASENAME + ".part1")).write_bytes(b"MEMSDOC1" + b"X" * 200)
            value = parts.collect_deposits(
                depot, ["bases/depot/" + self.BASENAME + ".part1"], root / "output")
            self.assertEqual(value, {})

    def test_later_second_part_completes_earlier_upload(self):
        with self.make_temp() as tmp:
            root = Path(tmp)
            depot = root / "depot"
            depot.mkdir()
            original = b"MEMSDOC1" + b"Y" * 500
            (depot / (self.BASENAME + ".part1")).write_bytes(original[:255])
            (depot / (self.BASENAME + ".part2")).write_bytes(original[255:])
            result = parts.collect_deposits(
                depot, ["bases/depot/" + self.BASENAME + ".part2"], root / "output")
            self.assertEqual(result["fr"]["size"], len(original))

    def test_direct_english_pack_remains_supported(self):
        with self.make_temp() as tmp:
            root = Path(tmp)
            depot = root / "depot"
            depot.mkdir()
            name = "MEMS-DOC-EN-AKM7169ENG-20261113-MAJ.encrypted"
            content = b"MEMSDOC1" + b"Z" * 100
            (depot / name).write_bytes(content)
            result = parts.collect_deposits(
                depot, ["bases/depot/" + name], root / "output")
            self.assertEqual(result["en"]["source_parts"], 1)
            self.assertEqual((root / "output" / name).read_bytes(), content)

    def test_split_corruption_is_not_silently_fixed(self):
        with self.make_temp() as tmp:
            root = Path(tmp)
            depot = root / "depot"
            depot.mkdir()
            (depot / (self.BASENAME + ".part1")).write_bytes(b"INVALID" + b"A" * 30)
            (depot / (self.BASENAME + ".part2")).write_bytes(b"B" * 90)
            with self.assertRaisesRegex(ValueError, "PACK_FORMAT_INVALID"):
                parts.collect_deposits(
                    depot, ["bases/depot/" + self.BASENAME + ".part2"], root / "output")
            self.assertFalse((root / "output" / self.BASENAME).exists())

    def test_oversized_part_is_refused(self):
        with self.make_temp() as tmp:
            root = Path(tmp)
            depot = root / "depot"
            depot.mkdir()
            with (depot / (self.BASENAME + ".part1")).open("wb") as stream:
                stream.truncate(parts.MAX_BROWSER_PART + 1)
            (depot / (self.BASENAME + ".part2")).write_bytes(b"X")
            with self.assertRaisesRegex(ValueError, "SPLIT_PART_TOO_LARGE"):
                parts.collect_deposits(
                    depot, ["bases/depot/" + self.BASENAME + ".part2"], root / "output")

    def test_cannot_publish_two_versions_same_language_in_one_push(self):
        with self.make_temp() as tmp:
            root = Path(tmp)
            depot = root / "depot"
            depot.mkdir()
            new = "MEMS-DOC-FR-SECOND-EDITION.encrypted"
            with self.assertRaisesRegex(ValueError, "MORE_THAN_ONE"):
                parts.collect_deposits(
                    depot, ["bases/depot/" + self.BASENAME + ".part1",
                            "bases/depot/" + new], root / "output")


if __name__ == "__main__":
    unittest.main()
