# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.
---

## Análise Manual

### code-smells-project

#### CRITICAL

Não conheço muito de python, mas me parece que existem rotas que dão acesso direto a atividades no banco de dados sem controle de acesso. Uma apaga todos os dados e a outra executa qualquer comando enviado. As consultas também são montadas com o texto digitado pelo usuário, o que permite enganar o login.

#### MEDIUM

Existem controllers e models, mas as regras estão espalhadas entre os dois e tem bastante código repetido. A validação de produto, por exemplo, aparece no cadastro e na edição com regras diferentes.

#### MEDIUM

A listagem de pedidos faz uma consulta para cada pedido e mais uma para cada produto, o que deve ficar lento com muitos dados. Se der erro no meio da criação de um pedido, o que já foi gravado não é desfeito.

#### LOW

O servidor sobe em modo debug e aceitando conexão de qualquer endereço. Para desenvolvimento tudo bem, mas não deveria ir assim para produção.

### ecommerce-api-legacy

#### CRITICAL

A senha do banco e a chave do sistema de pagamento estão escritas direto no código. No checkout, o número do cartão aparece no log junto com essa chave, e a função que deveria proteger a senha do usuário não faz uma criptografia de verdade.

#### MEDIUM

Quase tudo fica em uma única classe: criação do banco, rotas, checkout e relatório. Fica difícil mexer em uma parte sem afetar as outras.

#### MEDIUM

O checkout e o relatório financeiro têm muitas funções uma dentro da outra, o que deixa o fluxo difícil de seguir. No relatório, se algum passo der erro, a resposta pode nem ser enviada.

#### LOW

Os nomes de campos e variáveis são muito abreviados (`usr`, `eml`, `pwd`), o que atrapalha a leitura.

#### LOW

Tem variáveis criadas e nunca usadas, e cada mensagem de erro segue um formato diferente.

### task-manager-api

#### CRITICAL

Nenhuma rota pede autenticação, o token do login é só um texto com o id do usuário e qualquer um consegue se cadastrar como admin. A senha é guardada com MD5, que hoje é considerado fraco, e ainda volta nas respostas da API.

#### MEDIUM

O projeto tem pastas separadas, mas as rotas fazem quase tudo. Existem funções prontas que ninguém usa, e a regra de tarefa atrasada está copiada em vários lugares.

#### MEDIUM

A listagem de tarefas faz uma consulta extra por tarefa para buscar usuário e categoria, e nenhuma listagem tem paginação. Com mais dados, a API deve ficar lenta.

#### LOW

Os logs são `print` soltos e vários erros são tratados de forma genérica, respondendo só "Erro interno". Fica difícil descobrir o que deu errado.

#### LOW

O código usa `datetime.utcnow()`, que pelo que pesquisei está sendo descontinuado nas versões novas do python.

## Construção da Skill

Para criar a skill usei duas outras skills como apoio. A `grill-me` me ajudou no planejamento: ela faz uma série de perguntas sobre o plano até as decisões ficarem claras, como o que fazer com as rotas perigosas ou como validar a refatoração. Depois usei a `skill-creator` para escrever o `SKILL.md`, organizar os arquivos de referência e testar a skill nos projetos.

### Decisões de design

O `SKILL.md` descreve as 3 fases em ordem (análise, auditoria e refatoração) e diz em que momento cada arquivo de referência deve ser lido. A ideia foi deixar o `SKILL.md` só com o passo a passo e colocar o conhecimento nos arquivos de referência, que ficam em `.claude/skills/refactor-arch/references/`:

- `project-analysis.md`: como descobrir a linguagem, o framework, o banco e as rotas do projeto.
- `anti-patterns-catalog.md`: a lista de problemas, com sinais de detecção e severidade.
- `report-template.md`: o formato do relatório da Fase 2.
- `mvc-guidelines.md`: as regras da estrutura em camadas e o que cada camada pode fazer.
- `refactoring-playbook.md`: como corrigir cada problema, com exemplos de código.
- `validation.md`: como subir a aplicação, testar as rotas e comparar o antes e o depois.
- `stacks/`: um guia por linguagem (Python, Node, Java, .NET, Go, PHP e Ruby).

Também tem um script, `scripts/smoke_test.py`, que chama as rotas da API antes e depois da refatoração e compara as respostas.

Na Fase 2 a skill para e pede confirmação antes de mexer em qualquer arquivo, e dá para pular achados específicos (por exemplo `y, skip 3,7`).

### Anti-patterns do catálogo

O catálogo tem 22 anti-patterns, separados por severidade:

- **CRITICAL:** credenciais no código, injeção de SQL, God Class, rotas administrativas sem proteção, senha guardada de forma insegura e exposição de dados sensíveis.
- **HIGH:** regra de negócio na rota, acesso ao banco fora do model, estado global, acoplamento forte, gravações sem transação e configuração insegura (como debug ligado).
- **MEDIUM:** consultas N+1, código duplicado, validação fraca, tratamento de erro espalhado, fluxo assíncrono frágil e APIs deprecated.
- **LOW:** magic numbers, nomes ruins, código morto e `print` no lugar de log.

Escolhi esses porque são os problemas que encontrei na análise manual dos 3 projetos. Também incluí alguns que não apareceram, mas que são comuns em projetos legados, como acoplamento forte e magic numbers. Cada item aponta para a correção correspondente no playbook.

### Como a skill ficou agnóstica de tecnologia

Os arquivos principais descrevem os problemas e as correções sem citar nenhuma linguagem. Por exemplo, "consulta montada com texto do usuário" em vez de um código Python específico. O que muda de uma linguagem para outra fica nos guias da pasta `stacks/`, e todos seguem o mesmo formato: como detectar a stack, comandos para rodar, padrões de busca, APIs deprecated e a estrutura de pastas esperada. Na Fase 1 a skill descobre a linguagem e lê só o guia correspondente. Se não existir guia para a stack, ela segue usando o conhecimento próprio e avisa no relatório.

Testei nos 3 projetos, dois em Python/Flask e um em Node/Express, e a mesma skill funcionou nos três sem alteração.

### Desafios

- **Projeto que já parece organizado:** no `task-manager-api` as pastas já existiam, então a skill tendia a achar que estava tudo certo. Coloquei uma regra dizendo que ter pastas com nome de camada não prova nada, e que é preciso conferir o conteúdo.
- **Não quebrar a API:** a refatoração não podia mudar as rotas nem o formato das respostas. Por isso a skill grava as respostas antes de mexer no código e compara depois. As únicas mudanças permitidas são as de segurança, e elas precisam aparecer no resumo final.
- **Rotas perigosas:** apagar as rotas de admin mudaria a API, então decidi mantê-las, mas desligadas por padrão e protegidas por token.
- **Achados inventados:** em alguns testes a skill "forçava" problemas para cumprir as severidades. Adicionei uma regra para reportar só o que tiver arquivo e linha como prova.
- **Dados de teste:** chamar as rotas durante a validação altera o banco. A skill passou a fazer backup antes e a restaurar os dados no final.

## Resultados

### Resumo das auditorias

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| code-smells-project | 5 | 8 | 3 | 4 | 20 |
| ecommerce-api-legacy | 5 | 6 | 4 | 4 | 19 |
| task-manager-api | 4 | 5 | 6 | 4 | 19 |

Os relatórios completos estão em `reports/audit-report.md` dentro de cada projeto.

No `task-manager-api`, o achado #9 (apagar categoria deixaria tarefas órfãs) se mostrou um falso positivo durante a Fase 3. A própria skill testou e registrou isso no relatório.

### code-smells-project

**Antes**

```
app.py           rotas, configuração e SQL das rotas admin
controllers.py   handlers com validação e regras
models.py        acesso a dados dos 3 domínios
database.py      conexão global, criação das tabelas e seed
```

**Depois**

```
app.py           create_app: monta config, banco, erros e rotas
config/          leitura das variáveis de ambiente
models/          conexão por requisição + um model por entidade
services/        regras de pedido e notificações
controllers/     fluxo de cada caso de uso
routes/          Blueprints (HTTP → controller)
middlewares/     tratamento de erro central e proteção das rotas admin
utils/           constantes, erros, validações e hash de senha
```

**Checklist**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (API de loja)
- [x] Número de arquivos analisados condiz com a realidade (4 arquivos)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (20)
- [x] Detecção de APIs deprecated incluída (verificada, nenhuma encontrada)
- [x] Skill pausa e pede confirmação antes da Fase 3

Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

No teste das rotas, 31 de 37 chamadas ficaram iguais às de antes da refatoração. As 6 diferenças foram mudanças de segurança esperadas: o `/health` não mostra mais a chave secreta, o login não aceita mais injeção de SQL, as rotas admin respondem 403 por padrão e entradas inválidas passaram de erro 500 para 400.

### ecommerce-api-legacy

**Antes**

```
src/app.js          sobe o servidor
src/AppManager.js   banco, tabelas, seed, rotas e regras, tudo junto
src/utils.js        configuração com segredos, cache global e "criptografia"
```

**Depois**

```
src/app.js          entry point (npm start continua igual)
src/createApp.js    monta config, banco, middlewares e rotas
src/config/         variáveis de ambiente e constantes
src/models/         conexão e um repositório por tabela
src/services/       checkout, relatório, usuário e gateway de pagamento
src/controllers/    fluxo de cada rota
src/routes/         mapeamento das rotas
src/middlewares/    tratamento de erro, proteção admin e async
src/utils/          erros, validação, hash de senha, logger e máscara de cartão
```

**Checklist**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (JavaScript / Node.js)
- [x] Framework detectado corretamente (Express 4.22.1)
- [x] Domínio da aplicação descrito corretamente (plataforma de cursos com checkout)
- [x] Número de arquivos analisados condiz com a realidade (3 arquivos)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (19)
- [x] Detecção de APIs deprecated incluída (verificada, nenhuma encontrada)
- [x] Skill pausa e pede confirmação antes da Fase 3

Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

Sem token de admin, 6 de 11 chamadas ficaram iguais. As diferenças são o relatório financeiro e a exclusão de usuário, que agora pedem token (403). A outra diferença é um checkout com cartão inválido, que antes derrubava o servidor e agora responde 400. Rodando de novo com o token de admin, todas as rotas responderam como antes.

### task-manager-api

**Antes**

```
app.py          cria a app no import, com debug e chave fixa
database.py
models/         user, task, category
routes/         rotas com validação, consultas e regras
services/       notification_service (não era usado)
utils/          helpers (não era usado)
seed.py
```

**Depois**

```
app.py          create_app (python app.py continua igual)
config/         variáveis de ambiente
models/         entidades + database.py
services/       autenticação e relatórios
controllers/    fluxo de cada recurso (tasks, users, categorias, relatórios)
routes/         Blueprints finos; categorias saíram de report_routes
middlewares/    tratamento de erro central e autorização admin
utils/          constantes, validações, erros, datas e hash de senha
```

**Checklist**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0.0 + Flask-SQLAlchemy)
- [x] Domínio da aplicação descrito corretamente (gerenciador de tarefas)
- [x] Número de arquivos analisados condiz com a realidade (15 arquivos)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (19)
- [x] Detecção de APIs deprecated incluída (`datetime.utcnow()` e `Model.query.get()`)
- [x] Skill pausa e pede confirmação antes da Fase 3

Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

34 de 44 chamadas ficaram iguais. As diferenças foram o hash da senha, que não aparece mais nas respostas, a criação de usuário admin e a exclusão de usuário, que agora pedem autorização (403), e entradas inválidas que passaram de 500 para 400.

### Aplicações rodando após a refatoração

Subi cada projeto com o comando de start original e fiz algumas chamadas com `curl`. Abaixo estão o log do servidor e as respostas recebidas (cortei as respostas longas). Para não alterar os dados reais, usei uma cópia do banco nos projetos Python.

**code-smells-project** (`python app.py`)

```
2026-11-01 19:14:59,117 INFO [__main__] Servidor iniciado em http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
2026-11-01 19:14:59,434 INFO [werkzeug] "GET /health HTTP/1.1" 200 -
2026-11-01 19:14:59,628 INFO [werkzeug] "GET /produtos HTTP/1.1" 200 -
2026-11-01 19:14:59,785 INFO [werkzeug] "GET /produtos/busca?q=mouse HTTP/1.1" 200 -
2026-11-01 19:15:00,034 INFO [controllers.usuario_controller] Login bem-sucedido para usuario 1
2026-11-01 19:15:00,034 INFO [werkzeug] "POST /login HTTP/1.1" 200 -
2026-11-01 19:15:00,182 INFO [controllers.usuario_controller] Tentativa de login falhou
2026-11-01 19:15:00,182 INFO [werkzeug] "POST /login HTTP/1.1" 401 -
2026-11-01 19:15:00,313 INFO [werkzeug] "POST /admin/reset-db HTTP/1.1" 403 -
```

```
$ curl http://127.0.0.1:5000/health
200 {"counts":{"pedidos":0,"produtos":11,"usuarios":3},"database":"connected","status":"ok","versao":"1.0.0"}

$ curl http://127.0.0.1:5000/produtos/busca?q=mouse
200 {"dados":[{"ativo":1,"categoria":"informatica",...,"descricao":"Mouse sem fio er...

$ curl -X POST http://127.0.0.1:5000/login -d '{"email":"admin@loja.com","senha":"admin123"}'
200 {"dados":{"email":"admin@loja.com","id":1,"nome":"Admin","tipo":"admin"},"mensagem":"Login OK","sucesso":true}

$ curl -X POST http://127.0.0.1:5000/login -d "{\"email\":\"admin@loja.com' OR '1'='1\",\"senha\":\"x\"}"
401 {"erro":"Email ou senha inválidos","sucesso":false}

$ curl -X POST http://127.0.0.1:5000/admin/reset-db
403 {"erro":"Rotas administrativas desabilitadas"}
```

O `/health` não mostra mais a chave secreta, o login com injeção de SQL é recusado e a rota que apagava o banco está bloqueada.

**ecommerce-api-legacy** (`npm start`)

```
2026-11-01T22:15:01.803Z [WARN] PAYMENT_GATEWAY_KEY não definida (gateway simulado).
2026-11-01T22:15:01.841Z [INFO] LMS API rodando na porta 3000
2026-11-01T22:15:02.221Z [INFO] Processando pagamento de 497 no cartão **** **** **** 4444
2026-11-01T22:15:02.253Z [INFO] Checkout concluído: usuário 2, curso "Docker"
```

```
$ curl -X POST http://127.0.0.1:3000/api/checkout -d '{"usr":"Ana","eml":"ana@email.com","pwd":"senha123","c_id":2,"card":"4111222233334444"}'
200 {"msg":"Sucesso","enrollment_id":2}

$ curl -X POST http://127.0.0.1:3000/api/checkout -d '{"usr":"Ana"}'
400 Bad Request

$ curl http://127.0.0.1:3000/api/admin/financial-report
403 Acesso negado

$ curl -X DELETE http://127.0.0.1:3000/api/users/1
403 Acesso negado
```

O checkout continua funcionando, e agora o log mostra só os 4 últimos dígitos do cartão, sem a chave do gateway. As rotas de admin pedem token.

**task-manager-api** (`python app.py`)

```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
2026-11-01 19:15:04,964 INFO werkzeug: "GET /health HTTP/1.1" 200 -
2026-11-01 19:15:05,110 INFO werkzeug: "GET /tasks HTTP/1.1" 200 -
2026-11-01 19:15:05,248 INFO werkzeug: "GET /users/1 HTTP/1.1" 200 -
2026-11-01 19:15:05,494 INFO werkzeug: "POST /login HTTP/1.1" 200 -
2026-11-01 19:15:05,638 INFO werkzeug: "GET /reports/summary HTTP/1.1" 200 -
2026-11-01 19:15:05,787 INFO werkzeug: "POST /tasks HTTP/1.1" 400 -
```

```
$ curl http://127.0.0.1:5000/tasks
200 [{"category_id":1,"category_name":"Backend","created_at":"2026-11-01 20:36:25.884764","description":"Adicionar...

$ curl http://127.0.0.1:5000/users/1
200 {"active":true,"created_at":"2026-11-01 20:36:25.861960","email":"joao@email.com","id":1,"name":"João Sil...

$ curl -X POST http://127.0.0.1:5000/login -d '{"email":"joao@email.com","password":"1234"}'
200 {"message":"Login realizado com sucesso","token":"eyJ1c2VyX2lkIjoxfQ.aue56Q.2jca7Vp9...","user":...

$ curl http://127.0.0.1:5000/reports/summary
200 {"generated_at":"2026-11-01 22:15:05.629874","overdue":{"count":2,...

$ curl -X POST http://127.0.0.1:5000/tasks -d '{"title":"Teste","priority":"alta"}'
400 {"error":"Prioridade inválida"}
```

O usuário não traz mais o campo `password`, o login devolve um token assinado em vez do `fake-jwt-token` e a prioridade inválida, que antes dava erro 500, agora responde 400.

### Como a skill se comportou em stacks diferentes

- **Python x Node:** a mesma skill funcionou nos três projetos sem alteração. Ela leu o guia de Python nos projetos Flask e o de Node no Express, e a estrutura final seguiu o jeito de cada um (Blueprints no Flask, repositórios e middlewares no Express).
- **Nível de organização:** nos projetos bagunçados (`code-smells-project` e `ecommerce-api-legacy`) a skill montou as camadas do zero. No `task-manager-api`, que já tinha pastas, ela aproveitou o que existia e corrigiu o conteúdo, como as rotas que faziam tudo e os arquivos que ninguém usava.
- **APIs deprecated:** só apareceram no `task-manager-api`. Nos outros dois a skill verificou e registrou que não encontrou nenhuma, em vez de inventar.
- **Particularidades:** no Node ela tratou também o excesso de callbacks, que não existe nos projetos Python. Como o banco do `ecommerce-api-legacy` fica em memória, não foi preciso fazer backup dos dados para os testes.

## Como Executar

### Pré-requisitos

- **Claude Code** instalado e logado (`npm install -g @anthropic-ai/claude-code` e depois `claude` para fazer o login).
- **Python 3** com `pip`, para os projetos `code-smells-project` e `task-manager-api`.
- **Node.js** com `npm`, para o `ecommerce-api-legacy`.
- **Git**, para poder revisar e desfazer as mudanças da refatoração.

A skill fica em `.claude/skills/refactor-arch/` dentro de cada projeto, então o Claude Code já a encontra ao abrir a pasta. Para usar em outro projeto, basta copiar essa pasta para dentro dele.

### Executando a skill

Em cada projeto, entre na pasta e chame a skill:

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A skill faz a análise e a auditoria, salva o relatório em `reports/audit-report.md` e para pedindo confirmação. Nesse momento dá para responder:

- `y` para corrigir tudo;
- `n` para sair sem mexer em nada;
- `y, skip 3,7` para corrigir tudo menos os achados #3 e #7.

Neste repositório os 3 projetos já estão refatorados. Para rodar a skill no código original, dá para criar uma cópia do commit inicial e colocar a skill nela:

```bash
git worktree add ../projeto-original 6d1ce62
cp -r code-smells-project/.claude ../projeto-original/code-smells-project/
cd ../projeto-original/code-smells-project
claude "/refactor-arch"
```

### Validando a refatoração

A própria skill valida o resultado no fim da Fase 3: ela sobe a aplicação, chama todas as rotas e compara com as respostas de antes da refatoração. Os arquivos dessa comparação ficam em `reports/` (`baseline.json` é o antes e `after.json` o depois).

Para conferir manualmente:

**1. Subir a aplicação**

```bash
# code-smells-project
pip install -r requirements.txt
python app.py                  # http://localhost:5000

# ecommerce-api-legacy
npm install
npm start                      # http://localhost:3000

# task-manager-api
pip install -r requirements.txt
python seed.py
python app.py                  # http://localhost:5000
```

**2. Chamar algumas rotas**

```bash
curl http://localhost:5000/health        # Python: deve responder 200
curl http://localhost:5000/produtos      # code-smells-project
curl http://localhost:5000/tasks         # task-manager-api
curl -X POST http://localhost:3000/api/checkout -H "Content-Type: application/json" \
  -d '{"usr":"Ana","eml":"ana@email.com","pwd":"senha123","c_id":2,"card":"4111222233334444"}'
```

Para facilitar o teste, criei uma collection do Postman para cada projeto, já com as rotas e exemplos de requisição. É só importar no Postman e executar:

| Projeto | Collection |
|---|---|
| code-smells-project | `code-smells-project/code-smells-api.postman_collection.json` |
| ecommerce-api-legacy | `ecommerce-api-legacy/ecommerce-api.postman_collection.json` |
| task-manager-api | `task-manager-api/task-manager-api.postman_collection.json` |

O `ecommerce-api-legacy` também tem o `api.http`, com exemplos de chamadas para rodar no VS Code com a extensão REST Client.

**3. Comparar com o antes**

O script da skill compara as respostas de antes e depois:

```bash
python .claude/skills/refactor-arch/scripts/smoke_test.py compare \
  --baseline reports/baseline.json --current reports/after.json
```

As únicas diferenças esperadas são as de segurança: rotas admin respondendo 403, entradas inválidas respondendo 400 em vez de 500 e campos sensíveis (senha, chave secreta) que não aparecem mais nas respostas.

As rotas de admin vêm desligadas. Para testá-las, suba a aplicação com `ENABLE_ADMIN_ROUTES=true` e use o token de admin, como explicado no README de cada projeto (o `task-manager-api` usa o token de login de um usuário admin).
