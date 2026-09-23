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

## 3. Use texto ou voz

Você pode digitar, colar anotações ou usar a entrada de voz disponível no ChatGPT. A entrada de voz é um recurso do próprio ChatGPT; o plugin recebe o conteúdo fornecido na conversa e não possui um gravador ou serviço próprio de transcrição.

Exemplo de relato completo:

> Visitei o cliente Acme em 15/09/2026. A natureza foi Comercial e o tipo foi negociação. O objetivo foi renovar o contrato. Bruno foi o responsável comercial e Caio, o responsável técnico. Participaram Ana Souza (cliente, compras) e Bruno (empresa, comercial). Discutimos a renovação do contrato e a revisão dos valores. Bruno enviará a proposta revisada até 17/09/2026, e Ana analisará a proposta até 19/09/2026. Elaborado por Bruno.

## 4. Responda somente ao que estiver faltando

Se alguma informação obrigatória estiver ausente ou inválida, o plugin solicitará apenas os campos que ainda precisam ser completados. Você pode responder normalmente, em uma ou mais mensagens.

Se uma data relativa for usada para a visita ou para o prazo de uma ação, como “ontem” ou “sexta que vem”, o plugin mostrará a data que interpretou e pedirá sua confirmação antes de gerar o relatório.

Caso não existam próximos passos, informe isso explicitamente:

- `Não existem próximos passos.`

## 5. Revise e copie o relatório

Assim que todas as informações obrigatórias estiverem válidas, o plugin gera automaticamente um relatório com:

- cliente, data, natureza, tipo, objetivo e responsáveis comercial e técnico;
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
