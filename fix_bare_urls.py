"""Fix bare URLs in markdown files - convert 'text: https://url' to '[text](url)' format."""
import re
import glob

def fix_bare_urls(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Pattern: "- Some text: https://url" -> "- [Some text](https://url)"
    # Match lines like "- H430 (elohim): https://www.blueletterbible.org/..."
    # or "- Blue Letter Bible LXX Genesis 6:2: https://..."
    def replace_bare_url_line(m):
        prefix = m.group(1)  # "- " or "  - " etc
        label = m.group(2).rstrip()  # "H430 (elohim)"
        url = m.group(3)  # the URL
        return f"{prefix}[{label}]({url})"

    content = re.sub(
        r'^([ \t]*- )(.+?):\s+(https://\S+)$',
        replace_bare_url_line,
        content,
        flags=re.MULTILINE
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        # Count changes
        changes = sum(1 for a, b in zip(original.split('\n'), content.split('\n')) if a != b)
        return changes
    return 0

total = 0
files_changed = 0
for filepath in glob.glob('docs/**/*.md', recursive=True):
    count = fix_bare_urls(filepath)
    if count > 0:
        print(f"  {filepath}: {count} links fixed")
        total += count
        files_changed += 1

print(f"\nTotal: {total} bare URLs converted to markdown links across {files_changed} files")
