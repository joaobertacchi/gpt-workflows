# Documentar Reunião

Plugin skills-only para transformar anotações ou relato por voz em um relatório estruturado de reunião ou visita comercial. O nome técnico do pacote é `gpt-workflows`; o nome exibido ao usuário é **Documentar Reunião**.

## Escopo

O workflow:

1. recebe anotações livres;
2. extrai apenas fatos informados pelo usuário;
3. valida todos os campos obrigatórios;
4. pergunta somente pelos campos ausentes, inválidos ou ainda não confirmados;
5. combina respostas de vários turnos;
6. gera o relatório assim que o registro estiver completo; e
7. permite um rascunho incompleto somente mediante override explícito.

O PoC não possui MCP, backend, banco de dados, API externa, CRM, credenciais ou persistência. A entrada de voz depende da experiência normal do ChatGPT para produzir a mensagem do usuário.

## Campos obrigatórios

- empresa (cliente);
- data da reunião ou visita;
- pessoa(s) de contato;
- tipo: `corretiva`, `preventiva`, `desenvolvimento` ou `negociação`;
- assuntos discutidos;
- próximos passos, com responsável por cada ação; e
- data para follow up.

Uma declaração explícita de que não existem próximos passos completa apenas esse campo e é registrada como `Nenhum próximo passo definido`. Uma declaração explícita de que não haverá follow up também é válida e é registrada como `Não haverá follow up`.

Datas relativas, como “ontem” ou “sexta que vem”, são interpretadas a partir da data da conversa. O relatório só é considerado completo depois que o usuário confirma ou corrige as datas interpretadas.

## Estrutura

```text
gpt-workflows/
├── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   └── relatorio-reuniao/
│       ├── SKILL.md
│       └── agents/
│           └── openai.yaml
├── tests/
│   ├── scenarios.json
│   └── chatgpt-acceptance.md
└── scripts/
    └── test_flow.py
```

O contrato completo de runtime está em `SKILL.md`: ativação, intake, campos, validação, workflow, template e orientação de entrega. `tests/` e `scripts/` são recursos exclusivos de desenvolvimento.

## Customização

| Alteração | Arquivo |
| --- | --- |
| Ativação, intake, campos, validação, workflow e saída | `skills/relatorio-reuniao/SKILL.md` |
| Nome exibido e prompt inicial | `skills/relatorio-reuniao/agents/openai.yaml` |

## Validação automatizada

Execute na raiz do plugin:

```bash
python3 scripts/test_flow.py
```

O harness é determinístico e não faz parsing de linguagem natural. Ele lê as seções marcadas no `SKILL.md`; as fixtures fornecem fatos já extraídos e verificam estrutura do pacote, tipos, estados, campos ausentes, confirmação de datas, overrides e conteúdo renderizado.

## Superfícies de aceite

O ChatGPT Work é a superfície principal de aceite local. A aba Chat comum pode mostrar a menção sem carregar as instruções da skill e não deve ser usada como evidência. Na página inicial do ChatGPT, selecione **Work**; depois, digite `@` no composer e selecione **Documentar Reunião** no menu. Texto digitado que apenas se parece com uma menção não comprova que o host anexou a skill.

No Codex, `$relatorio-reuniao` é usado somente como teste auxiliar de carregamento do pacote.

Antes da submissão pública:

1. instale a versão pelo marketplace local;
2. reinicie o ChatGPT;
3. selecione a aba **Work** e abra uma conversa nova;
4. selecione a skill pelo menu `@`; e
5. envie `começar`.

A primeira resposta deve mostrar imediatamente os sete campos obrigatórios. Os demais cenários estão em `tests/chatgpt-acceptance.md`.

O teste no ChatGPT para Android ocorre somente depois que o plugin estiver publicado no marketplace público e o cliente instalar essa versão pública. Android não faz parte do critério pré-submissão.

## Publicação

O marco deste repositório é **pronto para submissão**. Antes de submeter, confirme no portal os dados reais do publicador, site, suporte, privacidade e termos exigidos. Não invente URLs para satisfazer os campos.

Documentação oficial:

- [Build skills](https://developers.openai.com/plugins/build/skills)
- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Agent Skills specification](https://agentskills.io/specification)
