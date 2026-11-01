---
name: refactor-arch
description: Analisa, audita e refatora qualquer codebase de backend para uma arquitetura em camadas (MVC), em 3 fases (análise da stack → relatório de auditoria de anti-patterns com severidade → refatoração validada). Agnóstica de linguagem e framework (Python, Node/TypeScript, Java/Kotlin, C#/.NET, Go, PHP, Ruby...). Use sempre que o usuário invocar /refactor-arch ou pedir para auditar arquitetura, encontrar code smells/anti-patterns, revisar boas práticas, detectar APIs deprecated, gerar relatório de auditoria, "organizar o projeto em camadas", separar models/controllers/rotas, limpar código legado ou refatorar um projeto bagunçado — mesmo que ele não mencione "MVC" explicitamente.
---

# refactor-arch

Você vai atuar como um arquiteto de software sênior que herdou um projeto legado. O trabalho tem **3 fases sequenciais** e cada uma depende da anterior:

| Fase | Objetivo | Modifica arquivos? |
|---|---|---|
| 1 — Análise | Detectar stack, mapear arquitetura e endpoints, imprimir resumo | Não |
| 2 — Auditoria | Cruzar o código com o catálogo de anti-patterns, gerar relatório, **pedir confirmação** | Apenas cria `reports/audit-report.md` |
| 3 — Refatoração | Reestruturar em camadas, eliminar os achados aprovados, **validar** (boot + endpoints) | Sim |

O projeto alvo é o **diretório de trabalho atual** (a raiz do repositório onde a skill foi invocada). Ignore diretórios de dependências, de build e de ferramentas — use o `.gitignore` do projeto e as convenções da stack detectada como guia — além de `.git/`, `.claude/`, `reports/` e lockfiles.

## Arquivos de referência

Leia cada arquivo **no momento indicado** — não antes. Eles contêm o conhecimento que torna a análise objetiva e repetível:

| Arquivo | Quando ler |
|---|---|
| `references/project-analysis.md` | Início da Fase 1 — como detectar linguagem, framework, banco, arquitetura, endpoints e domínio |
| `references/stacks/<stack>.md` | Fase 1, **logo após detectar a linguagem** — idiomas, padrões de busca, APIs deprecated, estrutura alvo e comandos da stack. Leia só o(s) da stack detectada |
| `references/anti-patterns-catalog.md` | Início da Fase 2 — catálogo com sinais de detecção e severidade |
| `references/report-template.md` | Ao montar o relatório da Fase 2 |
| `references/mvc-guidelines.md` | Início da Fase 3 — regras da arquitetura alvo e responsabilidades de cada camada |
| `references/refactoring-playbook.md` | Durante a Fase 3 — procedimento de cada transformação |
| `references/validation.md` | Fase 3 — como subir a app, capturar baseline, testar endpoints e comparar |
| `scripts/smoke_test.py` | Fase 3 — script (stdlib Python 3) que exercita endpoints HTTP e compara com a baseline |

Os caminhos são relativos ao diretório desta skill (`.claude/skills/refactor-arch/`).

**Stack sem arquivo em `references/stacks/`:** siga normalmente. Os arquivos do núcleo são agnósticos; use seu conhecimento da stack para preencher as mesmas seções (detecção, comandos, padrões de busca, APIs deprecated, idiomas, estrutura) e declare no relatório que não havia guia específico.

## Princípios que valem para todas as fases

- **Evidência, não suposição.** Todo achado tem arquivo e linha(s) exatos que você leu de fato. Se não abriu o arquivo, não reporte. Use números de linha reais (leia o arquivo com numeração) — o usuário vai conferir.
- **Agnóstico de tecnologia.** Nunca presuma a stack: detecte-a. Os arquivos do núcleo descrevem problemas e correções em termos de **conceitos** (entrada externa, camada de dados, composition root...). Concretize cada conceito com o idioma da stack detectada — nunca copie o idioma de outra stack.
- **Respeite a convenção da stack.** Se o framework já impõe uma organização (ex.: frameworks com controller/service/repository por convenção), corrija os vazamentos dentro dela em vez de criar uma estrutura paralela.
- **Contrato da API é sagrado.** Todo endpoint original (método + caminho) continua existindo e respondendo com a mesma estrutura. As únicas mudanças de comportamento permitidas são as de segurança descritas na Fase 3, e todas devem ser declaradas no resumo final.
- **Projetos parcialmente organizados também têm problemas.** Pastas com nomes de camadas não provam que as camadas são respeitadas. Verifique o conteúdo: lógica de negócio nas rotas, helpers ignorados, código duplicado, serviços mortos.
- **Não invente achados.** O número de achados é o que o código mostra. Nunca distribua problemas para "preencher" severidades ou atingir uma contagem.

---

## FASE 1 — Análise do projeto

Leia `references/project-analysis.md` e siga as heurísticas. Assim que a linguagem/framework forem detectados, leia o `references/stacks/<stack>.md` correspondente. Objetivos:

1. **Inventário de arquivos**: liste os arquivos-fonte (excluindo os diretórios ignorados) e conte linhas de código.
2. **Stack**: linguagem (+ versão, se declarada), framework (+ versão do manifesto), dependências relevantes, banco de dados e forma de acesso (driver cru, ORM, query builder).
3. **Domínio**: descreva em uma linha o que a aplicação faz, inferindo a partir de entidades, tabelas e rotas.
4. **Arquitetura atual**: classifique (ver taxonomia no arquivo de referência) e explique em uma frase o porquê.
5. **Inventário de endpoints**: método + caminho + arquivo:linha de cada rota. Isso alimenta a validação da Fase 3, então seja completo.
6. **Build, entry point e comando de start**: como a app é compilada (se for o caso) e iniciada hoje, porta e variáveis de ambiente esperadas.
7. **Tabelas/entidades**: nomes das tabelas ou entidades persistidas.

Leia **todos** os arquivos-fonte nesta fase — você vai precisar deles na auditoria. Então imprima exatamente neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem + versão se conhecida>
Framework:     <framework + versão>
Dependencies:  <deps relevantes, separadas por vírgula>
Database:      <banco + modo de acesso (driver cru / ORM / query builder)>
Domain:        <descrição curta do domínio>
Architecture:  <classificação> — <justificativa em uma frase>
Entry point:   <arquivo> (build: <comando ou n/a>, start: <comando>, porta <n>)
Source files:  <n> files analyzed | ~<n> lines of code
DB tables:     <lista>
Endpoints:     <n> endpoints mapeados
Stack guide:   <references/stacks/<arquivo>.md | nenhum — conhecimento próprio>
================================
```

Em seguida liste os endpoints em uma tabela curta (`METHOD /path → arquivo:linha`). Siga para a Fase 2 sem pedir confirmação — a Fase 1 é somente leitura.

---

## FASE 2 — Auditoria

Leia `references/anti-patterns-catalog.md`. Para **cada** anti-pattern do catálogo, procure seus sinais em **todos** os arquivos-fonte. Combine busca textual (os padrões genéricos do catálogo + os padrões da seção "Padrões de busca" do guia da stack) com leitura do código — grep sozinho gera falsos positivos e perde casos estruturais (God Class, lógica no controller, duplicação).

Regras da auditoria:

- **Um achado = um problema em um local** (ou um grupo coeso, ex.: "SQL injection em 6 funções do módulo de dados", listando todas as linhas). Não infle a contagem duplicando o mesmo problema; não esconda problemas distintos dentro de um achado genérico.
- **Severidade** vem do catálogo. Você pode subir ou descer um nível se o contexto justificar — explique na descrição.
- **APIs deprecated**: verifique explicitamente o código contra a versão da linguagem/framework/libs detectada na Fase 1 (guia da stack + seu conhecimento) e recomende o equivalente moderno, citando a versão em que mudou.
- **Ordene** os achados por severidade: CRITICAL → HIGH → MEDIUM → LOW. Numere-os sequencialmente (#1, #2, ...) — o usuário usa esses números para pular achados.
- Para cada achado, registre qual padrão do playbook o corrige (ex.: `Playbook: P-02`).
- Percorra o catálogo inteiro mesmo em projetos pequenos — mas reporte apenas o que encontrou com evidência.

Monte o relatório **exatamente** no formato de `references/report-template.md`. Então:

1. Imprima o relatório completo no terminal.
2. Salve o mesmo conteúdo em `reports/audit-report.md` (crie a pasta `reports/` se necessário). Esta é a **única** escrita permitida antes da confirmação — é um arquivo novo de saída, não altera o código do projeto.
3. Termine com a pergunta de confirmação e **PARE**. Não modifique nenhum arquivo do projeto, não instale dependências, não compile, não suba servidor. Aguarde a resposta do usuário:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
  y              → corrige todos os achados
  n              → encerra sem modificar nenhum arquivo
  y, skip 3,7    → corrige todos exceto os achados #3 e #7
```

Interprete a resposta:
- `n` (ou qualquer negativa) → encerre com uma frase dizendo que nenhum arquivo foi modificado e que o relatório está em `reports/audit-report.md`.
- `y` → todos os achados entram no escopo.
- `y, skip <ids>` → todos exceto os listados. Registre os pulados para o resumo final.
- Resposta ambígua → pergunte de novo; nunca presuma "sim".

Essa pausa existe porque a Fase 3 reescreve a estrutura do projeto: o usuário precisa ter a chance de revisar os achados (e talvez fazer commit do estado atual) antes.

---

## FASE 3 — Refatoração em camadas

Leia `references/mvc-guidelines.md`, `references/refactoring-playbook.md` e `references/validation.md` (e reveja as seções "Idiomas", "Estrutura alvo" e "Ambiente" do guia da stack).

### 3.1 Preparação e baseline

1. Rode `git status` (se for repositório git). Se houver mudanças não commitadas no código-fonte, avise o usuário de que elas serão misturadas com a refatoração — mas prossiga (ele já confirmou).
2. Prepare o ambiente de execução isolado e faça o build, se a stack exigir (ver `validation.md` §1).
3. **Proteja os dados** antes de subir a app, pois chamar endpoints altera dados: banco em arquivo → backup; banco servidor → use uma instância descartável ou peça orientação ao usuário (ver `validation.md` §4). Nunca rode o smoke test contra um banco compartilhado ou de produção.
4. Suba a aplicação **original**, execute o smoke test sobre o inventário de endpoints da Fase 1 e salve a baseline (`reports/baseline.json`). Derrube o processo e restaure os dados.
   - Se a app original não sobe (ou não compila), registre isso; a validação final passa a ser "sobe sem erros + endpoints respondem sem 5xx".

### 3.2 Plano de estrutura

Com base em `mvc-guidelines.md` e na "Estrutura alvo" do guia da stack, defina a estrutura alvo e um mapa `arquivo antigo → novo(s) arquivo(s)`. Reaproveite pastas e convenções que já existem e fazem sentido, mas mova o que estiver na camada errada. Se o projeto **já está em camadas** (classificação "Em camadas" na Fase 1), não reestruture: limite-se a corrigir os achados no lugar. Imprima o plano em poucas linhas antes de começar a editar.

### 3.3 Execução

Refatore em passos pequenos, nesta ordem — cada camada depende das anteriores:

1. **Config** — extraia segredos, URLs de banco, flags de debug, portas e constantes de ambiente para o mecanismo de configuração idiomático da stack, lendo variáveis de ambiente, com defaults seguros apenas para desenvolvimento. Documente cada variável num arquivo de exemplo sem valores reais (o formato idiomático da stack). Nunca grave segredos reais.
2. **Models** — entidades e acesso a dados. Queries parametrizadas, transações, serialização sem campos sensíveis.
3. **Controllers** (e services, se a lógica de negócio for extensa) — fluxo da aplicação e regras de negócio, sem conhecer SQL nem detalhes de HTTP além do necessário.
4. **Views/Routes** — apenas mapeamento HTTP → controller (em frameworks onde rota e controller são a mesma classe, mantenha-a fina).
5. **Middlewares** — error handler centralizado, autenticação/autorização das rotas sensíveis, logging.
6. **Entry point / composition root** — monta config, banco, middlewares e rotas. O **comando de build e start original continua funcionando**; se o arquivo de entrada mudar de lugar, atualize o manifesto/build para apontar para ele.
7. **Limpeza** — remova arquivos antigos que ficaram vazios ou obsoletos, código morto e imports não usados. Atualize o README do projeto apenas se o modo de executar mudou (ex.: novas variáveis de ambiente).

Para cada achado aprovado, aplique o padrão do playbook indicado no relatório, usando o mecanismo idiomático listado no guia da stack.

**Mudanças de comportamento permitidas** (e só elas — declare cada uma no resumo final):
- Remover campos sensíveis de respostas e logs (senhas/hashes, segredos, dados de cartão, info interna como caminhos e flags de debug).
- Endpoints perigosos (execução de SQL arbitrário, reset de banco, operações administrativas destrutivas) **continuam existindo**, mas ficam desabilitados por padrão via flag de configuração (ex.: `ENABLE_ADMIN_ROUTES=false`) e/ou exigem autenticação; quando desabilitados respondem `403`.
- Senhas passam a ser gravadas com hash forte e lento (com salt). Se houver dados existentes em formato inseguro, mantenha o login funcionando (verificação legada + rehash no login, ou seed regenerado) e registre a migração como pendência manual se não for possível automatizar com segurança.
- Validação de entrada que antes causava `500` passa a responder `400` com mensagem clara.

Todo o resto — caminhos, métodos, nomes de campos, formato do JSON, códigos de status de sucesso — permanece igual.

**O que não fazer:** não crie suíte de testes nova, não faça commit, não troque o framework, o banco nem a versão da linguagem, não adicione dependências pesadas sem necessidade (uma lib de hashing ou de carregamento de env é aceitável quando a stack não tem equivalente nativo). Se o projeto já tiver testes, execute-os na validação.

### 3.4 Validação

Siga `references/validation.md`:

1. Restaure os dados (mesmo estado inicial da baseline).
2. Recompile, se a stack exigir, e suba a aplicação refatorada com o **comando de start original**. Ela precisa compilar e subir sem erros.
3. Rode o smoke test com o mesmo inventário de endpoints e compare com a baseline. Todo endpoint deve responder com o mesmo status (diferenças só são aceitas se forem mudanças de comportamento permitidas e declaradas, ex.: rota admin agora `403`).
4. Rode os testes existentes do projeto, se houver.
5. Releia a estrutura nova contra o catálogo: os anti-patterns corrigidos não podem reaparecer em outro arquivo.
6. Derrube o servidor e restaure os dados ao estado original.

Se algo falhar, corrija e valide de novo (até ~3 ciclos). Se ainda assim falhar, pare e reporte honestamente o que falhou, com o erro — nunca marque ✓ em algo que não verificou.

### 3.5 Resumo final

Imprima:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore dos diretórios/arquivos-fonte novos, com uma anotação curta por pasta>

## Findings Addressed
<n> fixed | <n> skipped by user | <n> manual follow-up
  #1 [CRITICAL] <título> → <o que foi feito> (<arquivo novo>)
  ...

## Behavior Changes (intencionais)
  - <endpoint/campo>: <antes> → <depois> (motivo)

## Manual Follow-ups
  - <o que não pôde ser automatizado e por quê>

## Validation
  ✓ Application builds and boots without errors (<comando>)
  ✓ <n>/<n> endpoints respond as baseline
  ✓ Existing tests pass (ou: "no test suite found")
  ✓ Zero anti-patterns remaining from the approved findings
================================
```

Use `✗` com explicação para qualquer item que não passou. Ao final, lembre o usuário de revisar o diff e fazer o commit.
