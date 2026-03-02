#!/usr/bin/env python3
import argparse
import json
import os


def collect_files(node, base_path=""):
    """
    Recursively collect relative file paths from a tree -J JSON structure.
    """
    files = []

    if isinstance(node, list):
        for item in node:
            if isinstance(item, dict):
                files.extend(collect_files(item, base_path))
        return files

    if node.get("type") == "report":
        return files  # ignore summary

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


def file_exists_in_any(path_rel, dirs):
    """Return True if the file exists in any of the given directories."""
    for d in dirs:
        full_path = os.path.join(d, path_rel)
        if os.path.exists(full_path):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Compare ROM list (tree -J) against one or more NAS directories."
    )
    parser.add_argument("json_file", help="Path to JSON file from `tree -J` output.")
    parser.add_argument(
        "nas_dirs",
        nargs="+",
        help="One or more NAS directories to search (first is primary, rest are fallbacks).",
    )
    parser.add_argument(
        "--report",
        help="Optional path to save text report.",
        default="roms_comparison_report.txt",
    )
    args = parser.parse_args()

    with open(args.json_file, "r") as f:
        data = json.load(f)

    mac_files = collect_files(data)

    # Clean up relative paths
    mac_files = [
        f[2:] if f.startswith("./") else f.lstrip("./").lstrip("/") for f in mac_files
    ]
    mac_files = [f for f in mac_files if f]

    missing = []
    found = []

    for rel_path in mac_files:
        if file_exists_in_any(rel_path, args.nas_dirs):
            found.append(rel_path)
        else:
            missing.append(rel_path)

    print("=== ROM Comparison Report ===")
    print(f"Total ROMs in JSON: {len(mac_files)}")
    print(f"Found on NAS (any path): {len(found)}")
    print(f"Missing across all NAS dirs: {len(missing)}")

    if missing:
        print("\n❌ Missing files:")
        for f in missing:
            print("  -", f)

    if args.report:
        with open(args.report, "w") as out:
            out.write("=== ROM Comparison Report ===\n\n")
            out.write(f"Total ROMs in JSON: {len(mac_files)}\n")
            out.write(f"Found on NAS (any path): {len(found)}\n")
            out.write(f"Missing across all NAS dirs: {len(missing)}\n\n")
            if missing:
                out.write("❌ Missing files:\n")
                for f in missing:
                    out.write(f"  - {f}\n")
        print(f"\n📄 Report saved to {args.report}")


if __name__ == "__main__":
    main()
