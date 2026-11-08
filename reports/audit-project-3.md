```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python (versão não declarada; ambiente: 3.14.4)
Framework:     Flask 3.0.0
Dependencies:  flask-sqlalchemy 3.1.1, flask-cors 4.0.0, marshmallow 3.20.1 (declarado, não usado), requests 2.31.0 (declarado, não usado), python-dotenv 1.0.0 (declarado, não usado)
Database:      SQLite em arquivo (sqlite:///tasks.db → instance/tasks.db) via ORM (Flask-SQLAlchemy)
Domain:        API de gerenciamento de tarefas — tasks, users, categories e relatórios de produtividade
Architecture:  Camadas nominais (pseudo-MVC) — existem models/, routes/, services/, utils/, mas as rotas fazem validação, regras, consultas ORM e serialização; services/ e utils/helpers.py nunca são usados
Entry point:   app.py (build: n/a, start: python app.py, porta 5000; seed: python seed.py)
Source files:  15 files analyzed | ~1158 lines of code
DB tables:     users, categories, tasks
Endpoints:     22 endpoints mapeados
Stack guide:   references/stacks/python.md
================================
```

| Endpoint | Local |
|---|---|
| GET /health | app.py:22 |
| GET / | app.py:26 |
| GET /tasks | routes/task_routes.py:11 |
| GET /tasks/<id> | routes/task_routes.py:65 |
| POST /tasks | routes/task_routes.py:85 |
| PUT /tasks/<id> | routes/task_routes.py:156 |
| DELETE /tasks/<id> | routes/task_routes.py:225 |
| GET /tasks/search | routes/task_routes.py:240 |
| GET /tasks/stats | routes/task_routes.py:273 |
| GET /users | routes/user_routes.py:10 |
| GET /users/<id> | routes/user_routes.py:27 |
| POST /users | routes/user_routes.py:42 |
| PUT /users/<id> | routes/user_routes.py:92 |
| DELETE /users/<id> | routes/user_routes.py:134 |
| GET /users/<id>/tasks | routes/user_routes.py:153 |
| POST /login | routes/user_routes.py:185 |
| GET /reports/summary | routes/report_routes.py:12 |
| GET /reports/user/<id> | routes/report_routes.py:103 |
| GET /categories | routes/report_routes.py:157 |
| POST /categories | routes/report_routes.py:167 |
| PUT /categories/<id> | routes/report_routes.py:190 |
| DELETE /categories/<id> | routes/report_routes.py:211 |

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3.14 (não declarado) + Flask 3.0.0 | DB: SQLite (Flask-SQLAlchemy 3.1.1)
Files:   15 analyzed | ~1158 lines of code
Date:    2026-11-07

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 6 | LOW: 4

| # | Severity | Anti-pattern | Location |
|---|----------|--------------|----------|
| 1 | CRITICAL | Senhas com MD5 sem salt | models/user.py:27-32 |
| 2 | CRITICAL | Hash de senha exposto nas respostas | models/user.py:21 |
| 3 | CRITICAL | Segredos hardcoded | app.py:13; services/notification_service.py:7-10 |
| 4 | CRITICAL | Sem autenticação/autorização, token falso, role via body | routes/user_routes.py:52, 71-78, 119-122, 210 |
| 5 | HIGH | Debug ligado, bind 0.0.0.0, CORS aberto | app.py:15, 34 |
| 6 | HIGH | Lógica de negócio nas rotas (Fat Controller) | routes/task_routes.py:85-154; routes/report_routes.py:12-101 (+1 arquivo) |
| 7 | HIGH | Acesso a dados (ORM) nas rotas | routes/task_routes.py:14, 147-148; routes/user_routes.py:12, 81-82 (+1 arquivo) |
| 8 | HIGH | App sem factory, efeitos colaterais no import | app.py:9-31; seed.py:2 |
| 9 | HIGH | Deleção deixa órfãos / seed sem transação | routes/report_routes.py:217-219; seed.py:11-92 |
| 10 | MEDIUM | Queries N+1 e contagens repetidas | routes/task_routes.py:41-57; routes/report_routes.py:55-56 (+1 arquivo) |
| 11 | MEDIUM | Lógica e validação duplicadas | routes/task_routes.py:30-39, 110, 177; routes/user_routes.py:61, 106 (+3 arquivos) |
| 12 | MEDIUM | Validação de entrada fraca (500 em vez de 400) | routes/task_routes.py:96, 113, 182, 261, 264; routes/report_routes.py:196-197 (+1 arquivo) |
| 13 | MEDIUM | `except:` genérico e erro descentralizado | routes/task_routes.py:62, 137, 204, 236; routes/report_routes.py:186, 207, 221 (+2 arquivos) |
| 14 | MEDIUM | Deprecated API: datetime.utcnow() | models/task.py:15, 16, 52; routes/report_routes.py:35, 42, 45, 71, 133 (+6 arquivos) |
| 15 | MEDIUM | Deprecated API: Model.query.get() | routes/task_routes.py:42, 51, 67; routes/user_routes.py:29, 94 (+1 arquivo) |
| 16 | LOW | Código morto (service, helpers, métodos, imports) | services/notification_service.py:1-48; utils/helpers.py:9-116 (+5 arquivos) |
| 17 | LOW | Magic numbers e strings | routes/task_routes.py:96, 99, 104, 110, 113; routes/report_routes.py:24-28, 45, 129 (+1 arquivo) |
| 18 | LOW | Nomenclatura críptica | routes/report_routes.py:24-28; models/category.py:14 (+2 arquivos) |
| 19 | LOW | print() como log | routes/task_routes.py:149, 153, 219, 234; routes/user_routes.py:83, 89, 147 (+2 arquivos) |

## Findings

### #1 [CRITICAL] Armazenamento inseguro de senhas (AP-05)
File: models/user.py:3, 27-32
File: seed.py:19, 26, 33
Description: `set_password` grava `hashlib.md5(pwd.encode()).hexdigest()` sem salt e `check_password` compara com `==` (não é tempo constante). O seed cria usuários com senhas triviais (`1234`, `abcd`, `pass`), aceitas pela regra de mínimo de 4 caracteres.
Impact: Qualquer vazamento do banco (ou da API, ver #2) permite recuperar as senhas instantaneamente via rainbow tables.
Recommendation: Usar `werkzeug.security.generate_password_hash`/`check_password_hash` (scrypt/pbkdf2 com salt, já disponível via Flask), com verificação legada de MD5 + rehash no login para dados existentes.
Playbook: P-06

### #2 [CRITICAL] Exposição do hash de senha nas respostas (AP-06)
File: models/user.py:16-25 (linha 21)
File: routes/user_routes.py:33, 85, 129, 209
Description: `User.to_dict()` inclui `'password': self.password`, e é devolvido por `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`.
Impact: Qualquer cliente obtém o hash MD5 de qualquer usuário (combinado com #1 e #4, equivale a expor as senhas).
Recommendation: Remover `password` da serialização (`to_dict`) e nunca devolvê-lo em nenhuma resposta.
Playbook: P-06

### #3 [CRITICAL] Credenciais e segredos hardcoded (AP-01)
File: app.py:11, 13
File: services/notification_service.py:7-10
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` e a URI do banco fixos no código; `NotificationService` tem `email_user = 'taskmanager@gmail.com'` e `email_password = 'senha123'` literais.
Impact: Quem lê o repositório obtém a chave de assinatura de sessões do Flask e a senha da conta SMTP; rotacionar exige novo deploy.
Recommendation: Criar `config/settings.py` lendo `os.environ` (`SECRET_KEY`, `DATABASE_URL`, `SMTP_*`) com defaults apenas de desenvolvimento e documentar em `.env.example`.
Playbook: P-01

### #4 [CRITICAL] Endpoints sensíveis sem autenticação, token falso e escalada de privilégio (AP-04)
File: routes/user_routes.py:52, 71-78, 119-122, 210
File: routes/user_routes.py:134-151; routes/report_routes.py:211-223; routes/task_routes.py:225-238
Description: Nenhuma rota exige autenticação; `/login` devolve `'fake-jwt-token-' + str(user.id)` (previsível e nunca verificado); `POST /users` e `PUT /users/<id>` aceitam `role` (`admin`) direto do body; deleções de usuários (com cascata manual de tasks), categorias e tasks são abertas.
Impact: Qualquer cliente anônimo cria um usuário `admin`, promove a si mesmo, apaga usuários e todas as suas tarefas.
Recommendation: Emitir token assinado (`itsdangerous`, já dependência do Flask) no login e criar decorator `@admin_required` para atribuição de `role` privilegiado e para as rotas destrutivas de usuário; mudanças declaradas como comportamento de segurança.
Playbook: P-07

### #5 [HIGH] Configuração insegura de execução (AP-12)
File: app.py:15, 34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` fixo e `CORS(app)` liberando qualquer origem.
Impact: O debugger do Werkzeug exposto na rede permite execução remota de código; qualquer site pode chamar a API pelo navegador.
Recommendation: Ler `DEBUG` (default `False`), `HOST` (default `127.0.0.1`), `PORT` e `CORS_ORIGINS` da config.
Playbook: P-01

### #6 [HIGH] Lógica de negócio nas rotas — Fat Controller (AP-07)
File: routes/task_routes.py:11-63, 85-154, 156-223, 273-299
File: routes/user_routes.py:42-90, 92-132
File: routes/report_routes.py:12-101, 103-155
Description: Os handlers validam campos, aplicam regras (status/prioridade válidos, existência de usuário/categoria, cálculo de atraso e taxa de conclusão) e montam respostas à mão; `summary_report` tem ~90 linhas. O CRUD de categorias vive em `report_routes.py`, misturando dois domínios.
Impact: Regras impossíveis de reutilizar ou testar sem HTTP; cada mudança de regra exige editar várias rotas.
Recommendation: Criar `controllers/` (task, user, category, report) com as regras e deixar os Blueprints apenas mapeando HTTP → controller; mover categorias para `routes/category_routes.py`.
Playbook: P-04

### #7 [HIGH] Acesso a dados fora da camada Model (AP-08)
File: routes/task_routes.py:14, 42, 51, 67, 147-148, 218, 232-233, 247-266, 275-281
File: routes/user_routes.py:12, 29, 35, 67, 81-82, 128, 140-146, 159, 197
File: routes/report_routes.py:15-30, 46-56, 105, 109, 159, 163, 183-184, 205, 218-219
Description: Todas as rotas importam `db` e os models e chamam `Model.query`, `db.session.add/commit/rollback/delete` diretamente.
Impact: Persistência acoplada ao HTTP; trocar queries ou otimizar exige mexer em cada handler.
Recommendation: Concentrar consultas e escritas em métodos dos models (ex.: `Task.search(...)`, `Task.count_by_status()`, `User.find_by_email`) chamados pelos controllers.
Playbook: P-04

### #8 [HIGH] Acoplamento sem composition root e efeitos colaterais no import (AP-10)
File: app.py:9-31
File: seed.py:2
Description: `app = Flask(__name__)` em nível de módulo, config fixa e `db.create_all()` executado ao importar `app`; `seed.py` importa `app` e com isso dispara todo o wiring.
Impact: Impossível criar a app com outra config (ex.: banco de teste) e importar o módulo já cria tabelas.
Recommendation: `create_app(config)` em `app.py` registrando config, banco, error handlers e blueprints; `python app.py` e `seed.py` usam a factory.
Playbook: P-14

### #9 [HIGH] Deleção que deixa órfãos e escrita multi-etapa sem transação (AP-11)
File: routes/report_routes.py:217-219
File: seed.py:11-14, 37, 63, 92
Description: `delete_category` apaga a categoria sem tratar as tasks que referenciam `category_id` (SQLite não impõe FK por padrão), deixando IDs pendentes. O seed apaga todas as tabelas e repopula em 4 commits separados.
Impact: Tasks apontam para categorias inexistentes; uma falha no meio do seed deixa o banco vazio ou parcial.
Recommendation: Dentro de uma única transação, desassociar as tasks (`category_id = None`) antes de apagar a categoria; seed em uma transação única.
Playbook: P-09

> **Errata (Fase 3):** a parte "deleção deixa órfãos" estava incorreta. Um teste com o código original mostrou que o relacionamento `Category.tasks` (backref, sem `passive_deletes`) faz o SQLAlchemy zerar `category_id` das tasks no mesmo flush do `DELETE`. Só a parte do seed (4 commits separados) era um problema real, e foi corrigida.

### #10 [MEDIUM] Queries N+1 e carga desnecessária (AP-13)
File: routes/task_routes.py:41-57, 275-287
File: routes/user_routes.py:22, 140-142
File: routes/report_routes.py:15-30, 53-61, 159-163
Description: `get_tasks` faz `User.query.get` e `Category.query.get` por task; `get_users` usa `len(u.tasks)` (lazy load por usuário); `summary_report` faz 12 `count()` separados + uma query por usuário; `get_categories` conta tasks por categoria; `task_stats` carrega todas as tasks para contar atrasadas.
Impact: O número de queries cresce linearmente com os dados; endpoints de relatório degradam rapidamente.
Recommendation: Agregações com `func.count` + `group_by`, `joinedload` para user/category e contagem de atrasadas com filtro no banco.
Playbook: P-08

### #11 [MEDIUM] Código e validação duplicados (AP-14)
File: routes/task_routes.py:17-39, 71-80, 110, 177, 283-287
File: routes/user_routes.py:61, 71, 106, 120, 162-180
File: routes/report_routes.py:34-36, 132-135
File: models/task.py:38-60; utils/helpers.py:19-23, 57-116
Description: A regra de "atrasada" é reimplementada 6 vezes apesar de `Task.is_overdue()`; a serialização de task é montada à mão em `task_routes.py:17-28` e `user_routes.py:162-169` apesar de `to_dict()`; a lista de status aparece em 4 lugares, a regex de email em 3, a validação de create/update de task divergente de `process_task_data`.
Impact: Correções precisam ser replicadas e já divergem (ex.: update de título não faz `strip`, create sim no helper; helper aceita `DD/MM/YYYY`, rotas não).
Recommendation: Centralizar regras no model (`is_overdue`, serialização) e validações/constantes num módulo `utils/validators.py` + `utils/constants.py`, reaproveitado por create e update.
Playbook: P-11

### #12 [MEDIUM] Validação de entrada ausente ou fraca (AP-15)
File: routes/task_routes.py:96, 113, 141-142, 167, 182, 210-211, 261, 264
File: routes/user_routes.py:102-103, 115, 124-125
File: routes/report_routes.py:196-202
Description: `priority < 1` com string e `len(title)` com número lançam `TypeError` → 500; `int(priority)`/`int(user_id)` em `/tasks/search` lançam `ValueError` → 500; `update_category` usa `'name' in data` com `data` possivelmente `None` → 500; `name`, `active`, `color` e itens de `tags` não são validados.
Impact: Requisições malformadas derrubam o handler com 500 e permitem gravar dados inválidos (ex.: `active: "abc"`).
Recommendation: Validadores puros que verificam presença, tipo e faixa e respondem 400 com mensagem clara.
Playbook: P-11

### #13 [MEDIUM] Tratamento de erro descentralizado (AP-16)
File: routes/task_routes.py:62-63, 137, 151-154, 204, 221-223, 236-238
File: routes/user_routes.py:87-90, 130-132, 149-151
File: routes/report_routes.py:186-188, 207-209, 221-223
File: utils/helpers.py:46, 49, 88
Description: `except:` nu (captura até `KeyboardInterrupt`/`SystemExit`) e blocos try/rollback copiados em cada handler; `get_tasks` engole qualquer erro; não há `errorhandler` global, então erros fora dos try viram páginas HTML 500 do Flask.
Impact: Falhas ficam invisíveis, formato de erro inconsistente (JSON vs HTML) e duplicação em todo handler.
Recommendation: Exceções de domínio (`ValidationError`, `NotFoundError`...) + `register_error_handler` centralizado devolvendo JSON e logando a exceção; `except` específicos onde necessários.
Playbook: P-05

### #14 [MEDIUM] Deprecated API: datetime.utcnow() (AP-18)
File: models/category.py:11; models/task.py:15, 16, 52
File: routes/task_routes.py:31, 72, 215, 285; routes/user_routes.py:172
File: routes/report_routes.py:35, 42, 45, 71, 133
File: services/notification_service.py:35; utils/helpers.py:38; seed.py:66-74
Description: `datetime.utcnow()` está deprecated desde Python 3.12 (o ambiente usa 3.14) e retorna datetime naive.
Impact: DeprecationWarning em cada chamada e remoção futura; mistura de datetimes naive/aware é fonte de bugs.
Recommendation: Helper único `utils/dates.utcnow()` baseado em `datetime.now(timezone.utc)` (normalizado para naive UTC para manter o formato serializado e a comparação com colunas existentes).
Playbook: P-12

### #15 [MEDIUM] Deprecated API: Model.query.get() (AP-18)
File: routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227
File: routes/user_routes.py:29, 94, 136, 155
File: routes/report_routes.py:105, 192, 213
Description: `Query.get()` é API legada desde SQLAlchemy 2.0 (Flask-SQLAlchemy 3.x) e emite `LegacyAPIWarning`.
Impact: Warnings em runtime e quebra em versões futuras do SQLAlchemy.
Recommendation: Substituir por `db.session.get(Model, id)` dentro de métodos do model (ex.: `Task.get_by_id`).
Playbook: P-12

### #16 [LOW] Código morto (AP-21)
File: services/notification_service.py:1-48
File: utils/helpers.py:9-116
File: models/task.py:3, 38-48; models/user.py:34-38
File: app.py:7; routes/task_routes.py:7; routes/user_routes.py:6; routes/report_routes.py:7-8
Description: `NotificationService` nunca é importado; nenhuma função de `utils/helpers.py` é usada (`format_date`/`calculate_percentage` importados e ignorados); `Task.validate_status`, `validate_priority` e `User.is_admin` sem chamadas; imports não usados (`os, sys, json`, `time`, `hashlib`...). `requirements.txt` declara `marshmallow`, `requests` e `python-dotenv` sem uso.
Impact: Ruído que esconde a lógica real e dá falsa impressão de camadas existentes (helpers ignorados alimentam #11).
Recommendation: Reaproveitar o que for útil nas novas camadas (validação, percentuais) e remover o restante; o serviço de notificação não está ligado a nenhum fluxo (removê-lo; não muda o contrato).
Playbook: P-15

### #17 [LOW] Magic numbers e strings (AP-19)
File: routes/task_routes.py:96, 99, 104, 110, 113, 177, 182
File: routes/user_routes.py:64, 71, 115, 120
File: routes/report_routes.py:24-28, 45, 129
Description: Limites `3`/`200` do título, `4` da senha, prioridades `1..5` e default `3`, `days=7`, `priority <= 2` como "alta" e strings de status/roles soltas; as constantes já existem em `utils/helpers.py:110-116` mas não são usadas.
Impact: Mudar uma regra exige caçar literais em vários arquivos.
Recommendation: `utils/constants.py` com nomes explícitos (`TASK_STATUSES`, `MIN_TITLE_LENGTH`, `RECENT_ACTIVITY_DAYS`, ...).
Playbook: P-13

### #18 [LOW] Nomenclatura críptica (AP-20)
File: routes/report_routes.py:24-28, 192
File: models/category.py:14; models/task.py:45
File: routes/task_routes.py:16, 51
Description: `p1`..`p5` para contagens por prioridade, `d`, `p`, `t`, `cat` fora de escopos triviais.
Impact: Leitura mais lenta e propensa a erro.
Recommendation: Nomes descritivos internamente, mantendo os nomes dos campos JSON (contrato).
Playbook: P-13

### #19 [LOW] Saída padrão como log (AP-22)
File: routes/task_routes.py:149, 153, 219, 234
File: routes/user_routes.py:83, 89, 147
File: services/notification_service.py:21, 24; utils/helpers.py:39-41
Description: `print(...)` para registrar criação/deleção e erros, sem nível nem timestamp.
Impact: Logs impossíveis de filtrar ou desligar; erros misturados com eventos.
Recommendation: `logging.getLogger(__name__)` configurado uma vez no composition root com nível vindo da config.
Playbook: P-13

## Architecture Notes
- As pastas `models/`, `routes/`, `services/` e `utils/` existem, mas só `models/` cumpre seu papel (entidades ORM); falta a camada de controllers e as rotas acumulam regras, consultas e serialização.
- `services/notification_service.py` e `utils/helpers.py` são estrutura morta: implementam validação, constantes e notificação que as rotas reimplementam ou ignoram.
- `report_routes.py` mistura relatórios com o CRUD de categorias — dois domínios num Blueprint.
- `app.py` não tem factory: config fixa, banco criado no import e nenhum error handler/middleware global.
- Alvo: `config/` + `models/` (com `database.py` e consultas) + `controllers/` + `routes/` finos (task, user, category, report) + `middlewares/` (erros, auth) + `utils/` (constants, validators, dates, security), mantendo `python app.py` e `python seed.py`.

================================
Total: 19 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
  y              → corrige todos os achados
  n              → encerra sem modificar nenhum arquivo
  y, skip 3,7    → corrige todos exceto os achados #3 e #7
