"""Link all unlinked study references across the website's .md files."""
import re
from pathlib import Path

docs_dir = Path(r"D:\bible\genesis-6-website\docs")

# All 28 study folder names that exist on this site
VALID_STUDIES = {
    "genesis-6-sons-of-god",
    "genesis-6-sons-of-god_2",
    "genesis-6-sons-of-god-comprehensive-synthesis",
    "genesis-4-5-narrative-context-genesis-6",
    "genesis-6-4-grammar-analysis",
    "genesis-6-lxx-nt-comparison",
    "septuagint-genesis-6-translation",
    "nt-sons-of-god-humans",
    "hebrew-greek-sons-of-god-comparison",
    "gods-people-vs-angels-terminology",
    "moses-angel-terminology",
    "moses-human-god-relationship-terms",
    "jesus-angels-marriage-hermeneutical-ceiling",
    "matthew-24-days-of-noah",
    "psalm-82-gods",
    "deuteronomy-32-8-sons-of-god",
    "2-peter-2-4-angels-that-sinned",
    "jude-6-7-angels-sin",
    "jude-1-6-7-in-like-manner",
    "strange-flesh-jude-1-7",
    "1-peter-3-spirits-in-prison",
    "nephilim-origin",
    "angels-physical-form",
    "all-flesh-corrupted",
    "flood-judgment-severity",
    "second-temple-literature-genesis-6",
    "pentateuch-sexual-legislation-angel-unions",
    "genesis-6-explicit-vs-implied-evidence",
}

# Sort by longest first to avoid partial matches
SORTED_STUDIES = sorted(VALID_STUDIES, key=len, reverse=True)


def get_relative_link(from_file: Path, study_name: str) -> str:
    """Compute relative link from a file to a study's CONCLUSION.md."""
    rel = from_file.relative_to(docs_dir)
    parts = rel.parts

    if parts[0] == "report":
        return f"../studies/{study_name}/CONCLUSION.md"
    elif parts[0] == "studies":
        return f"../{study_name}/CONCLUSION.md"
    return f"studies/{study_name}/CONCLUSION.md"


def count_exact_unlinked(line: str, study_name: str) -> int:
    """Count occurrences of study_name that are NOT inside markdown links.
    Uses exact word boundary matching to avoid substring issues."""
    # First find all occurrences of the study name with word boundaries
    # Word boundary for these names: not preceded/followed by alphanumeric, hyphen, or underscore
    # But since study names contain hyphens, we need char-class boundaries
    boundary_before = r'(?<![a-zA-Z0-9_\-])'
    boundary_after = r'(?![a-zA-Z0-9_\-])'
    all_matches = list(re.finditer(boundary_before + re.escape(study_name) + boundary_after, line))
    if not all_matches:
        return 0

    # Now find which ones are inside markdown links [text](url)
    link_spans = []
    for m in re.finditer(r'\[[^\]]*\]\([^)]*\)', line):
        link_spans.append((m.start(), m.end()))

    unlinked = 0
    for m in all_matches:
        inside_link = any(ls <= m.start() and m.end() <= le for ls, le in link_spans)
        if not inside_link:
            unlinked += 1
    return unlinked


def replace_exact_unlinked(line: str, study_name: str, link: str) -> str:
    """Replace unlinked occurrences of study_name with markdown links.
    Handles the substring problem by using exact boundaries."""
    boundary_before = r'(?<![a-zA-Z0-9_\-])'
    boundary_after = r'(?![a-zA-Z0-9_\-])'
    pattern = re.compile(boundary_before + re.escape(study_name) + boundary_after)

    # Find link spans to avoid replacing inside existing links
    link_spans = []
    for m in re.finditer(r'\[[^\]]*\]\([^)]*\)', line):
        link_spans.append((m.start(), m.end()))

    # Process matches from right to left to preserve indices
    matches = list(pattern.finditer(line))
    for m in reversed(matches):
        inside_link = any(ls <= m.start() and m.end() <= le for ls, le in link_spans)
        if not inside_link:
            replacement = f'[{study_name}]({link})'
            line = line[:m.start()] + replacement + line[m.end():]

    return line


def link_table_cells(line: str, from_file: Path) -> str:
    """Link study names in table cells like '| study-name | description |'"""
    if '|' not in line:
        return line
    for study in SORTED_STUDIES:
        if count_exact_unlinked(line, study) > 0:
            link = get_relative_link(from_file, study)
            line = replace_exact_unlinked(line, study, link)
    return line


def link_backtick_paths(line: str, from_file: Path) -> str:
    """Link backtick-wrapped paths like `bible-studies/study-name/` or `../study-name/`"""
    for study in SORTED_STUDIES:
        patterns = [
            re.compile(r'`bible-studies/' + re.escape(study) + r'/?`'),
            re.compile(r'`\.\./' + re.escape(study) + r'/?`'),
            re.compile(r'`/home/michael/bible/bible-studies/' + re.escape(study) + r'/?`'),
        ]
        for pat in patterns:
            if pat.search(line):
                link = get_relative_link(from_file, study)
                line = pat.sub('[' + study + '](' + link + ')', line)
    return line


def link_source_and_footer(line: str, from_file: Path) -> str:
    """Link study names in source/footer lines like:
    '*Source: study-a, study-b*'
    '*Related studies: study-a, study-b*'
    '*Prerequisite studies: study-a, study-b*'
    """
    if not re.search(r'(?:Prerequisite|Related|Source)\s*(?:stud|:)', line, re.IGNORECASE):
        return line

    for study in SORTED_STUDIES:
        if count_exact_unlinked(line, study) > 0:
            link = get_relative_link(from_file, study)
            line = replace_exact_unlinked(line, study, link)
    return line


def link_headings(line: str, from_file: Path) -> str:
    """Link study names in headings like '### genesis-6-sons-of-god Study'
    or '## Connection to genesis-6-sons-of-god Word Studies'"""
    if not line.lstrip().startswith('#'):
        return line

    for study in SORTED_STUDIES:
        if count_exact_unlinked(line, study) > 0:
            link = get_relative_link(from_file, study)
            line = replace_exact_unlinked(line, study, link)
    return line


def link_see_also_paths(line: str, from_file: Path) -> str:
    """Link absolute paths like '/home/michael/bible/bible-studies/study-name/'"""
    for study in SORTED_STUDIES:
        pattern = re.compile(r'`?/home/michael/bible/bible-studies/' + re.escape(study) + r'/?`?')
        if pattern.search(line):
            link = get_relative_link(from_file, study)
            line = pattern.sub('[' + study + '](' + link + ')', line)
    return line


def link_italics_study_refs(line: str, from_file: Path) -> str:
    """Link study names in italics like *study-name* study"""
    for study in SORTED_STUDIES:
        pattern = re.compile(r'\*' + re.escape(study) + r'\*')
        if pattern.search(line):
            # Check it's not already inside a link
            link_spans = [(m.start(), m.end()) for m in re.finditer(r'\[[^\]]*\]\([^)]*\)', line)]
            for m in pattern.finditer(line):
                inside = any(ls <= m.start() and m.end() <= le for ls, le in link_spans)
                if not inside:
                    link = get_relative_link(from_file, study)
                    line = pattern.sub('[' + study + '](' + link + ')', line)
                    break
    return line


def link_from_keyword(line: str, from_file: Path) -> str:
    """Link study names preceded by 'From ' in headings like '### From genesis-6-sons-of-god Study'"""
    if 'From ' not in line and 'from ' not in line:
        return line
    for study in SORTED_STUDIES:
        if count_exact_unlinked(line, study) > 0:
            link = get_relative_link(from_file, study)
            line = replace_exact_unlinked(line, study, link)
    return line


def process_file(filepath: Path) -> int:
    """Process a single .md file. Returns number of changes made."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    changes = 0

    new_lines = []
    for line in lines:
        original = line
        line = link_table_cells(line, filepath)
        line = link_backtick_paths(line, filepath)
        line = link_source_and_footer(line, filepath)
        line = link_headings(line, filepath)
        line = link_see_also_paths(line, filepath)
        line = link_italics_study_refs(line, filepath)
        line = link_from_keyword(line, filepath)
        if line != original:
            changes += 1
        new_lines.append(line)

    if changes > 0:
        filepath.write_text("".join(new_lines), encoding="utf-8")

    return changes


def main():
    total_changes = 0
    files_changed = 0

    for md_file in sorted(docs_dir.rglob("*.md")):
        changes = process_file(md_file)
        if changes > 0:
            print(f"  {md_file.relative_to(docs_dir)}: {changes} links added")
            total_changes += changes
            files_changed += 1

    print(f"\nTotal: {total_changes} links added across {files_changed} files")


if __name__ == "__main__":
    main()
