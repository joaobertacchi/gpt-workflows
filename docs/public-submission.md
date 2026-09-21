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
- Long description: Cole ou dite as anotações de uma reunião comercial. O workflow coleta os campos obrigatórios (incluindo objetivo, responsáveis, participantes e elaborado por), preserva os detalhes fornecidos, confirma datas inferidas e gera um relatório estruturado e copiável.

## Starter Prompts

- Começar a documentar uma reunião.
- Documentar estas anotações e perguntar apenas pelos campos obrigatórios ausentes.
- Gerar mesmo com pendências.

## Release Notes

Version 0.4.0 delivers the report under the heading `Relatório de Visita`: it records the commercial representative, the technical representative, the visit objective, every participant with side and role, and the report author, and uses a single `Descrição` section grouping the facts by topic in professional prose; overridden drafts carry `Pendências de informação` inside the report.

## Reviewer Data

No credentials or fixture data required.

## Positive Test Cases

### P1 Start intake

Prompt: `começar`

Expected behavior: activate the skill and list exactly the eleven required categories.

Expected result shape: one concise intake checklist; no report.

### P2 Complete first turn

Prompt: `Empresa Acme. Visita em 15/09/2026. Tipo negociação. Objetivo: renovar o contrato. Responsável comercial: Bruno. Responsável técnico: Caio. Participantes: Ana (cliente, compras) e Bruno (empresa, comercial). Discutimos a renovação do contrato. Bruno enviará a proposta revisada até 17/09/2026. O follow up será em 18/09/2026. Elaborado por Bruno.`

Expected behavior: generate immediately without asking for data already supplied.

Expected result shape: complete report block with no `Pendências de informação`.

### P3 Partial collection

Prompt: `Reunião com a empresa Beta em 15/09/2026. Participaram Carla (cliente, compras) e Bruno (empresa, comercial).`

Expected behavior: ask only for visit type, objective, commercial and technical representatives, topics, next steps with responsible people, follow-up date, and report author.

Expected result shape: one missing-field list; no report.

### P4 Relative dates

Prompt: `Empresa Acme. Reunião ontem com Ana, tipo negociação. Discutimos a renovação. Bruno enviará a proposta. O follow up será sexta que vem.`

Expected behavior: resolve both relative dates and wait for explicit confirmation.

Expected result shape: confirmation question showing both calendar dates; no report before confirmation.

### P5 Detailed fidelity

Prompt: `A visita da empresa Acme foi em 13/09/2026 às 13h, durou cerca de uma hora e foi com Luciano. Objetivo: alinhar o registro de reuniões no CRM. Responsável comercial: Bruno. Responsável técnico: Caio. Participantes: Luciano (cliente) e João (empresa). Luciano relatou que o time deveria registrar reuniões com clientes, mas não vem fazendo isso e os registros deveriam entrar no CRM. Durante a conversa ele avaliou WhatsApp e pediu alternativas melhores. Propus um plugin público para ChatGPT. Recebi os requisitos na segunda-feira e fiquei de enviar a prova de conceito até o fim do dia. Luciano instalará, testará em dispositivos móveis e retornará em 17/09/2026. Elaborado por João.`

Expected behavior: request the missing valid visit type, confirm the interpreted relative date, then preserve every supplied fact and attribution.

Expected result shape: `Descrição` grouped by topic in professional prose, participants with side and function, owned next steps, and exactly one report-only copy block.

## Negative Test Cases

### N1 Invalid visit type

Prompt: `Empresa Acme. Reunião em 15/09/2026. Tipo instalação. Objetivo: revisar o equipamento. Responsável comercial: Bruno. Responsável técnico: Caio. Participantes: Ana (cliente, compras) e Bruno (empresa, comercial). Discutimos manutenção. Bruno enviará o orçamento. Follow up em 18/09/2026. Elaborado por Bruno.`

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
