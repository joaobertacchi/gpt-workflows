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

## Como usar

- [Instale o Documentar Reunião no ChatGPT](https://chatgpt.com/plugins/plugins_6aaadbf9b0608191820ae6351956faab).
- Consulte o [guia completo de instalação e uso](INSTRUCOES_DE_USO.md).

## Campos obrigatórios

- cliente;
- data;
- natureza da visita: `Comercial`, `Técnica` ou `Técnica Comercial`;
- tipo de visita: `corretiva`, `preventiva`, `desenvolvimento` ou `negociação`;
- objetivo da visita;
- responsável comercial;
- responsável técnico (ou a declaração de que não houve);
- participantes, com o lado (cliente ou empresa) e a função de cada um;
- assuntos discutidos;
- próximos passos, com responsável e prazo de cada ação; e
- elaborado por.

Uma declaração explícita de que não existem próximos passos completa apenas esse campo e é registrada como `Nenhum próximo passo definido`.

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
    ├── build_public_zip.sh
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

A primeira resposta deve mostrar imediatamente os onze campos obrigatórios. Os demais cenários estão em `tests/chatgpt-acceptance.md`.

O teste no ChatGPT para Android ocorre somente depois que o plugin estiver publicado no marketplace público e o cliente instalar essa versão pública. Android não faz parte do critério pré-submissão.

## Publicação

Gere o pacote público na raiz do repositório:

```bash
./scripts/build_public_zip.sh
```

O script executa a validação automatizada e cria `dist/documentar-reuniao-0.5.0.zip` contendo somente o manifest, o logo e os dois arquivos da skill. Esse ZIP é o arquivo enviado em **Create plugin → Skills only**.

O relatório é entregue como a mensagem inteira da conversa, renderizado em Markdown, sem orientações ou cercas de código; o botão de cópia da mensagem copia apenas o relatório.

A tabela de próximos passos inclui a coluna `Prazo` com a data de cada ação; passos gerados por override sem prazo exibem `Não informado`.

O pacote usa estes recursos públicos obrigatórios:

- [Repositório e website](https://github.com/joaobertacchi/gpt-workflows)
- [Suporte](https://github.com/joaobertacchi/gpt-workflows/issues)
- [Política de privacidade](PRIVACY.md)
- [Termos de uso](TERMS.md)
- [Material para submissão](docs/public-submission.md)

Após confirmar a identidade verificada do publicador e a permissão **Apps Management: Write**, envie o pacote como **Skills only** pelo [portal de submissão](https://platform.openai.com/plugins).

Documentação oficial:

- [Build skills](https://developers.openai.com/plugins/build/skills)
- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Agent Skills specification](https://agentskills.io/specification)
