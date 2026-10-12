from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET


PLACEHOLDERS = (
    "（中文译文待补）",
    "中文译文待补",
    "[[TODO_TRANSLATE]]",
    "TODO_TRANSLATION",
    "TRANSLATION MISSING",
)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def xml_member(archive: zipfile.ZipFile, member: str, errors: list[str]) -> ET.Element | None:
    try:
        return ET.fromstring(archive.read(member))
    except KeyError:
        errors.append(f"Missing XML resource: {member}")
    except ET.ParseError as exc:
        errors.append(f"Invalid XML in {member}: {exc}")
    return None


def resolve_member(base_file: str, reference: str) -> tuple[str, str]:
    parsed = urlsplit(reference)
    path = unquote(parsed.path)
    target = posixpath.normpath(posixpath.join(posixpath.dirname(base_file), path))
    return target, unquote(parsed.fragment)


def audit_epub(epub_path: Path) -> tuple[list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []
    stats = {"manifest": 0, "spine": 0, "navigation": 0, "xhtml": 0}
    try:
        archive = zipfile.ZipFile(epub_path)
    except (OSError, zipfile.BadZipFile) as exc:
        return [f"Cannot open EPUB: {exc}"], warnings, stats

    with archive:
        names = archive.namelist()
        name_set = set(names)
        if len(names) != len(name_set):
            errors.append("ZIP contains duplicate member names")
        if not names or names[0] != "mimetype":
            errors.append("The first ZIP member must be mimetype")
        elif archive.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            errors.append("The mimetype member must be uncompressed")
        try:
            mimetype = archive.read("mimetype").decode("ascii").strip()
            if mimetype != "application/epub+zip":
                errors.append(f"Unexpected mimetype value: {mimetype!r}")
        except (KeyError, UnicodeDecodeError) as exc:
            errors.append(f"Cannot read mimetype: {exc}")
        corrupt = archive.testzip()
        if corrupt:
            errors.append(f"Corrupt ZIP member: {corrupt}")

        container = xml_member(archive, "META-INF/container.xml", errors)
        if container is None:
            return errors, warnings, stats
        rootfile = next((e for e in container.iter() if local_name(e.tag) == "rootfile"), None)
        if rootfile is None or not rootfile.attrib.get("full-path"):
            errors.append("container.xml has no rootfile full-path")
            return errors, warnings, stats
        opf_path = posixpath.normpath(unquote(rootfile.attrib["full-path"]))
        opf = xml_member(archive, opf_path, errors)
        if opf is None:
            return errors, warnings, stats

        manifest_items = [e for e in opf.iter() if local_name(e.tag) == "item"]
        stats["manifest"] = len(manifest_items)
        manifest_by_id: dict[str, ET.Element] = {}
        manifest_by_path: dict[str, ET.Element] = {}
        for item in manifest_items:
            item_id = item.attrib.get("id", "")
            href = item.attrib.get("href", "")
            if not item_id or item_id in manifest_by_id:
                errors.append(f"Missing or duplicate manifest id: {item_id!r}")
            if item_id:
                manifest_by_id[item_id] = item
            if not href:
                errors.append(f"Manifest item {item_id!r} has no href")
                continue
            target, _ = resolve_member(opf_path, href)
            if target in manifest_by_path:
                errors.append(f"Duplicate manifest href target: {href} -> {target}")
            manifest_by_path[target] = item
            if target not in name_set:
                errors.append(f"Manifest target is missing: {href} -> {target}")

        spine = next((e for e in opf.iter() if local_name(e.tag) == "spine"), None)
        spine_children = list(spine) if spine is not None else []
        spine_refs = [e for e in spine_children if local_name(e.tag) == "itemref"]
        stats["spine"] = len(spine_refs)
        for ref in spine_refs:
            ref_id = ref.attrib.get("idref", "")
            if ref_id not in manifest_by_id:
                errors.append(f"Spine idref is not in manifest: {ref_id!r}")

        navigation_items = [
            item for item in manifest_items
            if item.attrib.get("media-type") == "application/x-dtbncx+xml"
        ]
        for nav_item in navigation_items:
            nav_path, _ = resolve_member(opf_path, nav_item.attrib["href"])
            nav_root = xml_member(archive, nav_path, errors)
            if nav_root is None:
                continue
            points = [e for e in nav_root.iter() if local_name(e.tag) == "navPoint"]
            stats["navigation"] += len(points)
            for point in points:
                content = next((e for e in point.iter() if local_name(e.tag) == "content"), None)
                if content is None or not content.attrib.get("src"):
                    errors.append(f"Navigation point has no content src in {nav_path}")
                    continue
                target, _ = resolve_member(nav_path, content.attrib["src"])
                if target not in name_set:
                    errors.append(f"Navigation target is missing: {nav_path} -> {target}")
        if not navigation_items:
            epub3_nav_items = [
                item for item in manifest_items
                if "nav" in item.attrib.get("properties", "").split()
            ]
            for nav_item in epub3_nav_items:
                nav_path, _ = resolve_member(opf_path, nav_item.attrib["href"])
                nav_root = xml_member(archive, nav_path, errors)
                if nav_root is None:
                    continue
                toc_nodes = [
                    e for e in nav_root.iter()
                    if local_name(e.tag) == "nav"
                    and any(local_name(key) == "type" and value == "toc" for key, value in e.attrib.items())
                ]
                for toc_node in toc_nodes:
                    links = [e for e in toc_node.iter() if local_name(e.tag) == "a"]
                    stats["navigation"] += len(links)
                    for link in links:
                        reference = link.attrib.get("href", "")
                        if not reference:
                            errors.append(f"EPUB 3 TOC link has no href in {nav_path}")
                            continue
                        target, _ = resolve_member(nav_path, reference)
                        if target not in name_set:
                            errors.append(f"Navigation target is missing: {nav_path} -> {target}")
            if not epub3_nav_items:
                warnings.append("No NCX or EPUB 3 navigation document is declared")

        xhtml_members = {
            path for path, item in manifest_by_path.items()
            if item.attrib.get("media-type") in {"application/xhtml+xml", "application/x-dtbook+xml"}
        }
        stats["xhtml"] = len(xhtml_members)
        parsed_docs: dict[str, ET.Element] = {}
        for member in sorted(xhtml_members):
            document = xml_member(archive, member, errors)
            if document is None:
                continue
            parsed_docs[member] = document

        for member, document in parsed_docs.items():
            for element in document.iter():
                for attr in ("href", "src"):
                    reference = element.attrib.get(attr)
                    if not reference:
                        continue
                    parsed = urlsplit(reference)
                    if parsed.scheme or reference.startswith("//") or not parsed.path:
                        continue
                    target, fragment = resolve_member(member, reference)
                    if target not in name_set:
                        errors.append(f"Broken local reference: {member} -> {reference} ({target})")
                        continue
                    if fragment and target in parsed_docs:
                        ids = {e.attrib.get("id") for e in parsed_docs[target].iter()}
                        if fragment not in ids:
                            warnings.append(f"Fragment not found: {member} -> {reference}")

        css_members = [name for name in names if name.lower().endswith(".css")]
        for member in css_members:
            css = archive.read(member).decode("utf-8", errors="replace")
            references = re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", css, flags=re.IGNORECASE)
            references.extend(re.findall(r"@import\s+['\"]([^'\"]+)['\"]", css, flags=re.IGNORECASE))
            for reference in references:
                parsed = urlsplit(reference.strip())
                if parsed.scheme or reference.strip().startswith("//") or not parsed.path:
                    continue
                target, _ = resolve_member(member, reference.strip())
                if target not in name_set:
                    errors.append(f"Broken CSS reference: {member} -> {reference} ({target})")

        for member in names:
            if member.lower().endswith((".xhtml", ".html", ".htm")):
                try:
                    text = archive.read(member).decode("utf-8", errors="replace")
                except KeyError:
                    continue
                for marker in PLACEHOLDERS:
                    if marker.casefold() in text.casefold():
                        errors.append(f"Known translation placeholder in {member}: {marker}")

    return errors, warnings, stats


def block_text(block: object) -> str:
    if isinstance(block, str):
        return block
    if isinstance(block, dict):
        value = block.get("text", "")
        return value if isinstance(value, str) else ""
    return ""


def audit_json_sections(source_dir: Path, translation_dir: Path) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    stats = {"sections": 0, "blocks": 0, "source_chars": 0, "translation_chars": 0}
    source_files = {p.name: p for p in source_dir.glob("*.json")}
    translation_files = {p.name: p for p in translation_dir.glob("*.json")}
    if not source_files:
        return [f"No source JSON sections found in {source_dir}"], stats
    missing = sorted(source_files.keys() - translation_files.keys())
    extra = sorted(translation_files.keys() - source_files.keys())
    for name in missing:
        errors.append(f"Missing translation section: {name}")
    for name in extra:
        errors.append(f"Translation has no matching source section: {name}")

    stats["sections"] = len(source_files)
    for name, source_path in sorted(source_files.items()):
        if name not in translation_files:
            continue
        try:
            source = json.loads(source_path.read_text(encoding="utf-8"))
            translation = json.loads(translation_files[name].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid JSON section {name}: {exc}")
            continue
        source_blocks = source.get("blocks")
        target_blocks = translation.get("blocks")
        if not isinstance(source_blocks, list) or not isinstance(target_blocks, list):
            errors.append(f"Section must contain blocks arrays: {name}")
            continue
        stats["blocks"] += len(source_blocks)
        if len(source_blocks) != len(target_blocks):
            errors.append(f"Block count differs in {name}: source={len(source_blocks)}, target={len(target_blocks)}")
        for index, source_block in enumerate(source_blocks):
            source_text = block_text(source_block)
            stats["source_chars"] += len(source_text)
            if index >= len(target_blocks):
                continue
            target_text = block_text(target_blocks[index])
            stats["translation_chars"] += len(target_text)
            if source_text.strip() and not target_text.strip():
                errors.append(f"Blank translation: {name} block {index}")
            for marker in PLACEHOLDERS:
                if marker.casefold() in target_text.casefold():
                    errors.append(f"Placeholder in translation: {name} block {index}: {marker}")
    return errors, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit an EPUB package and optional aligned translation JSON sections.")
    parser.add_argument("epub", type=Path, help="Built EPUB file")
    parser.add_argument("--source-sections", type=Path, help="Directory of source section JSON files")
    parser.add_argument("--translation-sections", type=Path, help="Directory of translation JSON files")
    args = parser.parse_args()

    if bool(args.source_sections) != bool(args.translation_sections):
        parser.error("--source-sections and --translation-sections must be supplied together")
    errors, warnings, package_stats = audit_epub(args.epub)
    print(f"EPUB: {args.epub.resolve()}")
    print("Package:", ", ".join(f"{key}={value}" for key, value in package_stats.items()))
    if args.source_sections and args.translation_sections:
        json_errors, json_stats = audit_json_sections(args.source_sections, args.translation_sections)
        errors.extend(json_errors)
        print("Sections:", ", ".join(f"{key}={value}" for key, value in json_stats.items()))
    for warning in warnings:
        print("WARN:", warning)
    for error in errors:
        print("FAIL:", error)
    print(f"Result: {'PASS' if not errors else 'FAIL'} ({len(errors)} errors, {len(warnings)} warnings)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
