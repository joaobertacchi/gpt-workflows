# Como usar o Documentar Reunião

O **Documentar Reunião** transforma anotações ou um relato por voz em um relatório estruturado de reunião ou visita comercial. Ele verifica se as informações essenciais foram fornecidas, pergunta somente o que estiver faltando e entrega um relatório pronto para copiar.

## 1. Instale o plugin

1. Abra a página do [Documentar Reunião no ChatGPT](https://chatgpt.com/plugins/plugins_6aaadbf9b0608191820ae6351956faab).
2. Selecione a opção para instalar o plugin.
3. Depois da instalação, inicie uma nova conversa no ChatGPT.

O plugin pode ser usado no ChatGPT pela web e nos aplicativos para computador ou celular, de acordo com a disponibilidade de plugins para a sua conta.

## 2. Inicie um relatório

Em uma nova conversa, digite `@` e selecione **Documentar Reunião** e envie. Você receberá instruções detalhadas. Pressione o botão microfone e fale sobre reunião.

Você não precisa seguir uma ordem nem preencher um formulário. Fale naturalmente e inclua, quando possível:

- empresa ou cliente;
- data da reunião ou visita;
- objetivo da visita;
- responsável comercial e responsável técnico (ou a declaração de que não houve);
- participantes, com o lado (cliente ou empresa) e a função de cada um;
- tipo da reunião ou visita: `corretiva`, `preventiva`, `desenvolvimento` ou `negociação`;
- assuntos discutidos;
- próximos passos, com responsável e prazo de cada ação;
- data para follow up; e
- elaborado por.

## 3. Use texto ou voz

Você pode digitar, colar anotações ou usar a entrada de voz disponível no ChatGPT. A entrada de voz é um recurso do próprio ChatGPT; o plugin recebe o conteúdo fornecido na conversa e não possui um gravador ou serviço próprio de transcrição.

Exemplo de relato completo:

> Visitei a empresa Acme em 15/09/2026 e conversei com Ana Souza. Foi uma visita de negociação. Discutimos a renovação do contrato e a revisão dos valores. Bruno enviará a proposta revisada até 17/09/2026. Ana analisará a proposta até 19/09/2026. O follow up será em 22/09/2026.

## 4. Responda somente ao que estiver faltando

Se alguma informação obrigatória estiver ausente ou inválida, o plugin solicitará apenas os campos que ainda precisam ser completados. Você pode responder normalmente, em uma ou mais mensagens.

Se uma data relativa for usada, como “ontem” ou “sexta que vem”, o plugin mostrará a data que interpretou e pedirá sua confirmação antes de gerar o relatório.

Caso não existam próximos passos ou não deva haver follow up, informe isso explicitamente, por exemplo:

- `Não existem próximos passos.`
- `Não haverá follow up.`

## 5. Revise e copie o relatório

Assim que todas as informações obrigatórias estiverem válidas, o plugin gera automaticamente um relatório com:

- identificação da empresa, data, tipo, objetivo, responsáveis comercial e técnico, e data para follow up;
- participantes, com o lado e a função de cada um;
- descrição dos assuntos discutidos agrupada por tópico, reescrita em linguagem profissional sem inventar nenhuma informação;
- próximos passos, responsáveis e prazos; e
- linha de elaborado por.

Revise nomes, datas, responsabilidades e demais informações antes de compartilhar ou registrar o conteúdo no sistema da empresa. Se encontrar algum erro, informe a correção na mesma conversa; o plugin atualizará e gerará novamente o relatório.

## Gerar um rascunho incompleto

Se quiser gerar o relatório mesmo sem todas as informações obrigatórias, use uma instrução explícita como:

> Continuar mesmo assim.

O relatório indicará os dados não informados e incluirá uma seção com as pendências.

## O que o plugin não faz

O Documentar Reunião não possui integração com CRM, WhatsApp ou outros sistemas externos. Ele também não mantém banco de dados, não possui servidor próprio e não envia o relatório automaticamente. Depois de revisar o resultado, você deve copiá-lo para o destino desejado.

## Suporte e sugestões

Para relatar um problema ou sugerir uma melhoria, [abra uma issue no GitHub](https://github.com/joaobertacchi/gpt-workflows/issues).

O código-fonte e a documentação técnica estão disponíveis no [repositório do projeto](https://github.com/joaobertacchi/gpt-workflows).

## Referência sobre plugins

Consulte também a [documentação oficial de plugins do ChatGPT](https://learn.chatgpt.com/docs/plugins).
