================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3.x (não declarada; venv 3.14.4) + Flask 3.0.0 | DB: SQLite (Flask-SQLAlchemy 3.1.1 / SQLAlchemy 2.1)
Files:   15 analyzed | ~1158 lines of code
Date:    2026-11-01

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 6 | LOW: 4

| # | Severity | Anti-pattern | Location |
|---|----------|--------------|----------|
| 1 | CRITICAL | Hash de senha exposto nas respostas | models/user.py:21 |
| 2 | CRITICAL | Senhas com MD5 sem salt | models/user.py:27-32 |
| 3 | CRITICAL | Sem autenticação/autorização + token falso + escalada de role | routes/user_routes.py:52, 71-72, 119-122, 210 |
| 4 | CRITICAL | Segredos hardcoded | app.py:13; services/notification_service.py:7-10 |
| 5 | HIGH | Configuração insegura de execução (debug, bind, CORS) | app.py:15, 34 |
| 6 | HIGH | Lógica de negócio nas rotas (Fat Controller) | routes/*.py |
| 7 | HIGH | Acesso a dados nas rotas | routes/*.py |
| 8 | HIGH | App criada no import, sem factory nem DI | app.py:9-31; seed.py:2 |
| 9 | HIGH | DELETE de categoria deixa tasks órfãs | routes/report_routes.py:211-223 |
| 10 | MEDIUM | Queries N+1 e contagens em memória | routes/task_routes.py:41-57; routes/user_routes.py:22; routes/report_routes.py:15-28, 53-68, 163 |
| 11 | MEDIUM | Lógica e validação duplicadas | routes/*.py; models/task.py:50-60; utils/helpers.py:57-108 |
| 12 | MEDIUM | Validação de entrada fraca (500 em entrada inválida) | routes/task_routes.py:113, 167, 182, 261, 264; routes/report_routes.py:196-197 |
| 13 | MEDIUM | Tratamento de erro descentralizado / `except:` genérico | routes/*.py; utils/helpers.py:46, 49, 88 |
| 14 | MEDIUM | Deprecated API: `datetime.utcnow()` | models/*.py; routes/*.py; utils/helpers.py:38 |
| 15 | MEDIUM | Deprecated API: `Model.query.get()` | routes/*.py |
| 16 | LOW | Magic numbers e strings | routes/*.py; models/task.py:39, 46 |
| 17 | LOW | Nomenclatura críptica | routes/report_routes.py:24-28; models/task.py:45 |
| 18 | LOW | Código morto (service, helpers, imports, deps) | services/notification_service.py; utils/helpers.py; vários imports |
| 19 | LOW | `print` como log | routes/task_routes.py:149, 153, 219, 234; routes/user_routes.py:83, 89, 147 |

## Findings

### #1 [CRITICAL] Exposição de dados sensíveis — hash de senha nas respostas (AP-06)
File: models/user.py:16-25
File: routes/user_routes.py:33, 85-86, 129, 209
Description: `User.to_dict()` inclui `'password': self.password`, e esse dict é devolvido por `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`.
Impact: Qualquer cliente obtém o hash MD5 de qualquer usuário (sem auth, ver #3); com MD5 sem salt o hash é revertido em segundos por rainbow tables.
Recommendation: Remover `password` da serialização pública de `User` (método `to_dict` seguro) e nunca serializar o hash.
Playbook: P-06

### #2 [CRITICAL] Armazenamento inseguro de senhas — MD5 sem salt (AP-05)
File: models/user.py:3, 27-32
File: seed.py:19, 26, 33
Description: `set_password` grava `hashlib.md5(pwd.encode()).hexdigest()` e `check_password` compara com `==` (sem tempo constante). O seed cria senhas como `'1234'`, e a política mínima é 4 caracteres (`routes/user_routes.py:64`).
Impact: Vazamento do banco (ou de #1) entrega todas as senhas em texto claro; comparação não-constante permite timing attack.
Recommendation: Usar `werkzeug.security.generate_password_hash`/`check_password_hash` (scrypt/pbkdf2 com salt); manter login de hashes MD5 legados com rehash transparente no login.
Playbook: P-06

### #3 [CRITICAL] Endpoints sem autenticação, token falso e escalada de privilégio (AP-04)
File: routes/user_routes.py:52, 71-72, 119-122, 134-151, 210
File: routes/report_routes.py:211-223
File: routes/task_routes.py:225-238
Description: Nenhuma rota exige autenticação; `POST /login` devolve `'fake-jwt-token-' + str(user.id)` (previsível e nunca verificado); `POST /users` e `PUT /users/<id>` aceitam `role: "admin"` direto do body; deleções de usuários/categorias/tasks são públicas.
Impact: Qualquer pessoa cria um admin, apaga usuários (e suas tasks em cascata) ou forja tokens trocando o id.
Recommendation: Emitir token assinado (itsdangerous, já dependência do Flask, com `SECRET_KEY`) e criar decorator `admin_required` que, quando habilitado por config, protege a atribuição de `role` privilegiado e as rotas destrutivas de usuário.
Playbook: P-07

### #4 [CRITICAL] Credenciais e segredos hardcoded (AP-01)
File: app.py:13
File: services/notification_service.py:7-10
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` e credenciais SMTP `email_user='taskmanager@gmail.com'`, `email_password='senha123'` fixas no código versionado.
Impact: Quem lê o repositório assina sessões/tokens válidos e usa a conta de email; rotação exige deploy.
Recommendation: Módulo `config/` lendo `os.environ` (via `python-dotenv`, já dependência), sem default para segredos em produção, e `.env.example` documentando as variáveis.
Playbook: P-01

### #5 [HIGH] Configuração insegura de execução (AP-12)
File: app.py:15, 34
File: app.py:11
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` fixo; `CORS(app)` libera qualquer origem; caminho do banco `sqlite:///tasks.db` fixo.
Impact: O debugger Werkzeug exposto em todas as interfaces permite execução remota de código; CORS aberto permite que qualquer site consuma a API.
Recommendation: Ler `DEBUG`, `HOST`, `PORT`, `DATABASE_URL` e `CORS_ORIGINS` da config com defaults seguros (debug off, `127.0.0.1`).
Playbook: P-01

### #6 [HIGH] Lógica de negócio nas rotas — Fat Controller (AP-07)
File: routes/task_routes.py:12-63, 86-154, 157-223, 274-299
File: routes/user_routes.py:43-90, 93-132
File: routes/report_routes.py:13-101, 104-155
Description: Handlers de 40–90 linhas validam, calculam atraso, montam estatísticas e relatórios e serializam entidades à mão; `report_routes.py` ainda hospeda o CRUD de categorias (outro domínio). `utils.helpers.process_task_data` e `Task.is_overdue` existem mas são ignorados.
Impact: Regras não testáveis sem HTTP e impossíveis de reusar; cada mudança de regra precisa ser replicada em várias rotas.
Recommendation: Rotas finas (Blueprints) → controllers/services (`task_service`, `user_service`, `report_service`, `category_service`) com regras; categorias em blueprint próprio mantendo os mesmos caminhos.
Playbook: P-04

### #7 [HIGH] Acesso a dados fora da camada Model (AP-08)
File: routes/task_routes.py:2, 14, 147-148, 218, 232-233, 247-266, 275-281
File: routes/user_routes.py:2, 12, 67, 81-82, 128, 140-146
File: routes/report_routes.py:2, 15-30, 46-56, 159-163, 183-184, 205, 218-219
Description: As rotas importam `db` e chamam `Model.query`, `db.session.add/commit/delete/rollback` diretamente.
Impact: Persistência acoplada ao HTTP; não há ponto único para transações, eager loading ou troca de estratégia de acesso.
Recommendation: Concentrar consultas e escrita em métodos de repositório/model (`models/`), chamados apenas pelos services.
Playbook: P-04

### #8 [HIGH] Acoplamento forte — app criada no import, sem factory (AP-10)
File: app.py:9-31
File: seed.py:2
File: services/notification_service.py:5-10
Description: `app = Flask(__name__)` em nível de módulo, config fixa, `db.create_all()` executado como efeito colateral do import; `seed.py` importa `app` para obter contexto; `NotificationService` instancia suas próprias credenciais.
Impact: Impossível criar instâncias com outra config (testes, outro banco) e importar `app` já toca o banco.
Recommendation: `create_app(config)` como composition root (config → db → CORS → error handlers → blueprints), mantendo `python app.py` funcional; seed usando a factory.
Playbook: P-14

### #9 [HIGH] Deleção deixa registros órfãos (AP-11)
File: routes/report_routes.py:211-223
File: models/task.py:14, 21
Description: `DELETE /categories/<id>` remove a categoria sem tratar `tasks.category_id`; SQLite não aplica FK por padrão e o relacionamento não tem cascade/limpeza.
Impact: Tasks ficam apontando para categoria inexistente (`category_id` pendurado, `category_name` null) — inconsistência permanente.
Recommendation: Na mesma transação, desassociar (`category_id = NULL`) as tasks da categoria antes de deletá-la.
Playbook: P-09

### #10 [MEDIUM] Queries N+1 e carga desnecessária (AP-13)
File: routes/task_routes.py:41-57, 275-287
File: routes/user_routes.py:12-22
File: routes/report_routes.py:15-30, 53-68, 159-163
Description: `GET /tasks` faz `User.query.get` e `Category.query.get` por task; `GET /users` faz lazy load `len(u.tasks)` por usuário; `summary_report` faz uma query por usuário e 13 `count()` separados; `GET /categories` faz um `count()` por categoria; atraso calculado carregando todas as tasks.
Impact: Número de queries cresce linearmente com os dados; relatórios ficam lentos rapidamente.
Recommendation: `joinedload`/`selectinload` nas listagens e agregações `func.count` + `group_by` (status, prioridade, usuário, categoria).
Playbook: P-08

### #11 [MEDIUM] Código e validação duplicados (AP-14)
File: routes/task_routes.py:17-39, 71-80, 110, 177, 284-287
File: routes/user_routes.py:61, 106, 162-180
File: routes/report_routes.py:34-37, 132-135
File: models/task.py:38-60
File: utils/helpers.py:19-23, 57-108, 110
Description: A regra "atrasada" é copiada 6 vezes apesar de `Task.is_overdue()`; a serialização de task é refeita à mão (task_routes 17-28 ≈ `to_dict`); a lista de status aparece 5 vezes; o regex de email está em 2 rotas e em `validate_email`; validação de create/update de task diverge (`update` não faz `strip`, `process_task_data` aceita 2 formatos de data, as rotas só 1).
Impact: Divergências já existentes viram bugs (regras diferentes conforme o endpoint) e toda alteração precisa ser feita em vários lugares.
Recommendation: Uma única regra (`Task.is_overdue`), um único serializer por entidade e validadores centralizados em `utils/validators.py` usados por create e update.
Playbook: P-11

### #12 [MEDIUM] Validação de entrada ausente ou fraca (AP-15)
File: routes/task_routes.py:113, 167, 182, 261, 264
File: routes/report_routes.py:196-202
File: routes/user_routes.py:102-103, 115, 124-125
Description: `priority` string (`"alta"`) causa `TypeError` em `priority < 1`; `title: null` no PUT quebra em `len()`; `?priority=abc` / `?user_id=abc` em `/tasks/search` quebram em `int()`; `PUT /categories/<id>` sem body acessa `'name' in None`; `name` vazio e `active` não-booleano aceitos; `color` nunca validado (`is_valid_color` existe e não é usado).
Impact: Entrada inválida vira `500` (ou dados corrompidos) em vez de `400` com mensagem clara.
Recommendation: Validar tipo/faixa em validadores únicos e responder `400`; checar body nulo em todos os handlers de escrita.
Playbook: P-11

### #13 [MEDIUM] Tratamento de erro descentralizado (AP-16)
File: routes/task_routes.py:62-63, 137, 151-154, 204, 221-223, 236-238
File: routes/user_routes.py:87-90, 130-132, 149-151
File: routes/report_routes.py:186-188, 207-209, 221-223
File: utils/helpers.py:46, 49, 88
Description: `try/except` copiado em cada handler, vários `except:` nus (capturam até `KeyboardInterrupt`), `GET /tasks` engole qualquer erro; não existe `errorhandler` — 404/405/500 do framework saem em HTML, diferente do JSON `{'error': ...}` das rotas.
Impact: Erros são mascarados (difícil diagnosticar) e o formato de erro é inconsistente para o cliente.
Recommendation: Exceções de domínio (`NotFoundError`, `ValidationError`...) + error handler central em `middlewares/` que faz rollback, loga e responde JSON.
Playbook: P-05

### #14 [MEDIUM] Deprecated API: `datetime.utcnow()` (AP-18)
File: models/task.py:15, 16, 52
File: models/user.py:14
File: models/category.py:11
File: routes/task_routes.py:31, 72, 215, 285
File: routes/user_routes.py:172
File: routes/report_routes.py:35, 42, 45, 71, 133
File: utils/helpers.py:38
File: services/notification_service.py:35
File: seed.py:66, 67, 69, 70, 74
Description: `datetime.utcnow()` está deprecated desde Python 3.12 (o ambiente usa 3.14) e devolve datetime naive.
Impact: `DeprecationWarning` em runtime e remoção futura; mistura de naive/aware tende a gerar `TypeError` em comparações.
Recommendation: Helper único `utc_now()` baseado em `datetime.now(timezone.utc)` (disponível desde 3.2), normalizado para naive UTC ao comparar com colunas `DateTime` sem tz para manter o formato atual das respostas.
Playbook: P-12

### #15 [MEDIUM] Deprecated API: `Model.query.get()` (AP-18)
File: routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227
File: routes/user_routes.py:29, 94, 136, 155
File: routes/report_routes.py:105, 192, 213
Description: `Query.get()` é API legada desde SQLAlchemy 2.0 (o ambiente resolve 2.1.6) e emite `LegacyAPIWarning`; Flask-SQLAlchemy 3.x recomenda `db.session.get`.
Impact: Warnings em runtime e quebra quando a API `Query` legada for removida.
Recommendation: `db.session.get(Model, id)` (SQLAlchemy 1.4+/2.0) dentro da camada Model.
Playbook: P-12

### #16 [LOW] Magic numbers e strings (AP-19)
File: routes/task_routes.py:32, 96, 99, 104, 110, 113, 167, 169, 177, 182
File: routes/user_routes.py:64, 71, 115, 120
File: routes/report_routes.py:24-28, 129, 180
File: models/task.py:39, 46
Description: Limites 3/200 de título, prioridade 1–5, default 3, senha mínima 4, `priority <= 2` = "alta", `'#000000'`, status e roles como strings literais; as constantes `VALID_STATUSES`, `MAX_TITLE_LENGTH` etc. existem em `utils/helpers.py:110-116` e não são usadas.
Impact: Mudar uma regra exige caçar literais pelo código; fácil esquecer um.
Recommendation: Constantes de domínio num módulo único (`utils/constants.py`) usadas por validadores, services e models.
Playbook: P-13

### #17 [LOW] Nomenclatura críptica (AP-20)
File: routes/report_routes.py:24-28
File: models/task.py:45
File: utils/helpers.py:83
File: models/category.py:14
Description: `p1`…`p5` para contagens por prioridade, `p` como prioridade, `d` como dict de categoria, além de `t`, `u`, `c`, `cat` em loops longos.
Impact: Leitura lenta; o mapeamento `p1 → 'critical'` fica implícito.
Recommendation: Nomes descritivos internamente (mantendo as chaves JSON `critical`, `high`... do contrato).
Playbook: P-13

### #18 [LOW] Código morto (AP-21)
File: services/notification_service.py:1-48
File: utils/helpers.py:9-55, 57-108, 110-116
File: models/task.py:38-60
File: models/user.py:34-38
File: app.py:7; routes/task_routes.py:7; routes/user_routes.py:6; routes/report_routes.py:7-8; models/task.py:3; utils/helpers.py:3-7
File: requirements.txt:4-5
Description: `NotificationService` nunca é importado; todas as funções de `utils/helpers.py` (inclusive `format_date`/`calculate_percentage`, importadas e não chamadas) e as constantes não são usadas; `Task.validate_status/validate_priority/is_overdue` e `User.is_admin` não têm chamadores; imports não usados (`os, sys, json, time, hashlib`); `marshmallow` e `requests` declarados e não usados.
Impact: Ruído que esconde a lógica real e confunde quem procura onde a regra está (o código "certo" está morto e o duplicado é o ativo).
Recommendation: Reaproveitar a lógica útil (overdue, validações, constantes) nas novas camadas e remover o resto, incluindo o serviço de notificação não ligado e imports/dependências não usados.
Playbook: P-15

### #19 [LOW] Saída padrão como mecanismo de log (AP-22)
File: routes/task_routes.py:149, 153, 219, 234
File: routes/user_routes.py:83, 89, 147
File: utils/helpers.py:39-41
File: services/notification_service.py:21, 24
Description: Eventos e erros registrados com `print(...)`, sem nível nem logger; `user_routes.py:89` imprime a mensagem crua da exceção.
Impact: Sem controle de nível/destino em produção e mistura de erro com log de auditoria.
Recommendation: `logging.getLogger(__name__)` configurado uma vez na factory, com nível vindo da config.
Playbook: P-13

## Architecture Notes
- Existem pastas `models/`, `routes/`, `services/`, `utils/`, mas só `models/` e `routes/` são usados; `routes/` acumula papel de controller, service e repositório.
- Falta camada de controllers/services, de configuração (`config/`) e de middlewares (erro, auth); `database.py` fica na raiz em vez de dentro de `models/`.
- `report_routes.py` mistura dois domínios (relatórios + CRUD de categorias).
- A lógica reaproveitável já escrita (`Task.is_overdue`, `process_task_data`, constantes) está morta enquanto as rotas a reimplementam com divergências.
- Plano provável: `app.py` (factory + start original) → `config/`, `models/` (+ `database.py`), `services/`, `controllers/`, `routes/` (Blueprints finos), `middlewares/`, `utils/`.

## Correção pós-auditoria (Fase 3)
- **#9 era falso positivo.** Teste executado na Fase 3 contra o código original (`DELETE /categories/4` seguido de `GET /tasks`) mostrou que o SQLAlchemy já desassocia as tasks (`category_id = NULL`) na mesma transação, pelo comportamento padrão do backref `Category.tasks` sem cascade de delete. Nenhuma correção foi necessária; o comportamento foi documentado em `models/category.py`.

================================
Total: 19 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
  y              → corrige todos os achados
  n              → encerra sem modificar nenhum arquivo
  y, skip 3,7    → corrige todos exceto os achados #3 e #7
