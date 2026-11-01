================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js, versão não declarada — v24.13.0 no ambiente) + Express 4.22.1 | DB: SQLite em memória (sqlite3 5.1.7, SQL cru)
Files:   3 analyzed | ~180 lines of code
Date:    2026-11-01

## Summary
CRITICAL: 5 | HIGH: 6 | MEDIUM: 4 | LOW: 4

| # | Severity | Anti-pattern | Location |
|---|----------|--------------|----------|
| 1 | CRITICAL | Credenciais e segredos hardcoded | src/utils.js:2-5 |
| 2 | CRITICAL | Número de cartão e chave do gateway em log | src/AppManager.js:45 |
| 3 | CRITICAL | Armazenamento inseguro de senhas | src/utils.js:17-23; src/AppManager.js:18, 68 |
| 4 | CRITICAL | Endpoints administrativos/destrutivos sem proteção | src/AppManager.js:80, 131 |
| 5 | CRITICAL | God Class `AppManager` | src/AppManager.js:4-138 |
| 6 | HIGH | Lógica de negócio nas rotas (Fat Controller) | src/AppManager.js:28-78, 80-129 |
| 7 | HIGH | Acesso a dados dentro dos handlers de rota | src/AppManager.js:37-133 |
| 8 | HIGH | Escrita multi-etapa sem transação / deleção com órfãos | src/AppManager.js:50-57, 69, 133-135 |
| 9 | HIGH | Estado global mutável | src/utils.js:9-15 |
| 10 | HIGH | Acoplamento forte sem injeção de dependência | src/AppManager.js:6-8; src/app.js:8-10 |
| 11 | HIGH | Porta fixa no código | src/utils.js:6; src/app.js:12 |
| 12 | MEDIUM | Queries N+1 no relatório financeiro | src/AppManager.js:83, 92, 104, 106 |
| 13 | MEDIUM | Validação de entrada fraca | src/AppManager.js:29-35, 46, 132 |
| 14 | MEDIUM | Tratamento de erro descentralizado e erros ignorados | src/AppManager.js:38, 57, 92-93, 104-106, 133-135 |
| 15 | MEDIUM | Fluxo assíncrono frágil (callback hell + contadores manuais) | src/AppManager.js:37-77, 86-122 |
| 16 | LOW | Nomenclatura ruim | src/AppManager.js:26, 29-33; src/utils.js:17 |
| 17 | LOW | Código morto | src/utils.js:2-3, 5, 10, 14, 25; src/AppManager.js:2 |
| 18 | LOW | Magic numbers e strings | src/AppManager.js:46, 48, 68, 108 |
| 19 | LOW | `console.log` como mecanismo de log | src/app.js:13; src/utils.js:13 |

## Findings

### #1 [CRITICAL] Credenciais e segredos hardcoded (AP-01)
File: src/utils.js:2-5
Description: O objeto `config` contém `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` (prefixo de chave live), `dbUser: "admin_master"` e `smtpUser` escritos no código versionado.
Impact: Qualquer pessoa com acesso ao repositório obtém a chave do gateway de pagamento e a senha do banco; rotacioná-las exige novo deploy.
Recommendation: Criar `src/config/index.js` lendo `process.env` (`PAYMENT_GATEWAY_KEY`, `PORT`, ...) sem defaults secretos, e documentar as variáveis em `.env.example`.
Playbook: P-01

### #2 [CRITICAL] Exposição de dados sensíveis em log (AP-06)
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` grava o número completo do cartão e a chave do gateway na saída padrão a cada checkout.
Impact: Logs passam a conter PAN completo e segredo do gateway (violação PCI-DSS); qualquer um com acesso aos logs pode reutilizá-los.
Recommendation: Remover o segredo do log e mascarar o cartão (apenas últimos 4 dígitos) usando um logger com níveis.
Playbook: P-06

### #3 [CRITICAL] Armazenamento inseguro de senhas (AP-05)
File: src/utils.js:17-23
File: src/AppManager.js:18, 68
Description: `badCrypto` repete os 2 primeiros caracteres do base64 da senha e trunca em 10 caracteres — não há salt nem função de derivação, e senhas com o mesmo prefixo geram o mesmo "hash". O seed grava a senha `'123'` em texto puro (linha 18) e o checkout usa a senha padrão `"123456"` quando `pwd` não é enviado (linha 68).
Impact: Hashes triviais de inverter/colidir; contas criadas sem senha ficam com uma senha conhecida por todos.
Recommendation: Usar `crypto.scrypt` com salt de `crypto.randomBytes` (nativo do Node) e `timingSafeEqual` na verificação; gerar senha aleatória em vez de default fixo; hashear o seed.
Playbook: P-06

### #4 [CRITICAL] Endpoints administrativos/destrutivos sem proteção (AP-04)
File: src/AppManager.js:80, 131
Description: `GET /api/admin/financial-report` expõe receita e nomes de alunos e `DELETE /api/users/:id` apaga usuários, ambos sem qualquer autenticação/autorização.
Impact: Qualquer cliente anônimo lê dados financeiros e apaga contas.
Recommendation: Middleware `requireAdmin` (token via env `ADMIN_TOKEN`) e flag `ENABLE_ADMIN_ROUTES` (default `false` → `403`).
Playbook: P-07

### #5 [CRITICAL] God Class `AppManager` (AP-03)
File: src/AppManager.js:4-138
Description: A classe abre a conexão (linha 7), cria schema e seed (10-23), registra as 3 rotas HTTP (25-138), executa SQL, aplica regras de pagamento/matrícula e monta o relatório — quatro camadas e três domínios (usuários, checkout, financeiro) num só lugar.
Impact: Nada pode ser testado ou alterado isoladamente; qualquer mudança toca o arquivo inteiro.
Recommendation: Decompor em `config/`, `models/` (conexão + repositórios), `services/`/`controllers/`, `routes/` e `middlewares/`, com `app.js` como composition root.
Playbook: P-03

### #6 [HIGH] Lógica de negócio nas rotas — Fat Controller (AP-07)
File: src/AppManager.js:28-78, 80-129
Description: O handler de `/api/checkout` (51 linhas) decide aprovação do pagamento (`cc.startsWith("4")`), cria usuário, matricula, registra pagamento e auditoria; o handler do relatório (50 linhas) agrega receita e alunos por curso.
Impact: Regras de pagamento e de relatório só podem ser exercitadas via HTTP; impossível reutilizar.
Recommendation: Mover para `CheckoutService`/`ReportService` chamados por controllers finos.
Playbook: P-04

### #7 [HIGH] Acesso a dados fora da camada Model (AP-08)
File: src/AppManager.js:37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133
Description: Todas as chamadas `this.db.get/run/all` com SQL cru estão dentro dos handlers de rota; não existe camada de repositório.
Impact: SQL espalhado pelas rotas; trocar esquema ou driver exige reescrever handlers.
Recommendation: Criar repositórios em `src/models/` (users, courses, enrollments, payments, audit_logs) com queries parametrizadas.
Playbook: P-04

### #8 [HIGH] Escrita multi-etapa sem transação (AP-11)
File: src/AppManager.js:50-57, 69, 133-135
Description: O checkout grava em `users` (69), `enrollments` (50), `payments` (54) e `audit_logs` (57) em callbacks encadeados sem `BEGIN/COMMIT/ROLLBACK`. O `DELETE /api/users/:id` remove o usuário e deixa matrículas e pagamentos órfãos — a própria resposta admite: "as matrículas e pagamentos ficaram sujos no banco".
Impact: Falha no meio do checkout deixa matrícula sem pagamento (aluno com acesso sem pagar) ou usuário criado sem matrícula; deleção corrompe o relatório.
Recommendation: Helper de transação (`BEGIN`/`COMMIT`/`ROLLBACK`) envolvendo o checkout e a deleção em cascata (payments → enrollments → user).
Playbook: P-09

### #9 [HIGH] Estado global mutável (AP-09)
File: src/utils.js:9-15
Description: `globalCache = {}` e `totalRevenue = 0` são variáveis de módulo; `logAndCache` escreve em `globalCache` a cada checkout e o cache cresce sem limite e nunca é lido.
Impact: Vazamento de memória proporcional ao número de usuários; estado compartilhado entre requisições e testes.
Recommendation: Eliminar o cache global (não há leitor); qualquer estado necessário passa a ser injetado via composition root.
Playbook: P-14

### #10 [HIGH] Acoplamento forte sem injeção de dependência (AP-10)
File: src/AppManager.js:6-8
File: src/app.js:8-10
Description: O construtor de `AppManager` instancia `new sqlite3.Database(':memory:')` e o módulo importa `config` global; `app.js` cria a app como efeito colateral de import, sem função de fábrica.
Impact: Impossível substituir o banco (ex.: em testes) ou montar a app sem subir o servidor.
Recommendation: `createApp({ db, config })` montando models → services → controllers → routes; `app.js` só cria a conexão e faz `listen`.
Playbook: P-14

### #11 [HIGH] Configuração de execução fixa no código (AP-12)
File: src/utils.js:6
File: src/app.js:12
Description: A porta `3000` é fixa em `config.port` e não pode ser alterada por ambiente. Não há debug, CORS ou bind inseguros; mantido em HIGH só porque a config inteira (incluindo segredos, #1) vive no mesmo literal — o próprio item, isolado, seria MEDIUM.
Impact: Não dá para rodar duas instâncias ou adaptar a ambientes (container/PaaS) sem editar código.
Recommendation: Ler `PORT` de `process.env` com default `3000` para desenvolvimento.
Playbook: P-01

### #12 [MEDIUM] Queries N+1 no relatório financeiro (AP-13)
File: src/AppManager.js:83, 92, 104, 106
Description: Para cada curso faz uma query de matrículas e, para cada matrícula, uma query de usuário e outra de pagamento — `1 + C + 2E` queries por requisição.
Impact: Latência cresce linearmente com o número de matrículas; o endpoint degrada rapidamente.
Recommendation: Uma única query com `LEFT JOIN` courses → enrollments → users → payments, agregada em memória preservando a ordem.
Playbook: P-08

### #13 [MEDIUM] Validação de entrada fraca (AP-15)
File: src/AppManager.js:29-35, 46, 132
Description: O checkout só verifica presença de `usr`, `eml`, `c_id`, `card`; não valida tipo/formato. Se `card` vier como número, `cc.startsWith` (46) lança `TypeError` dentro de um callback do sqlite e **derruba o processo**. `:id` do DELETE não é validado.
Impact: Uma requisição malformada derruba o servidor inteiro (DoS trivial); dados inválidos chegam ao banco.
Recommendation: Validadores puros em `src/utils/validators.js` (string não vazia, email, `c_id` inteiro, `card` só dígitos, id inteiro) respondendo `400`.
Playbook: P-11

### #14 [MEDIUM] Tratamento de erro descentralizado / erros ignorados (AP-16)
File: src/AppManager.js:38, 57, 92-93, 104-106, 133-135
Description: Erro de banco ao buscar curso vira `404` (38); o erro do insert de auditoria é ignorado (57); em 92 o `err` é ignorado e `enrollments.length` lança `TypeError` se a query falhar; erros em 104/106 são ignorados; o DELETE ignora `err` e responde sucesso sempre (133-135). Não há middleware de erro.
Impact: Falhas silenciosas, respostas mentirosas e crash do processo em erro de banco.
Recommendation: Funções async que propagam erros + middleware de erro Express (4 parâmetros) registrado por último, com `AppError` para erros de domínio.
Playbook: P-05

### #15 [MEDIUM] Fluxo assíncrono frágil (AP-17)
File: src/AppManager.js:37-77, 86-122
Description: O checkout aninha 5 níveis de callbacks (37 → 40 → 50 → 54 → 57); o relatório usa contadores manuais `coursesPending`/`enrPending` com o bloco de finalização duplicado (95-99 e 117-122), e a ordem dos cursos no array depende de qual callback termina primeiro.
Impact: Código difícil de seguir, erros não propagados, ordem de resposta não determinística.
Recommendation: Promisificar o driver (`util.promisify`/wrappers) e usar `async`/`await`.
Playbook: P-10

### #16 [LOW] Nomenclatura ruim (AP-20)
File: src/AppManager.js:26, 29-33
File: src/utils.js:17
Description: Variáveis `u`, `e`, `p`, `cid`, `cc` no fluxo de pagamento; `self = this` misturado com `this`; função `badCrypto`; módulo `utils` guardando configuração; classe `AppManager` sem significado de domínio.
Impact: Leitura lenta de código sensível (pagamento/senha).
Recommendation: Nomes descritivos internamente (`userName`, `email`, `password`, `courseId`, `cardNumber`), mantendo os campos do JSON (`usr`, `eml`, `pwd`, `c_id`, `card`) como contrato.
Playbook: P-13

### #17 [LOW] Código morto (AP-21)
File: src/utils.js:2-3, 5, 10, 14, 25
File: src/AppManager.js:2
Description: `totalRevenue` é exportado e importado em `AppManager.js:2` mas nunca usado; `globalCache` é escrito e nunca lido; `config.dbUser`, `config.dbPass` e `config.smtpUser` não são referenciados em lugar nenhum.
Impact: Ruído e falsa impressão de funcionalidades (cache, SMTP) que não existem.
Recommendation: Remover símbolos e imports não usados.
Playbook: P-15

### #18 [LOW] Magic numbers e strings (AP-19)
File: src/AppManager.js:46, 48, 68, 108
Description: Regra de aprovação `"4"` (prefixo do cartão) solta no handler; status `"PAID"`/`"DENIED"` repetidos como literais (46, 48, 108); default `"123456"` (68, ver #3).
Impact: Regras de negócio escondidas e divergência fácil entre lugares que comparam status.
Recommendation: `src/config/constants.js` com `PAYMENT_STATUS` e `APPROVED_CARD_PREFIX` congelados.
Playbook: P-13

### #19 [LOW] Saída padrão como mecanismo de log (AP-22)
File: src/app.js:13
File: src/utils.js:13
Description: `console.log` sem nível/timestamp no boot e em `logAndCache` (o log sensível de AppManager.js:45 está no #2).
Impact: Logs sem estrutura nem nível, impossíveis de filtrar.
Recommendation: Logger fino com níveis (`src/utils/logger.js`) e `LOG_LEVEL` via env.
Playbook: P-13

## Architecture Notes
- Arquitetura atual: **God Class** — `AppManager.js` concentra conexão, schema/seed, rotas, SQL e regras; `app.js` e `utils.js` são satélites (`utils` mistura config com segredos, estado global e "crypto").
- Camadas inexistentes: config, models/repositórios, services, controllers, routes e middlewares (erro/auth). Não há composition root.
- Código morto estrutural: `globalCache`/`logAndCache` (cache nunca lido), `totalRevenue`, credenciais de banco/SMTP sem uso.
- Deprecated APIs: nenhuma encontrada para Node 24 / Express 4.22 / sqlite3 5.1.7 (o estilo de callbacks não é deprecated no `sqlite3`, mas é tratado em #15).
- Plano antecipado: `src/config`, `src/models` (database + repositórios), `src/services` (checkout, report, user), `src/controllers`, `src/routes`, `src/middlewares` (errorHandler, requireAdmin), `src/utils` (validators, password, logger), `src/app.js` mantido como entry (`npm start` inalterado).

================================
Total: 19 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
  y              → corrige todos os achados
  n              → encerra sem modificar nenhum arquivo
  y, skip 3,7    → corrige todos exceto os achados #3 e #7
