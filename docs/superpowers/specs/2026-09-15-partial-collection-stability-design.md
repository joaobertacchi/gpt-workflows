# Partial Collection Stability Design

## Goal

Make missing-field collection consistent in ChatGPT Work when a user supplies only some required meeting fields.

## Evidence

For the same input, version `0.3.0` produced two different Work responses:

- one response requested generic notes, discussion points, decisions, and next steps, omitting required labels;
- one response correctly requested only visit type, topics, next steps with responsible people, and follow-up date.

The workflow rule exists, but `SKILL.md` has no concrete partial-collection example. The model therefore follows it inconsistently.

## Change

Add one mandatory example to `SKILL.md` using the observed Beta input:

```text
Reunião com a empresa Beta em 15/09/2026. O contato foi Carla.
```

The example response must request exactly:

- Tipo de reunião/visita;
- Assuntos discutidos;
- Próximos passos, com responsável por cada ação;
- Data para follow up.

The instruction must explicitly prohibit generic requests for more notes and must prohibit optional fields such as decisions, time, duration, objectives, success criteria, and unrelated deadlines.

No schema, report template, date handling, explicit-none behavior, or override behavior changes.

## Packaging

Release the instruction change as version `0.3.1` in both manifests. Keep the single-file runtime architecture and the existing `openai.yaml` invocation metadata.

## Testing

Add a static harness check for the partial-collection example and its four exact labels. The existing deterministic scenario remains responsible for state and missing-field behavior.

After installation through the Personal Plugins Directory, run the same Beta prompt in three separate ChatGPT Work conversations. The scenario passes only if all three responses request exactly the four unresolved categories and none requests completed or optional fields.

Any failure resets the consecutive-pass count and remains recorded as evidence. The other five acceptance scenarios do not need repetition because they already passed in Work on `0.3.0` and their contracts are unchanged.
