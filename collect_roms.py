#!/usr/bin/env python3
import argparse
import json
import os
import shutil


def collect_files(node, base_path=""):
    """Recursively collect relative file paths from a tree -J JSON structure."""
    files = []

    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict):
                files.extend(collect_files(item, base_path))
        return files

    if node.get("type") == "report":
        return files  # skip summary

    name = node.get("name")
    if not name:
        return files

    path = os.path.join(base_path, name)

    if node.get("type") == "file":
        files.append(path)
    elif node.get("type") == "directory":
        for sub in node.get("contents", []):
            files.extend(collect_files(sub, path))

    return files


def find_existing_file(rel_path, source_dirs):
    """Return the first full path that exists among the given source dirs, or None."""
    for d in source_dirs:
        full_path = os.path.join(d, rel_path)
        if os.path.exists(full_path):
            return full_path
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Copy all ROMs listed in a tree -J JSON to a new directory, "
        "searching across multiple source paths."
    )
    parser.add_argument("json_file", help="Path to JSON file from `tree -J`.")
    parser.add_argument(
        "source_dirs",
        nargs="+",
        help="Source directories to search (first is primary, rest are fallbacks).",
    )
    parser.add_argument(
        "--dest",
        required=True,
        help="Destination directory where ROMs should be copied (folder structure preserved).",
    )
    parser.add_argument(
        "--exclude-system",
        action="append",
        dest="exclude_systems",
        default=[],
        help="Exclude specific system directories (e.g. --exclude-system PS2). Can be used multiple times.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be copied without actually copying files.",
    )
    args = parser.parse_args()

    # Normalize excluded system names (case-insensitive)
    excluded = {s.lower() for s in args.exclude_systems}

    with open(args.json_file, "r") as f:
        data = json.load(f)

    rom_files = collect_files(data)
    rom_files = [
        f[2:] if f.startswith("./") else f.lstrip("./").lstrip("/") for f in rom_files
    ]
    rom_files = [f for f in rom_files if f]

    # Filter excluded systems
    if excluded:
        rom_files = [
            f
            for f in rom_files
            if not any(f.lower().startswith(ex + "/") for ex in excluded)
        ]

    copied = []
    missing = []

    for rel_path in rom_files:
        src_path = find_existing_file(rel_path, args.source_dirs)
        if not src_path:
            missing.append(rel_path)
            continue

        dest_path = os.path.join(args.dest, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        if not args.dry_run:
            shutil.copy2(src_path, dest_path)
        copied.append(rel_path)

    print("=== ROM Collection Report ===")
    print(f"Total ROMs in JSON (after exclusions): {len(rom_files)}")
    print(f"Copied: {len(copied)}")
    print(f"Missing: {len(missing)}")

    if excluded:
        print(f"Excluded systems: {', '.join(sorted(excluded))}")

    if missing:
        print("\n❌ Missing files:")
        for f in missing:
            print("  -", f)

    if args.dry_run:
        print("\n💡 Dry run mode: no files were actually copied.")


if __name__ == "__main__":
    main()
