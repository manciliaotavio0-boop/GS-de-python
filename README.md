# Citizen Assist AI

Assistente de terminal, feito em Python, que orienta **pessoas idosas** sobre saúde, transporte, direitos e benefícios, usando só informações de fontes oficiais, mostrando a fonte e sem coletar dados pessoais.

> Global Solution 2026.2 – Pensamento Computacional e Automação com Python (FIAP) – desafio CitizenTech

## Integrantes

| Nome | RM |
|------|----|
| Otávio Mancilia | 570225 |
| Wesley Marques | 573915 |
| Tiago Muhlmann | 569569 |

## Público e problema

**Público:** pessoas com 60 anos ou mais, e familiares que ajudam essas pessoas.

**Problema:** a informação sobre Cartão SUS, vacina, transporte gratuito, BPC ou prova de vida existe, mas está espalhada, em linguagem técnica e misturada com páginas e mensagens falsas. Idosos são alvo frequente de golpes que usam o nome do INSS. O assistente responde em linguagem simples, aponta a fonte oficial e avisa que **não é um canal oficial**.

## ODS relacionados

- **ODS 3 – Saúde e bem-estar** (Cartão SUS, vacinação, Farmácia Popular)
- **ODS 10 – Redução das desigualdades** (gratuidades, BPC, atendimento prioritário)
- **ODS 16 – Paz, justiça e instituições eficazes** (acesso à informação, denúncia de violência, combate a golpes)

## Como executar

Requisitos: Python 3.8 ou superior. Não usa bibliotecas externas.

```bash
git clone <link-do-repositorio>
cd citizen-assist-ai
python main.py
```

**No PyCharm:** abra a **pasta** `citizen-assist-ai` (File > Open, não só um arquivo), abra o `main.py` e clique em **Run**. O menu aparece na janela de baixo: clique nela para digitar as respostas.

**No Windows**, se `python` não for reconhecido, use `py main.py`.

Menu: `1` fazer uma pergunta · `2` navegar por categorias · `3` ver indicadores · `4` exportar CSV · `0` sair (pede a nota de facilidade de 1 a 5).

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py               # cria os objetos e inicia o menu
├── orientacao.py         # classe Orientacao
├── base_conhecimento.py  # classe BaseConhecimento (normalizar, pontuar, buscar)
├── assistente.py         # classe Assistente (atendimento, histórico, indicadores, CSV)
└── data/
    ├── base_conhecimento.json   # 12 orientações, 4 categorias
    ├── historico.json           # um dicionário por atendimento
    └── atendimentos.csv         # exportado com csv.DictWriter
```

**Composição:** `Assistente` tem uma `BaseConhecimento`, que tem uma lista de objetos `Orientacao`.

## Regra de pontuação

A pergunta e o texto das orientações são normalizados (minúsculas, sem acentos, sem pontuação) antes de comparar.

| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação que aparece na pergunta | +3 |
| Palavra da pergunta (4 letras ou mais) que aparece no título | +1 |

| Melhor pontuação | Resultado |
|------------------|-----------|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| Menos de 3 | "Não encontrei": sugere outras palavras ou as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)`, da maior para a menor pontuação (empate: menor `id` primeiro). O assistente mostra a melhor orientação e até duas alternativas com 3 pontos ou mais.

**Ajustes feitos (decisões da equipe):**

1. **Palavras ignoradas no título:** palavras comuns como "como", "para", "anos" e "mais" não ganham o ponto do título. Sem isso, perguntas genéricas somariam pontos por coincidência.
2. **Palavras-chave não repetidas:** se duas palavras-chave ficam iguais depois de normalizadas, valem uma vez só.
3. **Palavra inteira:** a busca procura palavras inteiras (`" sus "`), então "sus" não casa com "susto".

Exemplo: "Como faço o cartão do SUS?" → `cartao do sus` (+3) + `sus` (+3) + `cartao` no título (+1) = **7 pontos, confiança ALTA**.

## Regras de atendimento

- **Entradas inválidas** (letras, vazio, número fora da faixa, s/n inválido) nunca encerram o programa.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Pergunta com 8 ou mais dígitos, ou com `@`, é recusada e **não é registrada**.
- **Transparência:** toda orientação mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** JSON da base ausente ou corrompido não trava o programa; histórico corrompido é guardado como `historico.json.corrompido` e um novo é iniciado.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: data, sessão, origem (`pergunta` ou `categoria`), pergunta, id da orientação, se encontrou, se ajudou, tentativas, tempo em segundos (`time.time()`) e nota de facilidade (preenchida ao sair).

Indicadores exibidos: resposta encontrada (%), taxa de acerto/ajudou (%), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (1 a 5, média por sessão) e lista de dúvidas sem solução. O CSV `data/atendimentos.csv` é gerado com `csv.DictWriter` (menu opção 4 e automaticamente ao sair).

Como contamos: um atendimento termina quando a pessoa responde "s" (ajudou) ou digita 0 depois de tentar. As tentativas são as perguntas digitadas até esse ponto. O tempo inclui a leitura da resposta.

## Fontes consultadas

Todas as orientações estão em `data/base_conhecimento.json`, cada uma com `fonte` e `verificado_em`.

- Cartão Nacional de Saúde – Ministério da Saúde: https://www.gov.br/saude/pt-br/acesso-a-informacao/acoes-e-programas/cns
- Programa Nacional de Imunizações – Ministério da Saúde: https://www.gov.br/saude/pt-br/acesso-a-informacao/acoes-e-programas/programa-nacional-de-imunizacoes-vacinacao
- Meu SUS Digital: https://meususdigital.saude.gov.br/login
- Farmácia Popular – Ministério da Saúde: https://www.gov.br/saude/pt-br/campanhas-da-saude/2023/farmacia-popular/
- Estatuto da Pessoa Idosa (Lei 10.741/2003): https://www.planalto.gov.br/ccivil_03/leis/2003/l10.741.htm
- Cartilha do Idoso – ANTT: https://www.gov.br/antt/pt-br/assuntos/passageiros/viajantes/cartilhas/cartilha-do-idoso.pdf
- Disque 100 e denúncias de violência contra idosos – Agência Gov/Secom: https://www.gov.br/secom/pt-br/assuntos/noticias/2025/06/denuncias-de-violencia-contra-idosos-terao-prioridade-no-disque-100
- INSS: https://www.gov.br/inss/pt-br e https://meu.inss.gov.br
- Cartilha do BPC – INSS: https://www.gov.br/inss/pt-br/media/cartilha-bpc_atualizado-novembro-2024.pdf

## Resultado do teste com usuários

Testamos com **3 pessoas de fora da equipe**, em **11 atendimentos** (nenhum nome ou dado pessoal foi registrado). Os dados completos estão em `data/historico.json` e `data/atendimentos.csv`.

| Indicador | Resultado |
|-----------|-----------|
| Resposta encontrada (%) | 81,8 |
| Taxa de acerto: ajudou (%) | 81,8 |
| Tempo médio para encontrar | 53,5 s |
| Tentativas por atendimento | 1,5 |
| Facilidade de uso (1 a 5) | 4,3 (3 avaliações: 5, 3 e 5) |

**Dúvidas sem solução:** "Como pagar menos no cinema?" e "Quero ir até Paris". As duas estão fora do tema da base, e o assistente respondeu "não encontrei" em vez de inventar.

**O que o teste mostrou:** em 4 dos 11 atendimentos a pessoa precisou de mais de uma tentativa. Também vimos que o indicador de acerto depende da opinião de quem usa: a pergunta "Quero viajar de ônibus para outro estado sem pagar" trouxe a orientação 5 (ônibus urbano, 65+) em vez da 6 (passagem interestadual), e mesmo assim a pessoa marcou que ajudou.

**Melhoria feita a partir do teste:** nessa pergunta, as duas orientações empataram com 4 pontos e o desempate (menor `id`) escolheu a errada. Acrescentamos a palavra-chave `viajar de onibus` na orientação 6. Agora a mesma pergunta soma 7 pontos e traz a orientação certa, e as outras perguntas do teste continuam com o mesmo resultado.

## Limitações

- A base tem só 12 orientações; o assistente não responde nada fora dela.
- A busca compara palavras exatas: não entende sinônimos nem erros de digitação (ex.: "onibos"). Por isso o teste com usuários serve para descobrir novas palavras-chave.
- As regras são federais. Datas de campanhas, formas de acesso e documentos podem mudar em cada cidade ou estado.
- As informações mudam com o tempo; cada orientação mostra a data de verificação.
- A detecção de dados pessoais olha só dígitos e `@`: um nome digitado na pergunta não é detectado.
- O tempo medido inclui o tempo de leitura da resposta, não só o da busca.

## Vídeo técnico

https://youtu.be/PCYWJLImlbA?is=Uo5jmMNezTrzqH6g
