import json
import re
from pathlib import Path
from db.database import AppDatabase


def sync_course_catalog(db: AppDatabase, kb_root: str):
    """Scan KB directory and populate concepts, units, and exercises tables."""
    kb_path = Path(kb_root)
    if not kb_path.exists():
        print(f"KB root not found: {kb_root}, skipping catalog sync")
        return

    # Parse Contents.md for unit structure
    contents_file = kb_path / "Contents.md"
    units = []
    if contents_file.exists():
        units = _parse_contents(contents_file.read_text(encoding="utf-8"))

    # Insert units
    for i, unit in enumerate(units):
        db.execute(
            "INSERT OR REPLACE INTO course_units(id, title, order_index, concept_ids_json) VALUES (?, ?, ?, ?)"
        ).run([unit["id"], unit["title"], i, json.dumps(unit.get("concept_ids", []), ensure_ascii=False)])

    # Scan all markdown files for concepts
    md_files = sorted(kb_path.rglob("*.md"))
    for md_file in md_files:
        if md_file.name == "Contents.md":
            continue
        concept = _parse_concept_md(md_file)
        if concept:
            # Determine unit from path
            unit_id = _infer_unit_id(md_file, kb_path, units)
            db.execute(
                """INSERT OR REPLACE INTO concepts(id, name, unit_id, order_index, content_md, summary_md, prerequisites_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?)"""
            ).run([
                concept["id"], concept["name"], unit_id, concept.get("order_index", 0),
                concept.get("content", ""), concept.get("summary", ""),
                json.dumps(concept.get("prerequisites", []), ensure_ascii=False)
            ])

    db.conn.commit()
    concept_count = db.execute("SELECT COUNT(*) as cnt FROM concepts").get()
    unit_count = db.execute("SELECT COUNT(*) as cnt FROM course_units").get()
    print(f"Course catalog synced: {concept_count['cnt']} concepts, {unit_count['cnt']} units")


def _parse_contents(text: str) -> list[dict]:
    """Parse Contents.md to extract unit hierarchy."""
    units = []
    current_unit = None
    for line in text.split("\n"):
        unit_match = re.match(r"^##\s+Unit\s*(\d+)[：:]\s*(.+)", line, re.IGNORECASE)
        if unit_match:
            if current_unit:
                units.append(current_unit)
            current_unit = {
                "id": f"unit_{unit_match.group(1).zfill(2)}",
                "title": unit_match.group(2).strip(),
                "concept_ids": [],
            }
        elif current_unit and re.match(r"^-\s+\[.+\]\((.+)\)", line):
            concept_match = re.match(r"^-\s+\[.+\]\((.+)\)", line)
            if concept_match:
                concept_id = _slugify(Path(concept_match.group(1)).stem)
                current_unit["concept_ids"].append(concept_id)
    if current_unit:
        units.append(current_unit)
    return units


def _parse_concept_md(file_path: Path) -> dict | None:
    """Parse a concept markdown file to extract metadata."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception:
        return None

    # Extract title from first heading
    title_match = re.match(r"^#\s+(.+)", text)
    if not title_match:
        return None

    name = title_match.group(1).strip()
    concept_id = _slugify(file_path.stem)

    # Extract summary (first paragraph after title)
    lines = text.split("\n")
    summary_lines = []
    in_summary = False
    for line in lines[1:]:
        stripped = line.strip()
        if stripped.startswith("##"):
            break
        if stripped and not in_summary:
            in_summary = True
        if in_summary:
            summary_lines.append(stripped)

    summary = " ".join(summary_lines[:5])

    # Extract prerequisites
    prerequisites = []
    prereq_match = re.search(r"前置[要求条件].*?[：:]\s*(.+)", text)
    if prereq_match:
        prerequisites = [p.strip() for p in prereq_match.group(1).split("、") if p.strip()]

    return {
        "id": concept_id,
        "name": name,
        "content": text,
        "summary": summary,
        "prerequisites": prerequisites,
        "order_index": 0,
    }


def _infer_unit_id(file_path: Path, kb_root: Path, units: list[dict]) -> str | None:
    """Infer which unit a concept file belongs to."""
    try:
        rel = file_path.relative_to(kb_root)
        parts = rel.parts
        if len(parts) > 1:
            for unit in units:
                if unit["title"] in parts[0] or parts[0] in unit["title"]:
                    return unit["id"]
            # Try naming convention: 01_Introduction etc.
            dir_name = parts[0]
            match = re.match(r"^(\d+)", dir_name)
            if match:
                return f"unit_{match.group(1).zfill(2)}"
    except ValueError:
        pass
    return None


def _slugify(text: str) -> str:
    """Convert text to a safe identifier."""
    # Remove special chars, replace spaces with underscores
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "_", text)
    return text.strip("_")
