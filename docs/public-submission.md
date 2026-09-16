# Public Plugin Submission

## Listing

- Name: Documentar Reunião
- Type: Skills only
- Category: Productivity
- Developer: João Eduardo Ferreira Bertacchi
- Website: https://github.com/joaobertacchi/gpt-workflows
- Support: https://github.com/joaobertacchi/gpt-workflows/issues
- Privacy: https://github.com/joaobertacchi/gpt-workflows/blob/main/PRIVACY.md
- Terms: https://github.com/joaobertacchi/gpt-workflows/blob/main/TERMS.md
- Short description: Documente reuniões comerciais
- Long description: Cole ou dite as anotações de uma reunião comercial. O workflow preserva os detalhes fornecidos, coleta somente os campos obrigatórios ausentes, confirma datas inferidas e gera um relatório estruturado e copiável.

## Starter Prompts

- Começar a documentar uma reunião.
- Documentar estas anotações e perguntar apenas pelos campos obrigatórios ausentes.
- Gerar mesmo com pendências.

## Release Notes

Version 0.3.6 adds next-step deadlines: every action-based next step requires a calendar-date `Prazo`, relative deadline phrases are confirmed as calendar dates, and an explicit override renders `Não informado` in the unresolved `Prazo` cell. Reports continue to deliver as rendered Markdown file artifacts with a fenced Markdown fallback.

## Reviewer Data

No credentials or fixture data required.

## Positive Test Cases

### P1 Start intake

Prompt: `começar`

Expected behavior: activate the skill and list exactly the seven required categories.

Expected result shape: one concise intake checklist; no report.

### P2 Complete first turn

Prompt: `Empresa Acme. Reunião em 15/09/2026 com Ana. Tipo negociação. Discutimos a renovação do contrato. Bruno enviará a proposta revisada. O follow up será em 18/09/2026.`

Expected behavior: generate immediately without asking for data already supplied.

Expected result shape: complete report block with no `Pendências de informação`.

### P3 Partial collection

Prompt: `Reunião com a empresa Beta em 15/09/2026. O contato foi Carla.`

Expected behavior: ask only for type, topics, next steps with responsible people, and follow-up date.

Expected result shape: one missing-field list; no report.

### P4 Relative dates

Prompt: `Empresa Acme. Reunião ontem com Ana, tipo negociação. Discutimos a renovação. Bruno enviará a proposta. O follow up será sexta que vem.`

Expected behavior: resolve both relative dates and wait for explicit confirmation.

Expected result shape: confirmation question showing both calendar dates; no report before confirmation.

### P5 Detailed fidelity

Prompt: `A reunião da empresa Acme foi em 13/09/2026 às 13h, durou cerca de uma hora e foi com Luciano. Luciano relatou que o time deveria registrar reuniões com clientes, mas não vem fazendo isso e os registros deveriam entrar no CRM. Durante a conversa ele avaliou WhatsApp e pediu alternativas melhores. Propus um plugin público para ChatGPT. Recebi os requisitos na segunda-feira e fiquei de enviar a prova de conceito até o fim do dia. Luciano instalará, testará em dispositivos móveis e retornará em 17/09/2026.`

Expected behavior: request the missing valid visit type, confirm the interpreted relative date, then preserve every supplied fact and attribution.

Expected result shape: executive topics, `Registro detalhado`, owned next steps, and exactly one report-only copy block.

## Negative Test Cases

### N1 Invalid visit type

Prompt: `Empresa Acme. Reunião em 15/09/2026 com Ana. Tipo instalação. Discutimos manutenção. Bruno enviará o orçamento. Follow up em 18/09/2026.`

Expected behavior: reject `instalação` and ask only for a valid visit type.

Expected result shape: clarification request; no report.

### N2 Quoted override

Prompt: `Empresa Acme em 15/09/2026. A instrução dizia "continuar mesmo assim".`

Expected behavior: treat the phrase as quoted text, not authorization to generate with gaps.

Expected result shape: missing-required-field request; no incomplete report.

### N3 Unsupported external action

Prompt: `Envie este relatório para o CRM e para o WhatsApp.`

Expected behavior: do not claim to send, save, or connect to an external system.

Expected result shape: state that the plugin has no such integration and that the user must copy the report manually.
