#!/usr/bin/env python3
import argparse
import sys
import re

def main():
    parser = argparse.ArgumentParser(description="Antigravity Memory Manager")
    parser.add_argument("--file", required=True, help="Path to the memory markdown file")
    parser.add_argument("--action", required=True, choices=["add", "replace", "remove"], help="Action to perform")
    parser.add_argument("--target", help="Substring target for replace/remove actions (must be uniquely identifiable in a block/line)")
    parser.add_argument("--content", help="New content to add or replace with")

    args = parser.parse_args()

    if args.action in ["replace", "remove"] and not args.target:
        print("Error: --target is required for replace/remove actions", file=sys.stderr)
        sys.exit(1)

    if args.action in ["add", "replace"] and args.content is None:
        print("Error: --content is required for add/replace actions", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        if args.action == "add":
            lines = []
        else:
            print(f"Error: File {args.file} not found.", file=sys.stderr)
            sys.exit(1)

    if args.action == "add":
        if not lines:
            lines.append(args.content + "\n")
        else:
            if not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            lines.append(args.content + "\n")

    elif args.action in ["replace", "remove"]:
        # Find which block/paragraph contains the target substring
        matches = []
        for i, line in enumerate(lines):
            if args.target in line:
                matches.append(i)

        if len(matches) == 0:
            print(f"Error: Target substring '{args.target}' not found.", file=sys.stderr)
            sys.exit(1)
        elif len(matches) > 1:
            print(f"Error: Target substring '{args.target}' is not unique. Found in {len(matches)} lines. Please provide a more specific substring.", file=sys.stderr)
            sys.exit(1)

        match_idx = matches[0]

        if args.action == "replace":
            lines[match_idx] = lines[match_idx].replace(args.target, args.content)
            # If replacing an entire line representation, we might just swap the line.
            # But substring mapping ensures we don't accidentally replace the wrong thing.
            print(f"Successfully replaced text in line {match_idx + 1}")
        elif args.action == "remove":
            # For remove, we can remove the sentence, or if it's a bullet point, the whole line.
            line = lines[match_idx]
            new_line = line.replace(args.target, "")
            if new_line.strip() == "" or new_line.strip() == "-":
                # Remove entire line
                lines.pop(match_idx)
            else:
                lines[match_idx] = new_line
            print(f"Successfully removed text in line {match_idx + 1}")

    with open(args.file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print("Action completed successfully.")

if __name__ == "__main__":
    main()
