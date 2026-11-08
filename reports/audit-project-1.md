```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python (versão não declarada; ambiente: 3.14.4)
Framework:     Flask 3.1.1
Dependencies:  flask==3.1.1, flask-cors==5.0.1
Database:      SQLite (arquivo loja.db) + driver cru (sqlite3, SQL em strings)
Domain:        API de e-commerce — produtos, usuários (login), pedidos com itens e relatório de vendas
Architecture:  Camadas nominais (pseudo-MVC) — existem app.py/controllers.py/models.py, mas app.py e controllers.py executam SQL direto, models.py concentra CRUD de 4 entidades + regras (desconto, estoque) e não há config nem middlewares
Entry point:   app.py (build: n/a, start: python app.py, porta 5000)
Source files:  4 files analyzed | ~780 lines of code
DB tables:     produtos, usuarios, pedidos, itens_pedido
Endpoints:     19 endpoints mapeados
Stack guide:   references/stacks/python.md
================================
```

| Endpoint | Local |
|---|---|
| GET /produtos | app.py:11 |
| GET /produtos/busca | app.py:12 |
| GET /produtos/<id> | app.py:13 |
| POST /produtos | app.py:14 |
| PUT /produtos/<id> | app.py:15 |
| DELETE /produtos/<id> | app.py:16 (destrutivo) |
| GET /usuarios | app.py:18 |
| GET /usuarios/<id> | app.py:19 |
| POST /usuarios | app.py:20 |
| POST /login | app.py:21 |
| POST /pedidos | app.py:23 |
| GET /pedidos | app.py:24 |
| GET /pedidos/usuario/<usuario_id> | app.py:25 |
| PUT /pedidos/<pedido_id>/status | app.py:26 |
| GET /relatorios/vendas | app.py:28 |
| GET /health | app.py:30 |
| GET / | app.py:32 |
| POST /admin/reset-db | app.py:47 (destrutivo) |
| POST /admin/query | app.py:59 (perigoso: SQL arbitrário) |

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python 3.14 (não declarada) + Flask 3.1.1 | DB: SQLite (sqlite3 cru)
Files:   4 analyzed | ~780 lines of code
Date:    2026-11-07

## Summary
CRITICAL: 5 | HIGH: 8 | MEDIUM: 3 | LOW: 4

| # | Severity | Anti-pattern | Location |
|---|----------|--------------|----------|
| 1 | CRITICAL | SQL Injection | models.py:28, 48-49, 58-60, 68, 92, 110, 127-128 (+ 10 trechos) |
| 2 | CRITICAL | Endpoints admin sem proteção (SQL arbitrário / reset) | app.py:47-57, 59-78 |
| 3 | CRITICAL | Segredo hardcoded | app.py:7; controllers.py:289 |
| 4 | CRITICAL | Senhas em texto puro | models.py:110, 126-128; database.py:163-171 |
| 5 | CRITICAL | Exposição de dados sensíveis | models.py:83, 99; controllers.py:285-289 |
| 6 | HIGH | Configuração insegura (debug, CORS, bind) | app.py:8, 9, 88 |
| 7 | HIGH | Erro interno vazado / try-except em todo handler | controllers.py:10-12, 21-22 (+ 14 handlers); app.py:77-78 |
| 8 | HIGH | God Module de dados | models.py:1-314 |
| 9 | HIGH | Lógica de negócio no controller | controllers.py:24-62, 188-220, 237-255 |
| 10 | HIGH | Acesso a dados fora do Model | app.py:49-55, 66-76; controllers.py:266-274 |
| 11 | HIGH | Conexão global compartilhada | database.py:4, 7-10 |
| 12 | HIGH | Sem composition root / efeitos colaterais no import | app.py:6-30; database.py:7-84 |
| 13 | HIGH | Escrita multi-etapa sem transação | models.py:133-169 |
| 14 | MEDIUM | Queries N+1 | models.py:187-199, 219-231, 239-254 |
| 15 | MEDIUM | Código e validação duplicados | models.py:12-21, 31-40, 304-313, 171-233; controllers.py:28-50, 72-90 |
| 16 | MEDIUM | Validação de entrada ausente/fraca | controllers.py:43-50, 118-121, 169-171, 239-240; models.py:139-146 |
| 17 | LOW | Magic numbers e strings | models.py:257-262; controllers.py:47-52, 242 |
| 18 | LOW | Nomenclatura ruim | models.py:187-193, 219-225; controllers.py:56, 160 |
| 19 | LOW | Código morto (imports não usados) | models.py:2; database.py:2; controllers.py:268 |
| 20 | LOW | print() como log / notificações simuladas | controllers.py:8, 11, 57, 208-210 (+ 9 linhas); app.py:56, 83-86 |

## Findings

### #1 [CRITICAL] SQL Injection (AP-02)
File: models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155, 158-160, 164-165, 174, 188, 192, 220, 224, 280, 291-297
Description: Todas as consultas do módulo de dados concatenam valores externos na string SQL — ex.: `login_usuario` monta `"... WHERE email = '" + email + "' AND senha = '" + senha + "'"` e `buscar_produtos` concatena `termo`/`categoria` da query string. O contraste com o seed parametrizado (`database.py:158-171`, `?`) mostra que o driver suporta placeholders.
Impact: Login burlável com `' OR '1'='1' --`; leitura, alteração ou destruição de qualquer tabela via body ou query string.
Recommendation: Usar placeholders `?` do `sqlite3` em todas as consultas, montando os filtros dinâmicos de `buscar_produtos` com lista de condições + lista de parâmetros.
Playbook: P-02

### #2 [CRITICAL] Endpoints administrativos sem proteção (AP-04)
File: app.py:47-57, 59-78
Description: `POST /admin/reset-db` executa `DELETE FROM` sem WHERE em todas as tabelas e `POST /admin/query` executa (e commita) qualquer SQL recebido em `dados["sql"]`; não há nenhuma autenticação/autorização no projeto.
Impact: Qualquer cliente da rede apaga o banco inteiro ou executa SQL arbitrário (exfiltração de senhas, escalada de privilégio).
Recommendation: Manter as rotas, mas desabilitá-las por padrão via flag de configuração (`ENABLE_ADMIN_ROUTES=false` → 403) e exigir token admin quando habilitadas, com decorator dedicado.
Playbook: P-07

### #3 [CRITICAL] Segredo hardcoded (AP-01)
File: app.py:7; controllers.py:289
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` está fixo no código versionado e o mesmo literal é repetido na resposta do `health_check`.
Impact: Quem lê o repositório (ou chama `/health`) obtém a chave de assinatura de sessão do Flask; não é possível rotacioná-la sem deploy.
Recommendation: Ler `SECRET_KEY` de variável de ambiente num módulo `config`, com default apenas para desenvolvimento, e documentar em `.env.example`.
Playbook: P-01

### #4 [CRITICAL] Senhas armazenadas em texto puro (AP-05)
File: models.py:110, 126-128; database.py:163-171
Description: `criar_usuario` grava `senha` exatamente como recebida, o seed grava `admin123`/`123456`/`senha123` em claro e `login_usuario` compara a senha por igualdade dentro do SQL.
Impact: Qualquer vazamento do banco (trivial via #1, #2 ou #5) expõe todas as senhas reutilizáveis dos usuários.
Recommendation: Gravar com `werkzeug.security.generate_password_hash` (scrypt/pbkdf2 com salt) e verificar com `check_password_hash`; manter compatibilidade com registros legados em claro via rehash no login.
Playbook: P-06

### #5 [CRITICAL] Exposição de dados sensíveis (AP-06)
File: models.py:83, 99; controllers.py:285-289
Description: As serializações de usuário incluem `"senha": row["senha"]`, devolvida por `GET /usuarios` e `GET /usuarios/<id>`; `GET /health` retorna `secret_key`, `db_path` e `debug`.
Impact: Qualquer cliente lista as senhas de todos os usuários (inclusive do admin) e obtém a chave secreta e detalhes internos do servidor.
Recommendation: Serializador único de usuário sem o campo `senha`; `/health` devolve apenas status e contagens.
Playbook: P-06

### #6 [HIGH] Configuração insegura de execução (AP-12)
File: app.py:8, 9, 85, 88
Description: `DEBUG = True` e `app.run(host="0.0.0.0", port=5000, debug=True)` fixos no código, e `CORS(app)` libera qualquer origem.
Impact: O debugger interativo do Werkzeug exposto em todas as interfaces permite execução remota de código; porta e modo não são configuráveis por ambiente.
Recommendation: Ler `DEBUG`, `HOST`, `PORT` e `CORS_ORIGINS` da config com defaults seguros (`debug=False`, `127.0.0.1`).
Playbook: P-01

### #7 [HIGH] Tratamento de erro descentralizado com vazamento de erro interno (AP-16)
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292; app.py:77-78
Description: Todo handler repete `except Exception as e: return jsonify({"erro": str(e)}), 500`. Severidade elevada de MEDIUM para HIGH porque `str(e)` de `sqlite3` devolve fragmentos de SQL (ex.: `near "x": syntax error`), o que facilita explorar o #1.
Impact: Mensagens internas e de SQL chegam ao cliente; 17 cópias do mesmo bloco para manter.
Recommendation: Error handler centralizado (`@app.errorhandler`) registrado na app factory, com exceções de domínio (`ValidationError` → 400, `NotFoundError` → 404) e resposta genérica para 500, logando o detalhe no servidor.
Playbook: P-05

### #8 [HIGH] God Module na camada de dados (AP-03)
File: models.py:1-314
Description: Um único módulo concentra CRUD de produtos, usuários, pedidos e itens, autenticação (`login_usuario`), regra de estoque/total (`criar_pedido`, 139-146) e regra de desconto do relatório (`relatorio_vendas`, 256-262). Severidade HIGH (não CRITICAL) porque não contém rotas — está em uma camada, mas cobre 4 domínios e regras de negócio.
Impact: Qualquer mudança de regra exige mexer no acesso a dados; impossível testar a regra de desconto ou de estoque sem banco.
Recommendation: Dividir em `models/` por entidade (só acesso a dados) e mover regras (estoque, desconto, notificações) para `services/`.
Playbook: P-03

### #9 [HIGH] Lógica de negócio no controller (AP-07)
File: controllers.py:24-62, 188-220, 237-255
Description: `criar_produto` contém regras de domínio (categorias válidas, limites de nome, preço/estoque não-negativos) inline; `criar_pedido` e `atualizar_status_pedido` disparam as "notificações" de email/SMS/push e de aprovação/cancelamento diretamente no handler.
Impact: Regras não reutilizáveis nem testáveis sem HTTP; o comentário "Devolver estoque" no cancelamento indica regra que deveria existir e não está em lugar nenhum.
Recommendation: Mover validação para `utils/validators` e o fluxo de pedido + notificações para `services/pedido_service` (com um `notificacao_service`), deixando o controller só traduzir request/response.
Playbook: P-04

### #10 [HIGH] Acesso a dados fora da camada Model (AP-08)
File: app.py:49-55, 66-76; controllers.py:266-274
Description: `reset_database` e `executar_query` em `app.py` e `health_check` em `controllers.py` chamam `get_db()` e `cursor.execute(...)` diretamente.
Impact: SQL espalhado em três camadas; mudanças de schema exigem caçar consultas fora do model.
Recommendation: Criar funções no model (`sistema_model`: `reset`, `executar_sql`, `contagens`) e chamá-las a partir dos controllers.
Playbook: P-04

### #11 [HIGH] Conexão global compartilhada e mutável (AP-09)
File: database.py:4, 7-10
Description: `db_connection = None` global é reaproveitado por todas as requisições com `check_same_thread=False`; o servidor Flask é multi-thread por padrão.
Impact: Requisições concorrentes compartilham cursor/transação — um `commit()` de uma requisição efetiva escritas pendentes de outra; risco de `ProgrammingError` e corrupção de estado.
Recommendation: Uma conexão por requisição em `flask.g`, fechada em `teardown_appcontext`.
Playbook: P-14

### #12 [HIGH] Acoplamento sem composition root (AP-10)
File: app.py:6-30; database.py:7-84
Description: `app = Flask(__name__)` e o registro de rotas acontecem no import do módulo, sem `create_app`; `get_db()` cria schema e roda seed como efeito colateral da primeira chamada, e todos os módulos importam essa função global.
Impact: Impossível criar a app com outra config/banco (testes, ambientes); o primeiro request concorrente pode disparar a criação de schema.
Recommendation: `create_app(config)` em `app.py` que inicializa o banco (schema + seed) explicitamente, registra Blueprints, middlewares e error handlers; `python app.py` continua funcionando.
Playbook: P-14

### #13 [HIGH] Escrita multi-etapa sem transação (AP-11)
File: models.py:133-169
Description: `criar_pedido` insere o pedido, insere cada item e decrementa estoque em várias instruções sem `rollback` em caso de erro; a checagem de estoque (144) e o decremento (163-166) não são atômicos.
Impact: Uma exceção no meio deixa escritas pendentes na conexão global, que o próximo `commit()` de outra requisição efetiva (pedido sem itens, estoque baixado parcialmente); pedidos concorrentes podem vender estoque inexistente.
Recommendation: Executar o fluxo em `with conn:` (commit/rollback automático do `sqlite3`) e decrementar com `UPDATE ... WHERE id = ? AND estoque >= ?`, verificando `rowcount`.
Playbook: P-09

### #14 [MEDIUM] Queries N+1 e agregações separadas (AP-13)
File: models.py:187-199, 219-231, 239-254, 155
Description: `get_pedidos_usuario` e `get_todos_pedidos` fazem 1 query por pedido para itens e mais 1 por item para o nome do produto; `relatorio_vendas` faz 5 queries separadas onde uma agregação basta; `criar_pedido` relê o preço de cada produto já lido no primeiro loop.
Impact: `GET /pedidos` cresce para 1 + P + I queries; degrada linearmente com o volume.
Recommendation: Um `JOIN itens_pedido/produtos` filtrado pelos ids dos pedidos agrupado em memória; relatório com `COUNT/SUM` + `SUM(CASE WHEN status=...)` numa única query.
Playbook: P-08

### #15 [MEDIUM] Código e validação duplicados (AP-14)
File: models.py:12-21, 31-40, 304-313, 79-86, 95-102, 171-201, 203-233; controllers.py:28-50, 72-90
Description: O mapeamento linha→dict de produto aparece 3 vezes e o de usuário 2 vezes; `get_pedidos_usuario` e `get_todos_pedidos` são idênticas exceto pelo WHERE; a validação de produto é copiada entre criar e atualizar com divergência (o update não valida tamanho do nome nem categoria).
Impact: Correções precisam ser replicadas; a divergência já permite gravar categoria inválida via `PUT /produtos/<id>`.
Recommendation: Serializadores únicos por entidade, uma função de listagem de pedidos com filtro opcional e um validador de produto compartilhado.
Playbook: P-11

### #16 [MEDIUM] Validação de entrada ausente ou fraca (AP-15)
File: controllers.py:43-50, 118-121, 169-171, 239-240; models.py:139-146
Description: `preco < 0` com `preco` string lança `TypeError` (500); `float(preco_min)` com valor não numérico lança `ValueError` (500); `login` e `atualizar_status_pedido` chamam `dados.get` com body ausente (`AttributeError` → 500); itens de pedido sem `produto_id`/`quantidade` geram `KeyError` e `quantidade` negativa ou zero é aceita (total negativo e estoque aumentado).
Impact: Entradas malformadas viram 500; pedidos com quantidade negativa manipulam estoque e faturamento.
Recommendation: Validadores puros em `utils/validators` (tipos numéricos, inteiros positivos, body obrigatório) lançando `ValidationError` → 400.
Playbook: P-11

### #17 [LOW] Magic numbers e strings (AP-19)
File: models.py:150, 247-253, 257-262; controllers.py:47-52, 242, 247-249; app.py:36, 85, 88; controllers.py:285
Description: Faixas e percentuais de desconto (`10000/5000/1000`, `0.1/0.05/0.02`), limites de nome (2/200), lista de categorias, strings de status de pedido repetidas em models e controllers, versão `"1.0.0"` duplicada e porta 5000.
Impact: Regras de negócio escondidas em literais; mudar um status ou faixa exige editar vários arquivos.
Recommendation: Centralizar em `utils/constants.py` (status, categorias, faixas de desconto, limites).
Playbook: P-13

### #18 [LOW] Nomenclatura ruim (AP-20)
File: models.py:187-193, 219-225; controllers.py:56, 160
Description: `cursor2`/`cursor3`/`prod` com sufixos numéricos e o parâmetro/variável `id` sombreando o builtin (`id = models.criar_produto(...)`).
Impact: Leitura mais difícil e risco de bug ao usar `id()` no mesmo escopo.
Recommendation: Renomear internamente (`produto_id`, `itens_rows`...), mantendo os nomes dos parâmetros de rota e campos JSON.
Playbook: P-13

### #19 [LOW] Código morto (AP-21)
File: models.py:2; database.py:2; controllers.py:268
Description: `import sqlite3` em models.py e `import os` em database.py nunca são usados; `cursor.execute("SELECT 1")` no health check tem o resultado descartado.
Impact: Ruído e falsa impressão de dependência.
Recommendation: Remover os imports e a query sem efeito.
Playbook: P-15

### #20 [LOW] Saída padrão como log e notificações simuladas (AP-22)
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250; app.py:56, 83-86
Description: `print()` usado como log de operações e erros, sem nível nem timestamp; o envio de email/SMS/push é "simulado" com `print` no meio do fluxo; logs de login/criação incluem o email do usuário.
Impact: Logs não filtráveis por nível nem desativáveis em produção; notificações não têm ponto de extensão.
Recommendation: `logging.getLogger(__name__)` configurado no composition root e um `notificacao_service` que encapsula os envios.
Playbook: P-13

## Architecture Notes
- Há três arquivos com nomes de camada (`app.py`, `controllers.py`, `models.py`) + `database.py`, mas as responsabilidades vazam: SQL em `app.py` e `controllers.py`, regras de negócio em `models.py` e nos controllers.
- Faltam as camadas de config (segredos e flags estão no código), routes/Blueprints (rotas e handlers admin vivem em `app.py`), services, middlewares (sem error handler central, sem autenticação) e utils (validação/constantes).
- Não existe autenticação no projeto: `/login` apenas devolve os dados do usuário, sem token. As rotas admin serão protegidas por flag + token de config; demais rotas mantêm o contrato público.
- Nenhuma API deprecated foi encontrada para Python 3.14 / Flask 3.1.1 (sem `utcnow`, `before_first_request`, conversores de data do `sqlite3` etc.).
- Plano da Fase 3: `config/`, `models/` (database + um model por entidade), `services/` (pedido, notificação), `controllers/`, `routes/` (Blueprints), `middlewares/` (erros, admin), `utils/` (validators, constants, security), com `app.py` como composition root `create_app()`.

================================
Total: 20 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
  y              → corrige todos os achados
  n              → encerra sem modificar nenhum arquivo
  y, skip 3,7    → corrige todos exceto os achados #3 e #7
