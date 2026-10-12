# Quality and EPUB Validation

## Translation Completeness

- Source navigation entries and extracted sections agree in reading order.
- Every non-empty source block has exactly one non-empty target block with the same stable index.
- Headings, epigraphs, captions, quotations, repeated phrases, and ending paragraphs are present.
- No placeholder, truncation, untranslated prose, accidental source-language carryover, or duplicated/missing block remains.
- Compare suspiciously short target blocks with the source manually. Cross-language character ratios are warning signals only, never proof of omission.
- Review proper names, terminology, pronouns, tense/aspect, negation, modality, causality, and recurring concepts across chapter boundaries.
- Preserve notes separately; do not let a model silently erase the user's annotations.

## EPUB Package Checks

The included `scripts/epub_translation_audit.py` checks ZIP integrity, mimetype placement/storage, container and OPF parsing, manifest/spine references, navigation targets when present, XHTML parsing, and local XHTML links. With JSON section directories, it also checks filename coverage, block counts, blanks, and known placeholders.

Before delivery, additionally verify:

1. The source's navigable sections are all represented in the target reading order.
2. Relative stylesheet, image, font, and navigation references resolve from the files that use them.
3. Cover and other required binary assets are retained and declared in the manifest.
4. Poetic line breaks, headings, notes, dialogue, and footnotes have not been flattened by XHTML/CSS generation.
5. The final archive opens in an EPUB reader. Run EPUBCheck when available and report whether it was actually run.

## Evidence Boundaries

Structural validation proves that files and blocks are present and referenced as expected. It does not prove that a translation is semantically complete, stylistically successful, historically accurate, or publication-ready. Do not claim a perfect translation from a green script alone. For high-stakes or publication use, recommend a bilingual human editorial pass on the full work.
