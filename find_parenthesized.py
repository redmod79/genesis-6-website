"""Find all parenthesized text in report files and categorize them."""
import re
from pathlib import Path

report_dir = Path(r"D:\bible\genesis-6-website\docs\report")

# Pattern: capture content inside parentheses
paren_pattern = re.compile(r'\(([^)]+)\)')
# Pattern: already has a BLB link inside
blb_pattern = re.compile(r'blueletterbible\.org')

for md_file in sorted(report_dir.glob("*.md")):
    findings = []
    for i, line in enumerate(md_file.read_text(encoding="utf-8").splitlines(), 1):
        for match in paren_pattern.finditer(line):
            content = match.group(1)
            has_link = bool(blb_pattern.search(content))
            findings.append((i, content, has_link))

    if findings:
        print(f"\n{'='*80}")
        print(f"FILE: {md_file.name}")
        print(f"{'='*80}")
        for line_num, content, has_link in findings:
            status = "LINKED" if has_link else "NOT LINKED"
            # Truncate long content
            display = content if len(content) <= 120 else content[:120] + "..."
            print(f"  Line {line_num:4d} [{status:10s}]: ({display})")
