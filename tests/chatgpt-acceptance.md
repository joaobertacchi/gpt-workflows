# ChatGPT Acceptance Record

## Baseline Observed On 0.1.1

The pre-correction Codex integration run produced direct evidence of these failures:

- all six initial resource reads targeted missing paths under `skills/relatorio-reuniao/{assets,references}` and required a package-wide recovery search;
- a report generated with `ontem` as the meeting date without resolving or confirming the calendar date; and
- the complete report rendered `Pendências de informação` with `Nenhuma`.

These observations define the regression baseline for version `0.2.0`.

## Build

- Plugin version: 0.3.8
- Marketplace: personal
- Source verification: passed (`python3 scripts/test_flow.py`, 33/33)
- Installed-cache verification: pending for 0.3.8
- Auxiliary Codex loading: pending for 0.3.8

## Local ChatGPT Scenarios

| Scenario | Result | Evidence |
| --- | --- | --- |
| Start checklist | Passed | Work-mode screenshot supplied in chat for version 0.3.0: `SKILL.md` loaded and the response listed only the seven required categories. |
| Complete first turn | Passed | Work-mode screenshot supplied in chat for version 0.3.0: complete report generated immediately with Bruno responsible for the proposal and no pending section. |
| Missing-field follow-up | Passed | Stability gate: 3/3 consecutive Work passes on 0.3.1. |
| Relative-date confirmation | Passed | Work-mode screenshot supplied in chat for version 0.3.0: resolved meeting date to 14/09/2026 and follow-up to 18/09/2026, then waited for confirmation. |
| Explicit no next steps/follow up | Passed | Work-mode screenshot supplied in chat for version 0.3.0: complete report rendered `Nenhum próximo passo definido` and `Não haverá follow up` without pending information. |
| Explicit incomplete override | Passed | Work-mode screenshot supplied in chat for version 0.3.0: incomplete draft used `Não informado` and listed contact, visit type, topics, next steps and follow-up date under `Pendências de informação`. |
| Detailed-note fidelity | Passed | Work screenshots `10.04.32`, `10.04.41` and `10.04.47` show the exact `Registro detalhado` heading and preserve time, duration, attribution, CRM context, WhatsApp evaluation, requested alternatives, plugin proposal, chronology, actions and deadlines. |
| Copyable report boundary | Passed | Work screenshots show one report block with no content after it; the user confirmed its copy control copied only the report. |
| Report-only message | Passed | User-confirmed in chat on 0.3.7: the entire message was exactly the rendered report — no status, no guidance, no code fences; the message copy button copied only the report; behavior described as perfect after install and test. |
| Next-step deadline column | Passed | User-confirmed in chat on 0.3.6: report generated correctly with the rendered `Prazo` column; relative deadline phrases were confirmed as calendar dates shown in the table; the explicit override generated with `Não informado` in the `Prazo` cell as expected. |

## Partial-Collection History On 0.3.0

- Failed: `Screenshot 2026-09-15 at 22.23.18.png` requested generic notes, discussion points, decisions and next steps instead of only the four unresolved required fields.
- Passed on repetition: `Screenshot 2026-09-15 at 22.29.53.png` requested only visit type, topics, owned actions and follow-up date for the same Beta prompt.

This inconsistent behavior requires the separate three-consecutive-pass gate on version `0.3.1`.

## Partial-Collection Stability On 0.3.1

- Run 1: Passed. Image 1 supplied in chat requested exactly visit type, topics, next steps with a responsible person for each action, and follow-up date.
- Run 2: Passed. Image 1 supplied in the following chat turn requested exactly visit type, topics, next steps with a responsible person for each action, and follow-up date.
- Run 3: Passed. Image 1 supplied in the following chat turn requested exactly visit type, topics, next steps with a responsible person for each action, and follow-up date. The trace included path-recovery narration before the compliant final request, but requested no extra report fields.

## Detailed-Report Fidelity Baseline On 0.3.1

- Input: `Screenshot 2026-09-15 at 22.49.07.png` supplied extensive context, chronology, time, duration, attribution, alternatives and implementation details.
- Output: `Screenshot 2026-09-15 at 22.49.21.png` produced a useful summary but omitted or compressed part of those supplied facts and did not isolate the report from operational guidance.

## Detailed-Report Fidelity On 0.3.2

- First attempt failed: screenshots `09.43.48`, `09.43.56` and `09.44.04` preserved the main facts but used `Detalhes fornecidos` and removed explicit attribution from parts of the WhatsApp/alternatives discussion.
- Corrected attempt passed: screenshots `10.04.32`, `10.04.41` and `10.04.47` used `Registro detalhado`, preserved every supplied relevant fact and attribution, resolved and confirmed `segunda-feira` as `14/09/2026`, and kept the report inside the isolated copy block.
- Copy boundary passed: the user confirmed that the block copy control copied only the report.

## Invalid Chat-Surface Attempts

These attempts used the regular Chat surface rather than ChatGPT Work and therefore do not count as plugin acceptance failures:

- Versions 0.2.0-0.2.2, start checklist: `Screenshot 2026-09-15 at 17.21.56.png`, `Screenshot 2026-09-15 at 18.22.08.png`, `Screenshot 2026-09-15 at 18.22.39.png`, and the 0.2.2 retest supplied in chat show generic intake or extra fields.
- Version 0.2.x, complete first turn: `Screenshot 2026-09-15 at 17.21.56.png` shows questions for horário, duração, prazo, follow-up owner/objective and decisão instead of report generation.
- Version 0.2.x, missing-field follow-up: `Screenshot 2026-09-15 at 17.22.52.png` omits the required visit type and requests decisões and generic prazos outside the schema.

## Procedure

Quit and reopen ChatGPT after installing version `0.3.8`. On the ChatGPT homepage, switch from **Chat** to **Work**. For each scenario, start a new Work conversation, type `@`, and select **Documentar Reunião** from the menu. Do not use the regular Chat surface or manually typed mention text as acceptance evidence.

### Start checklist

Send `começar` after the selected mention.

Expected: the first response immediately lists company, meeting date, contacts, one of the four valid types, topics, next steps with a responsible person, and follow-up date.

### Complete first turn

Send:

```text
Empresa Acme. Reunião em 15/09/2026 com Ana. Tipo negociação. Discutimos a renovação do contrato. Bruno enviará a proposta revisada. O follow up será em 18/09/2026.
```

Expected: a complete report in the same response, with no pending-information section.

### Missing-field follow-up

Send:

```text
Reunião com a empresa Beta em 15/09/2026. O contato foi Carla.
```

Expected: asks only for type, topics, next steps with responsible people, and follow-up date. After those answers, it generates without asking again for company, date, or contact.

### Relative-date confirmation

Provide otherwise complete notes using `ontem` for the meeting date and `sexta que vem` for follow up.

Expected: shows both inferred calendar dates and waits for confirmation or correction before generation.

### Explicit no next steps/follow up

Provide all other required fields and state:

```text
Não existem próximos passos e não haverá follow up.
```

Expected: a complete report containing `Nenhum próximo passo definido` and `Não haverá follow up`.

### Explicit incomplete override

Provide only company and meeting date, then send:

```text
Gerar mesmo com pendências.
```

Expected: an incomplete draft with a `Pendências de informação` section listing every unresolved required field.

### Detailed-note fidelity and copy boundary

Send:

```text
A reunião da empresa Acme foi em 13/09/2026 às 13h, durou cerca de uma hora e foi com Luciano. Luciano relatou que o time deveria registrar reuniões com clientes, mas não vem fazendo isso e os registros deveriam entrar no CRM. Durante a conversa ele avaliou WhatsApp e pediu alternativas melhores. Propus um plugin público para ChatGPT. Recebi os requisitos na segunda-feira e fiquei de enviar a prova de conceito até o fim do dia. Luciano instalará, testará em dispositivos móveis e retornará em 17/09/2026.
```

Expected: a readable executive topic summary and a `Registro detalhado` section preserve every supplied fact without invention. Attribution and chronology remain intact, and the detailed record is written as polished professional prose: reproducing the user's dictated or typed sentences near-verbatim records `Failed`. The entire message must be exactly the rendered report: no status, no guidance, no code fences. The message copy button copies only the report. The next-steps table must include the `Prazo` column with a calendar date per action. A draft report carries `Pendências de informação` inside the report.

Record `Passed` or `Failed` and a conversation identifier, transcript, or screenshot in the table. Preserve the exact unexpected response for any failure.

## Post-Publication Android

Not executed before public marketplace publication. Record separately after the customer installs the public listing.
