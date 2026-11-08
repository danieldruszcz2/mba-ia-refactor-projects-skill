```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js, CommonJS) — versão não declarada (ambiente: v24.13.0)
Framework:     Express ^4.18.2 (resolvido 4.22.1 no lockfile)
Dependencies:  express 4.22.1, sqlite3 5.1.7
Database:      SQLite em memória (':memory:') — driver cru (sqlite3, SQL parametrizado via callbacks)
Domain:        API de LMS com checkout — usuários, cursos, matrículas, pagamentos e logs de auditoria
Architecture:  God Class — src/AppManager.js concentra conexão, DDL, seed, rotas e regras de negócio dos 3 domínios; app.js e utils.js são satélites
Entry point:   src/app.js (build: n/a, start: npm start → node src/app.js, porta 3000 fixa em src/utils.js:6)
Source files:  3 files analyzed | ~180 lines of code
DB tables:     users, courses, enrollments, payments, audit_logs
Endpoints:     3 endpoints mapeados
Stack guide:   references/stacks/node.md
================================

| Método | Caminho | Local | Observação |
|---|---|---|---|
| POST   | /api/checkout               | src/AppManager.js:28  | escreve em users/enrollments/payments/audit_logs |
| GET    | /api/admin/financial-report | src/AppManager.js:80  | administrativo, sem auth |
| DELETE | /api/users/:id              | src/AppManager.js:131 | destrutivo, sem auth |
```

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js, versão não declarada) + Express 4.22.1 | DB: SQLite (in-memory, sqlite3 5.1.7)
Files:   3 analyzed | ~180 lines of code
Date:    2026-11-07

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 5 | LOW: 4

| # | Severity | Anti-pattern | Location |
|---|----------|--------------|----------|
| 1 | CRITICAL | Segredos hardcoded | src/utils.js:2-5 |
| 2 | CRITICAL | Cartão e chave do gateway em log | src/AppManager.js:45 |
| 3 | CRITICAL | Armazenamento inseguro de senhas | src/utils.js:17-23; src/AppManager.js:18, 68 |
| 4 | CRITICAL | Endpoints admin/destrutivos sem proteção | src/AppManager.js:80, 131 |
| 5 | CRITICAL | God Class AppManager | src/AppManager.js:4-139 |
| 6 | HIGH | Escrita multi-etapa sem transação / órfãos | src/AppManager.js:50-61, 69, 133-135 |
| 7 | HIGH | Estado global mutável | src/utils.js:9-10, 12-15 |
| 8 | HIGH | Lógica de negócio nas rotas | src/AppManager.js:28-78, 80-129 |
| 9 | HIGH | SQL direto nos handlers | src/AppManager.js:37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133 |
| 10 | HIGH | Acoplamento sem injeção de dependência | src/AppManager.js:7; src/app.js:5-14 |
| 11 | MEDIUM | Validação de entrada fraca | src/AppManager.js:29-35, 46, 132 |
| 12 | MEDIUM | Tratamento de erro descentralizado / erros engolidos | src/AppManager.js:38, 41, 57, 92-93, 104-106, 133-135 |
| 13 | MEDIUM | Porta fixa no código | src/utils.js:6; src/app.js:12 |
| 14 | MEDIUM | Queries N+1 no relatório financeiro | src/AppManager.js:83, 92, 104, 106 |
| 15 | MEDIUM | Callback hell e contadores manuais | src/AppManager.js:37-77, 86-127 |
| 16 | LOW | Código morto | src/utils.js:2-5, 9-10, 25; src/AppManager.js:2 |
| 17 | LOW | Magic numbers e strings | src/AppManager.js:21, 46, 48, 68, 108 |
| 18 | LOW | Nomenclatura ruim | src/AppManager.js:26, 29-33; src/utils.js:17 |
| 19 | LOW | console.log como log | src/app.js:13; src/utils.js:13 |

## Findings

### #1 [CRITICAL] Credenciais e segredos hardcoded (AP-01)
File: src/utils.js:2-5
Description: O objeto `config` versionado contém `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` (prefixo de chave live), `dbUser` e `smtpUser`, sem leitura de variáveis de ambiente.
Impact: Qualquer pessoa com acesso ao repositório obtém a chave do gateway de pagamento e a senha de banco de produção; rotacioná-las exige deploy.
Recommendation: Criar `src/config/index.js` lendo `process.env` (defaults seguros só para dev, nunca segredos reais) e documentar as variáveis em `.env.example`.
Playbook: P-01

### #2 [CRITICAL] Exposição de dados sensíveis em log (AP-06)
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` escreve o número completo do cartão e a chave do gateway na saída padrão a cada checkout.
Impact: Número de cartão (dado PCI) e segredo do gateway ficam em logs de servidor/agregadores, acessíveis a qualquer operador.
Recommendation: Nunca logar o segredo; mascarar o cartão (ex.: `************4444`) via helper `maskCard` e usar um logger com níveis.
Playbook: P-06

### #3 [CRITICAL] Armazenamento inseguro de senhas (AP-05)
File: src/utils.js:17-23
File: src/AppManager.js:18, 68
Description: `badCrypto` aplica base64 à senha, repete os 2 primeiros caracteres e trunca em 10 — é reversível/colidível e sem salt; o checkout usa `badCrypto(p || "123456")` (senha padrão quando ausente) e o seed grava `'123'` em texto puro.
Impact: Senhas triviais de recuperar após vazamento; usuários criados sem senha compartilham a mesma senha conhecida `123456`.
Recommendation: Usar `crypto.scrypt` com salt de `crypto.randomBytes` e verificação com `crypto.timingSafeEqual`; gerar senha aleatória (não um literal) quando ausente; hashear o seed.
Playbook: P-06

### #4 [CRITICAL] Endpoints administrativos/destrutivos sem proteção (AP-04)
File: src/AppManager.js:80, 131
Description: `GET /api/admin/financial-report` (receita e nomes dos alunos) e `DELETE /api/users/:id` não têm nenhuma autenticação/autorização; não existe mecanismo de auth no projeto.
Impact: Qualquer cliente anônimo lê o relatório financeiro e apaga qualquer usuário.
Recommendation: Middleware `requireAdmin` (token de admin via env) nessas rotas, com flag `ENABLE_ADMIN_ROUTES` desligada por padrão respondendo `403`.
Playbook: P-07

### #5 [CRITICAL] God Class / God Module (AP-03)
File: src/AppManager.js:4-139
Description: A classe `AppManager` abre a conexão (`constructor`, linha 7), cria o schema e popula seed (`initDb`, 10-23) e registra todas as rotas com regras de negócio e SQL de 5 tabelas (`setupRoutes`, 25-138; o handler de checkout tem 50 linhas).
Impact: Nenhuma parte pode ser testada ou reutilizada isoladamente; qualquer mudança toca o mesmo arquivo e mistura camadas.
Recommendation: Separar em `config/`, `models/` (conexão + repositórios por tabela), `services/` (checkout, relatório), `controllers/`, `routes/`, `middlewares/` e um `createApp` como composition root.
Playbook: P-03

### #6 [HIGH] Escrita multi-etapa sem transação (AP-11)
File: src/AppManager.js:50-61, 69, 133-135
Description: O checkout grava `users` (69), `enrollments` (50), `payments` (54) e `audit_logs` (57) em callbacks encadeados sem `BEGIN/COMMIT/ROLLBACK`; o `DELETE FROM users` (133) não remove matrículas/pagamentos, como a própria resposta admite ("as matrículas e pagamentos ficaram sujos no banco").
Impact: Falha no meio deixa matrícula sem pagamento ou usuário criado sem matrícula; deleção gera órfãos que distorcem o relatório financeiro ("Unknown").
Recommendation: Helper de transação no model e executar o checkout inteiro e a deleção em cascata (payments → enrollments → user) dentro de uma transação.
Playbook: P-09

### #7 [HIGH] Estado global mutável (AP-09)
File: src/utils.js:9-10, 12-15
Description: `let globalCache = {}` e `let totalRevenue = 0` no escopo do módulo; `logAndCache` (chamada em src/AppManager.js:59) escreve no cache a cada checkout sem limite nem leitura.
Impact: Crescimento de memória ilimitado por usuário e estado compartilhado entre requisições que impede testes isolados.
Recommendation: Remover o cache global (é write-only) e `totalRevenue`; qualquer estado necessário deve viver em instâncias injetadas pelo composition root.
Playbook: P-14

### #8 [HIGH] Lógica de negócio na rota (Fat Controller) (AP-07)
File: src/AppManager.js:28-78, 80-129
Description: O handler de checkout decide aprovação do pagamento (`cc.startsWith("4")`, 46), cria usuário, matricula e audita; o handler do relatório agrega receita (`courseData.revenue += payment.amount`, 109) e monta a resposta manualmente.
Impact: Regras de pagamento e de relatório não podem ser testadas nem reutilizadas sem HTTP.
Recommendation: Mover para `services/checkoutService` e `services/reportService`; controllers só extraem entrada e devolvem a resposta.
Playbook: P-04

### #9 [HIGH] Acesso a dados fora da camada Model (AP-08)
File: src/AppManager.js:37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133
Description: Os handlers chamam `this.db.get/all/run` com SQL diretamente, para 5 tabelas distintas.
Impact: SQL espalhado pelas rotas; trocar schema ou adicionar transação exige mexer em código HTTP.
Recommendation: Repositórios em `models/` (`userRepository`, `courseRepository`, `enrollmentRepository`, `paymentRepository`, `auditLogRepository`, `reportRepository`) com queries parametrizadas.
Playbook: P-04

### #10 [HIGH] Acoplamento forte sem injeção de dependência (AP-10)
File: src/AppManager.js:7
File: src/app.js:5-14
Description: O construtor de `AppManager` instancia `new sqlite3.Database(':memory:')`; `app.js` cria a app, o banco e chama `listen` no carregamento do módulo, sem função de fábrica.
Impact: Impossível subir a app com outro banco (ex.: de teste) ou sem abrir a porta.
Recommendation: `createApp({ db, config })` monta repositórios → services → controllers → rotas; `app.js` apenas cria o banco, chama a fábrica e faz `listen`.
Playbook: P-14

### #11 [MEDIUM] Validação de entrada ausente ou fraca (AP-15)
File: src/AppManager.js:29-35, 46, 132
Description: O checkout só verifica presença de `usr`, `eml`, `c_id`, `card`; não valida tipo/formato — `card` numérico (ex.: `"card": 4111`) faz `cc.startsWith` lançar `TypeError` → 500; email e `c_id` não são validados; `req.params.id` (132) é usado sem checar se é inteiro.
Impact: Entradas malformadas derrubam o handler com 500 ou gravam dados inválidos (emails inválidos).
Recommendation: Validadores puros em `utils/validators.js` (string não vazia, email, inteiro positivo, cartão só dígitos) respondendo `400`.
Playbook: P-11

### #12 [MEDIUM] Tratamento de erro descentralizado / erros engolidos (AP-16)
File: src/AppManager.js:38, 41, 57, 92-93, 104-106, 133-135
Description: Cada callback trata `err` à sua maneira: erro de banco vira `404` (38), o erro do audit log é ignorado (57), erros em 92/104/106 são ignorados (`enrollments.length` com `enrollments` indefinido lança exceção dentro do callback e derruba o processo), e o `DELETE` responde sucesso mesmo com erro (133-135). Não há error handler central do Express.
Impact: Falhas silenciosas, respostas enganosas e possível crash do processo inteiro por exceção não capturada em callback.
Recommendation: Handlers `async` envolvidos por `asyncHandler`, erros tipados (`HttpError`) e um middleware de erro de 4 parâmetros registrado por último, sem vazar detalhes internos.
Playbook: P-05

### #13 [MEDIUM] Configuração de execução fixa no código (AP-12)
File: src/utils.js:6
File: src/app.js:12
Description: A porta `3000` é literal no objeto `config` e usada direto em `app.listen(config.port)`, sem `process.env.PORT`. Severidade reduzida de HIGH para MEDIUM: não há debug, CORS aberto nem bind inseguro — só a porta fixa.
Impact: Não é possível alterar a porta por ambiente (containers, PaaS) sem editar código.
Recommendation: Ler `PORT` em `src/config/index.js` com default `3000`.
Playbook: P-01

### #14 [MEDIUM] Queries N+1 no relatório financeiro (AP-13)
File: src/AppManager.js:83, 92, 104, 106
Description: O relatório faz 1 query de cursos, 1 de matrículas por curso e 2 (usuário + pagamento) por matrícula: `1 + C + 2E` consultas.
Impact: O tempo de resposta cresce linearmente com o número de matrículas.
Recommendation: Uma única query com `LEFT JOIN` courses → enrollments → users → payments, agregada no service preservando ordem e formato.
Playbook: P-08

### #15 [MEDIUM] Fluxo assíncrono frágil (AP-17)
File: src/AppManager.js:37-77, 86-127
Description: O checkout aninha 5 níveis de callbacks (`get` → `get` → `run` → `run` → `run`) misturando `this`/`self`; o relatório controla término com contadores manuais `coursesPending`/`enrPending` e a ordem de `report.push` depende da ordem de conclusão dos callbacks.
Impact: Código difícil de seguir, erros não propagados e ordem de saída não determinística.
Recommendation: Promisificar o driver no model (`run/get/all` retornando Promise) e usar `async/await`.
Playbook: P-10

### #16 [LOW] Código morto (AP-21)
File: src/utils.js:2-5, 9-10, 25
File: src/AppManager.js:2
Description: `totalRevenue` é exportado e importado em AppManager.js:2 mas nunca usado; `globalCache` é só escrito; `config.dbUser`, `config.dbPass` e `config.smtpUser` não são lidos em lugar nenhum.
Impact: Ruído que sugere funcionalidades inexistentes (SMTP, banco autenticado).
Recommendation: Remover símbolos e imports não usados.
Playbook: P-15

### #17 [LOW] Magic numbers e strings (AP-19)
File: src/AppManager.js:21, 46, 48, 68, 108
Description: A regra de aprovação `cc.startsWith("4")`, os status `"PAID"`/`"DENIED"` repetidos e a senha padrão `"123456"` são literais soltos.
Impact: A regra de pagamento e os status ficam espalhados e sujeitos a divergência.
Recommendation: `config/constants.js` com `PAYMENT_STATUS` e `APPROVED_CARD_PREFIX` congelados (`Object.freeze`).
Playbook: P-13

### #18 [LOW] Nomenclatura ruim (AP-20)
File: src/AppManager.js:26, 29-33
File: src/utils.js:17
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`, mistura de `self` e `this` no mesmo handler, `badCrypto` como nome de função de produção e `utils.js` guardando configuração.
Impact: Leitura lenta e propensa a erro em código de pagamento.
Recommendation: Nomes descritivos internamente, mantendo os campos de contrato do JSON (`usr`, `eml`, `pwd`, `c_id`, `card`).
Playbook: P-13

### #19 [LOW] Saída padrão como mecanismo de log (AP-22)
File: src/app.js:13
File: src/utils.js:13
Description: `console.log` sem nível nem timestamp no boot e em `logAndCache` (o log de AppManager.js:45 já está no #2).
Impact: Logs sem estrutura, impossíveis de filtrar por nível.
Recommendation: Logger fino em `utils/logger.js` com níveis e timestamp.
Playbook: P-13

## Architecture Notes
- Não há camadas: `AppManager` é ao mesmo tempo conexão, migração/seed, repositório, serviço e roteador; `utils.js` mistura config e helpers.
- Faltam por completo: config via ambiente, models/repositórios, services, controllers, routes, middlewares (erro e auth) e composition root.
- O banco é em memória e recriado no boot com seed — a baseline e a validação da Fase 3 só precisam reiniciar o processo (sem backup de arquivo).
- APIs deprecated: verificado contra Node 24 / Express 4.22 / sqlite3 5.1.7 — nenhum uso encontrado (`Buffer.from` é a API moderna; não há `new Buffer`, `body-parser`, `res.send(status, body)` etc.). O estilo de callbacks é tratado no #15.
- O contrato de entrada (`usr`, `eml`, `pwd`, `c_id`, `card`) e as respostas em texto puro (`"Bad Request"`, `"Curso não encontrado"`, ...) precisam ser preservados na refatoração.

================================
Total: 19 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
  y              → corrige todos os achados
  n              → encerra sem modificar nenhum arquivo
  y, skip 3,7    → corrige todos exceto os achados #3 e #7
