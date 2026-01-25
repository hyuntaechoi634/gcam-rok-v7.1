#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Find <floor-to-surface-ratio> in XML files and report entries whose text != 5.5
(or missing, if --report-missing is set).

Usage:
  python check_floor_ratio.py /path/to/file_or_dir
  python check_floor_ratio.py /path/to/dir --recursive
  python check_floor_ratio.py /path/to/dir --recursive --report-missing
  python check_floor_ratio.py /path/to/dir --recursive --tolerance 1e-9
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import xml.etree.ElementTree as ET


def iter_xml_files(path: Path, recursive: bool) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        pattern = "**/*.xml" if recursive else "*.xml"
        return sorted(path.glob(pattern))
    raise FileNotFoundError(f"Not found: {path}")


def safe_float(s: str | None) -> float | None:
    if s is None:
        return None
    s = s.strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def localname(tag: str) -> str:
    # Handles namespaces: {ns}floor-to-surface-ratio -> floor-to-surface-ratio
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def find_ratio_elements(root: ET.Element) -> list[ET.Element]:
    # Robust to namespaces by checking localname
    out = []
    for el in root.iter():
        if localname(el.tag) == "floor-to-surface-ratio":
            out.append(el)
    return out


def element_path(el: ET.Element, parent_map: dict[ET.Element, ET.Element]) -> str:
    # Build a simple XPath-like path with indices among same-tag siblings
    parts = []
    cur = el
    while cur is not None:
        p = parent_map.get(cur)
        tag = localname(cur.tag)
        if p is None:
            parts.append(f"/{tag}")
            break
        # index among siblings with same tag
        same = [c for c in list(p) if localname(c.tag) == tag]
        if len(same) > 1:
            idx = same.index(cur) + 1
            parts.append(f"/{tag}[{idx}]")
        else:
            parts.append(f"/{tag}")
        cur = p
    return "".join(reversed(parts))


def build_parent_map(root: ET.Element) -> dict[ET.Element, ET.Element]:
    return {c: p for p in root.iter() for c in list(p)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="XML file or directory")
    ap.add_argument("--recursive", action="store_true", help="Search directories recursively")
    ap.add_argument("--expected", type=float, default=5.5, help="Expected value (default: 5.5)")
    ap.add_argument("--tolerance", type=float, default=0.0,
                    help="Numeric tolerance for float comparisons (default: 0)")
    ap.add_argument("--report-missing", action="store_true",
                    help="Also report if the element is missing in a file")
    args = ap.parse_args()

    base = Path(args.path)
    xml_files = iter_xml_files(base, args.recursive)

    if not xml_files:
        print("No XML files found.")
        return

    any_issues = False
    for fp in xml_files:
        try:
            tree = ET.parse(fp)
            root = tree.getroot()
        except Exception as e:
            any_issues = True
            print(f"[PARSE_ERROR] {fp}: {e}")
            continue

        parent_map = build_parent_map(root)
        elems = find_ratio_elements(root)

        if not elems:
            if args.report_missing:
                any_issues = True
                print(f"[MISSING] {fp} : <floor-to-surface-ratio> not found")
            continue

        for el in elems:
            txt = (el.text or "").strip()
            val = safe_float(txt)
            path_str = element_path(el, parent_map)

            bad = False
            reason = ""
            if val is None:
                bad = True
                reason = f"non-numeric/empty text={txt!r}"
            else:
                if args.tolerance > 0:
                    if not math.isclose(val, args.expected, rel_tol=0.0, abs_tol=args.tolerance):
                        bad = True
                        reason = f"value={val} (expected {args.expected} ± {args.tolerance})"
                else:
                    if val != args.expected:
                        bad = True
                        reason = f"value={val} (expected {args.expected})"

            if bad:
                any_issues = True
                print(f"[NOT_EXPECTED] {fp} {path_str} : {reason}")

    if not any_issues:
        print("OK: all <floor-to-surface-ratio> values match the expected value.")


if __name__ == "__main__":
    main()
