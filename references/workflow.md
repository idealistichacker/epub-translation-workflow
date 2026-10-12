# Translation and Revision Workflow

## 1. Inventory Before Editing

- Confirm the user-provided source EPUB, target language, existing translation, desired output path, and whether notes or bilingual content should remain.
- Inspect the ZIP container, OPF manifest/spine, NCX or EPUB 3 navigation, and XHTML resources. Do not infer completeness from filenames alone.
- Extract every navigable section in reading order. Preserve an explicit source path, section label, block index, tag, and text for each unit.
- Compare the extracted source against the source XHTML by section and block. This catches extraction omissions before translation starts.
- Record a terminology list from the current draft and user instructions. Mark uncertain choices instead of silently normalizing them.

## 2. Translate Missing Content

Use the source as the sole authority. Translate every non-empty block, including headings, epigraphs, captions, and other navigable text. Keep one output string per input block and keep translator notes in a separate field.

Request complete translation rather than summary. Preserve meaning, tone, chronology, ambiguity, register, quotations, numbers, and paragraph order. Do not omit, censor, embellish, or add interpretations. Add only short factual notes that materially help the target reader, and do not use notes to replace body text.

## 3. Revise an Existing Draft

Provide the source and the matching draft together, aligned by stable block index. The source controls meaning; the draft is evidence of the user's current terminology and style, not evidence that a sentence is complete.

For each block, check sentence-level coverage, modifiers, negation, modality, cause and effect, time/place, agency, pronoun reference, quotations, numbers, and rhetorical repetition. Then edit for target-language grammar, cadence, register, and consistency without changing the source's force.

Use modest batches bounded by both block count and source size. Keep a long paragraph intact when practical; if it must be split, retain sub-block IDs and reassemble in order. Include enough neighboring context or a glossary to resolve references, but do not exceed the model's reliable output capacity.

## 4. Checkpointing and Recovery

- Back up the complete draft set before the first write. Never treat the backup as the working output.
- Validate each response before accepting it: strict parse, exact item count, correct types, non-empty output for non-empty source, no known placeholder, and no truncation signal.
- Retry only bounded transient or validation failures. On repeated failure, stop and preserve completed work; do not fill the gap with a guessed paragraph.
- Write a whole section only after all its batches pass. Prefer a temporary file plus atomic rename when implementing a reusable pipeline.
- Preserve translator notes and editorial metadata unless the user requests their removal or their factual accuracy is being explicitly revised.

## 5. Terminology and Voice

Maintain a compact glossary with the source form, preferred target form, and rationale when needed. Apply it consistently, but do not force a stored choice where context changes the meaning. Preserve distinctions in names, institutions, technical terms, recurring concepts, and narrative voice.

Literary polish means clearer, more idiomatic target-language prose without flattening deliberate repetition, ambiguity, irony, vulgarity, or abruptness. Do not make every sentence ornate; match the local register.

## 6. Delivery

Build to a new output file rather than replacing the source or the only draft. Preserve reading order, navigation, cover, images, metadata, and relative links. Run package and alignment checks before delivery. State what was checked, any unavailable EPUBCheck result, and the limits of automated fidelity review.
