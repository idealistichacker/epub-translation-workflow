# Prompt Templates

Adapt the language pair, glossary, output schema, and house style to the job. Keep source text and draft text in separately labelled fields.

## Translation Pass

```text
Translate the supplied source blocks into [target language]. The source is authoritative.
Preserve every sentence's meaning, tone, chronology, ambiguity, register, names, numbers,
quotations, and paragraph order. Do not summarize, omit, censor, explain, or add content.
Translate every non-empty block, including headings. Keep block boundaries and return exactly
one translation string for each input index in the same order. Put optional factual reader notes
in a separate notes array; never use notes to replace translation.

Return strict JSON only:
{"blocks":["..."],"notes":[]}
```

## Source-Grounded Revision Pass

```text
The source text is authoritative. The existing target-language text is a draft, not a constraint.
Compare each source block with its matching draft block sentence by sentence. Restore any omitted
meaning, qualification, relation, action, quotation, number, or repetition; correct mistranslation
and grammar; then polish for idiomatic literary prose while preserving the source's voice and force.
Do not summarize, censor, embellish, or merge blocks. Keep indices and output count exactly equal
to the input. Return strict JSON only: {"blocks":["..."],"notes":[]}
```

## Suggested Request Shape

```json
{
  "section": "chapter label",
  "glossary": [{"source": "Name", "target": "Preferred rendering"}],
  "blocks": [
    {"index": 0, "tag": "h1", "source": "...", "draft": "..."},
    {"index": 1, "tag": "p", "source": "...", "draft": "..."}
  ]
}
```

For source-only translation, omit `draft`. Keep the machine-readable result limited to fields that the pipeline validates. Request editorial commentary separately if the user needs a change log.
