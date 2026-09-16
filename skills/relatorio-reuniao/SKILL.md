---
name: relatorio-reuniao
description: Use when the user selects @Documentar Reunião, invokes relatorio-reuniao, or asks to documentar, registrar or gerar relatório de reunião or visita comercial from text or voice notes.
---

# Documentar Reunião

Create one structured commercial meeting or visit report from facts supplied by the user. Ask only for unresolved required information. Never invent business facts or request fields outside this contract.

## Activation

Selecting `Documentar Reunião`, invoking `$relatorio-reuniao`, or making a matching explicit request starts a new active report. Text after activation is the first payload.

If the payload is empty or only `começar`, `iniciar`, or `start`, respond with exactly the intake below and stop. Do not paraphrase it or add fields.

<!-- INTAKE_START -->
Vamos montar o relatório da reunião/visita.

Você pode falar naturalmente, usar a entrada de voz ou colar suas anotações — não precisa seguir uma ordem. Inclua:

- empresa (cliente);
- data da reunião/visita;
- pessoa(s) de contato;
- tipo de reunião/visita: corretiva, preventiva, desenvolvimento ou negociação;
- assuntos discutidos;
- próximos passos, com o responsável por cada ação;
- data para follow up.

Depois eu verifico o que estiver faltando e pergunto somente pelos campos ausentes. Se preferir gerar o relatório mesmo com informações pendentes, diga explicitamente: “continuar mesmo assim”.

Se você usar datas relativas, como “ontem” ou “sexta que vem”, eu mostrarei as datas interpretadas para sua confirmação.
<!-- INTAKE_END -->

## Required Record

Only these seven fields are required. Time, duration, objective, decisions, success criteria, and unrelated deadlines are not required and must not be requested.

<!-- FIELD_SCHEMA_START -->
```json
{
  "missingValue": "Não informado",
  "fields": [
    {"id":"company","label":"Empresa (cliente)","required":true,"type":"string","validation":{"kind":"non_empty"}},
    {"id":"meeting_date","label":"Data da reunião/visita","required":true,"type":"string","validation":{"kind":"absolute_date","formats":["YYYY-MM-DD","DD/MM/YYYY"]}},
    {"id":"contacts","label":"Pessoa(s) de contato","required":true,"type":"array<string>","validation":{"kind":"non_empty_list"}},
    {"id":"visit_type","label":"Tipo de reunião/visita","required":true,"type":"string","allowedValues":["corretiva","preventiva","desenvolvimento","negociação"],"validation":{"kind":"enum","caseInsensitive":true}},
    {"id":"topics_discussed","label":"Assuntos discutidos","required":true,"type":"array<string>","validation":{"kind":"non_empty_list"}},
    {"id":"provided_details","label":"Registro detalhado","required":false,"type":"array<string>","validation":{"kind":"non_empty_list"}},
    {"id":"next_steps","label":"Próximos passos","required":true,"type":"array<object>","itemFields":["action","responsible"],"itemFieldTypes":{"action":"string","responsible":"string"},"allowExplicitNone":true,"explicitNoneValue":"Nenhum próximo passo definido","validation":{"kind":"non_empty_list"}},
    {"id":"follow_up_date","label":"Data para follow up","required":true,"type":"string","allowExplicitNone":true,"explicitNoneValue":"Não haverá follow up","validation":{"kind":"absolute_date","formats":["YYYY-MM-DD","DD/MM/YYYY"]}}
  ]
}
```
<!-- FIELD_SCHEMA_END -->

<!-- VALIDATION_RULES_START -->
```json
{
  "missingSentinels":["não informado","nao informado","não sei","nao sei","desconhecido","unknown","n/a","não disponível","nao disponivel","omitido"],
  "explicitOverridePhrases":["continuar mesmo assim","continuar com pendências","continuar com pendencias","gerar mesmo com pendências","gerar mesmo com pendencias","pode gerar mesmo faltando","proceed anyway","continue anyway","generate anyway"],
  "explicitNegativeAnswers":{"next_steps":["não existem próximos passos","não há próximos passos","nenhum próximo passo"],"follow_up_date":["não haverá follow up","não será feito follow up","sem follow up"]}
}
```
<!-- VALIDATION_RULES_END -->

## Workflow

1. Extract only user-provided facts into the active record. Merge later answers. A clear correction replaces the prior value; an ambiguous conflict triggers one question about only that field.
2. Validate all seven fields after every turn. Ask one concise question containing only missing, invalid, conflicting, or unconfirmed required labels.
3. Accept `visit_type` only as `corretiva`, `preventiva`, `desenvolvimento`, or `negociação` after normalization.
4. Require every next-step action to have a responsible person. A direct statement that no next steps exist becomes `Nenhum próximo passo definido`.
5. A direct statement that no follow up will occur becomes `Não haverá follow up`. Negative answers complete no other field.
6. Resolve relative meeting and follow-up dates from the conversation date. Show every calendar date and wait for confirmation or correction.
7. Generate immediately when all fields are valid and inferred dates are confirmed. Do not ask for permission.
8. Generate with gaps only after affirmative use of a configured override phrase. Quoted, hypothetical, ambiguous, or negated mentions are not overrides.
9. A correction after generation reopens validation and regenerates without repeating intake.

## Detail Fidelity

- Preserve every relevant user-supplied fact. Store context and specificity behind topic labels in `provided_details`; a concise topic does not replace its supporting facts.
- Relevant supplied facts include context, chronology, problems, evidence, current processes, alternatives, decisions, restrictions, channels, deadlines, times, durations and expectations.
- Improve grammar and remove repetition or speech disfluencies, but preserve names, attribution, dates, times, quantities, relationships and temporal order. Never replace distinct facts with a lossy generalization or invent an interpretation.
- Do not ask for `provided_details`. When absent, continue using only the seven required fields.
- A correction replaces affected detail facts while preserving unrelated facts.

For rich notes, use the exact `Registro detalhado` heading and retain the actor attached to every attributed fact. Do not rename the section from the field label or turn attributed statements into actorless summaries.

<!-- DETAIL_FIDELITY_EXAMPLE_START -->
User facts:

`Luciano relatou que o time não registra as reuniões no CRM. Luciano avaliou o WhatsApp e Luciano pediu alternativas melhores. Eu propus um plugin público para ChatGPT.`

Required detailed section excerpt:

## Registro detalhado

- Luciano relatou que o time não vem registrando as reuniões no CRM.
- Luciano avaliou uma solução baseada em WhatsApp.
- Luciano pediu alternativas melhores para o registro das reuniões.
- Eu propus um plugin público para ChatGPT.

Do not remove or change the actor attached to any of these facts.
<!-- DETAIL_FIDELITY_EXAMPLE_END -->

## Missing-Field Response

When validation finds unresolved fields, enumerate every unresolved required label and no completed or optional field. Do not ask for generic notes or say only “tell me the rest.” Do not request decisions, time, duration, objectives, success criteria, or unrelated deadlines.

<!-- PARTIAL_EXAMPLE_START -->
User:

`Reunião com a empresa Beta em 15/09/2026. O contato foi Carla.`

Required response:

Para completar o relatório, informe:

- Tipo de reunião/visita;
- Assuntos discutidos;
- Próximos passos, com responsável por cada ação;
- Data para follow up.

Do not ask for generic notes. Do not request decisions. Do not repeat Empresa, Data da reunião/visita, or Pessoa(s) de contato because the user already supplied them.
<!-- PARTIAL_EXAMPLE_END -->

## Report Output

Render this template in order. Render contacts as comma-separated names, topics as bullets, and action-based next steps as a table with `Ação` and `Responsável` columns.

For every complete, overridden or regenerated report, place status and operational guidance before exactly one fenced `markdown` block. Put only the report inside that block and emit nothing after its closing fence. `Pendências de informação`, when applicable, belongs inside the report block.

<!-- REPORT_TEMPLATE_START -->
# Relatório de reunião/visita

**Empresa (cliente):** {{company}}  
**Data da reunião/visita:** {{meeting_date}}  
**Pessoa(s) de contato:** {{contacts}}  
**Tipo de reunião/visita:** {{visit_type}}  
**Data para follow up:** {{follow_up_date}}

## Assuntos discutidos

{{topics_discussed}}

{{provided_details_section}}

## Próximos passos

{{next_steps}}
<!-- REPORT_TEMPLATE_END -->

Before a complete report block, output this guidance. Do not include a pending section or missing placeholder in the report.

<!-- COMPLETE_GUIDANCE_START -->
✅ **Todas as informações necessárias foram preenchidas.**

O relatório está pronto para ser revisado e compartilhado. Revise nomes, datas e responsáveis; depois, copie o conteúdo do relatório para um e-mail, WhatsApp, CRM ou registro interno.
<!-- COMPLETE_GUIDANCE_END -->

For an overridden report, use `Não informado` for every unresolved field and append `## Pendências de informação` with every unresolved label inside the report. Before the report block, output this guidance:

<!-- INCOMPLETE_GUIDANCE_START -->
⚠️ **O relatório foi gerado como rascunho com informações pendentes.**

O rascunho deve ser completado e revisado antes de ser compartilhado como versão final. O plugin não envia mensagens nem grava o relatório em outros sistemas.
<!-- INCOMPLETE_GUIDANCE_END -->

## Common Mistakes

- Do not replace the intake with a generic meeting questionnaire.
- Do not request time, duration, decisions, success criteria, or unrelated deadlines.
- Do not preserve a relative date as final without confirmation.
- Do not treat a quoted, hypothetical, ambiguous, or negated override phrase as permission.
- Do not show `Pendências de informação` in a complete report.

This skills-only plugin has no tools, storage, transcription service, backend, database, external API, or CRM connection.
