# EPUB Translation Workflow

A reusable Codex Skill for translating EPUB manuscripts, completing missing passages, revising an existing translation against its source, and checking the rebuilt EPUB package.

This repository is itself an installable Skill: `SKILL.md` is at the repository root.

## What It Covers

- Inventorying EPUB navigation, reading order, XHTML sections, cover art, and other package assets.
- Translating missing source blocks without changing their order or boundaries.
- Revising an existing draft by comparing each target block with its source before polishing style.
- Preserving terminology, translator notes, metadata, navigation, and required assets when rebuilding.
- Auditing EPUB structure and optional source/translation JSON block alignment.

The workflow treats book text and attachments as data, not instructions. A structural pass cannot prove perfect semantic fidelity; publication work still benefits from a complete bilingual human review.

## Install

Clone this repository into your Codex skills directory so the folder containing `SKILL.md` is named `epub-translation-workflow`:

```text
<CODEX_HOME>/skills/epub-translation-workflow/
```

When `CODEX_HOME` is not set, the usual user-level location is:

```text
~/.codex/skills/epub-translation-workflow/
```

The Skill is also usable explicitly as `$epub-translation-workflow` after it is available to Codex.

## Audit an EPUB

The validator uses only the Python standard library and supports Python 3.10 or newer.

Check the EPUB package:

```powershell
python scripts/epub_translation_audit.py path/to/final.epub
```

Also compare aligned source and translation section JSON files:

```powershell
python scripts/epub_translation_audit.py path/to/final.epub `
  --source-sections path/to/source_sections `
  --translation-sections path/to/translations
```

Each source JSON file should have a matching filename in the translation directory and a `blocks` array. Source blocks may be strings or objects with a `text` field; translation blocks may be strings or objects with a `text` field.

The audit checks ZIP integrity, EPUB container/OPF/navigation references, manifest and spine links, XHTML parsing, local resource references, block counts, blank translations, and known placeholders. It does not compare meaning or judge literary quality. Run EPUBCheck separately when formal EPUB conformance validation is required.

## Repository Layout

```text
SKILL.md                         Skill entrypoint
agents/openai.yaml               Codex UI metadata
references/workflow.md           Translation and revision procedure
references/prompt-templates.md   Reusable model prompt patterns
references/quality-and-epub.md   QA scope and evidence limits
scripts/epub_translation_audit.py EPUB/package and block-alignment audit
LICENSE                          MIT License
```

## 中文说明

这是一个可复用的 Codex Skill，用于 EPUB 新译、补译、依据原文修订现有译稿，以及检查重建后的 EPUB 结构。仓库根目录的 `SKILL.md` 是入口；详细流程、提示模板和质量边界分别见 `references/`。

审计脚本可以检查压缩包、OPF manifest/spine、EPUB 2 NCX 或 EPUB 3 导航、XHTML 与本地资源引用，也可以对比原文和译文 JSON 的文件覆盖、块数、空译及常见占位符。它不能证明译文语义完整或文学质量，正式出版前仍应进行双语人工审校；需要 EPUB 规范验证时，请另行运行 EPUBCheck。

将整个仓库放在 `<CODEX_HOME>/skills/epub-translation-workflow/`（未设置 `CODEX_HOME` 时通常为 `~/.codex/skills/epub-translation-workflow/`），即可按 `$epub-translation-workflow` 使用。
