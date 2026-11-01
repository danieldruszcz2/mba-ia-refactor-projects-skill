================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python 3.14 (não declarada; ambiente) + Flask 3.1.1 | DB: SQLite (sqlite3, SQL cru)
Files:   4 analyzed | ~780 lines of code
Date:    2026-11-01

## Summary
CRITICAL: 5 | HIGH: 8 | MEDIUM: 3 | LOW: 4

| # | Severity | Anti-pattern | Location |
|---|----------|--------------|----------|
| 1 | CRITICAL | SQL Injection por concatenação | models.py:28, 48-49, 58-60, 68, 92, 110, ... |
| 2 | CRITICAL | Endpoints admin destrutivos sem proteção | app.py:47-78 |
| 3 | CRITICAL | Segredo hardcoded (SECRET_KEY) | app.py:7, controllers.py:289 |
| 4 | CRITICAL | Senhas em texto puro | models.py:109-111, 126-129; database.py:76-78 |
| 5 | CRITICAL | Exposição de senha e config sensível | models.py:83, 99; controllers.py:285-289 |
| 6 | HIGH | Configuração de execução insegura | app.py:8, 9, 88 |
| 7 | HIGH | Erro interno (SQL) vazado ao cliente | controllers.py:10-12 (+15 handlers); app.py:77-78 |
| 8 | HIGH | Criação de pedido sem transação | models.py:133-169 |
| 9 | HIGH | God Module na camada de dados | models.py:1-314 |
| 10 | HIGH | Regra de negócio no controller | controllers.py:24-62, 188-220, 237-255 |
| 11 | HIGH | Acesso a dados fora do Model | controllers.py:3, 264-274; app.py:4, 47-78 |
| 12 | HIGH | Conexão global compartilhada | database.py:4-11 |
| 13 | HIGH | Sem composition root / efeitos no import | app.py:6-30; database.py:7-86 |
| 14 | MEDIUM | Validação de entrada ausente/fraca | controllers.py:43-50, 118-121, 169-171, 195-201, 239-245 |
| 15 | MEDIUM | Queries N+1 e agregações separadas | models.py:139-166, 187-193, 219-225, 239-254 |
| 16 | MEDIUM | Código e validação duplicados | models.py:12-21, 31-40, 304-313, 171-233; controllers.py:28-50 vs 72-90 |
| 17 | LOW | Magic numbers e strings | models.py:257-262; controllers.py:47-52, 242 |
| 18 | LOW | Nomenclatura ruim | models.py:187-192, 219-224; controllers.py:14, 56, 64, 98 |
| 19 | LOW | Código morto (imports) | models.py:2; database.py:2 |
| 20 | LOW | print() como log | controllers.py:8, 11, 57, 61, 106, ...; app.py:56, 83-86 |

## Findings

### #1 [CRITICAL] SQL Injection por concatenação (AP-02)
File: models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155, 158-160, 164-165, 174, 188, 192, 220, 224, 280, 291, 293, 295, 297
Description: Praticamente todas as funções de `models.py` montam SQL concatenando valores do body/query (`login_usuario`: `"... WHERE email = '" + email + "' AND senha = '" + senha + "'"`; `buscar_produtos`: `LIKE '%" + termo + "%'`; `criar_produto`, `criar_usuario`, `atualizar_status_pedido` etc.). O contraste com o seed em `database.py:70-83`, que usa placeholders `?`, mostra que o driver já suportava parametrização.
Impact: Login burlável com `' OR '1'='1' --`; `GET /produtos/busca?q=` permite `UNION SELECT` para extrair senhas de `usuarios`; criação de produto/usuário permite alterar ou apagar tabelas.
Recommendation: Usar placeholders `?` do `sqlite3` em todas as consultas, com valores passados como tupla para `cursor.execute`; montar filtros dinâmicos de `buscar_produtos` acumulando cláusulas + lista de parâmetros.
Playbook: P-02

### #2 [CRITICAL] Endpoints administrativos destrutivos sem proteção (AP-04)
File: app.py:47-57, 59-78
Description: `POST /admin/reset-db` executa `DELETE FROM` em todas as tabelas sem WHERE e `POST /admin/query` executa qualquer SQL recebido em `dados["sql"]` (inclusive escrita, com `commit`). Nenhum dos dois exige autenticação; a API não possui mecanismo de auth algum (o que também deixa `/usuarios`, `/pedidos` e `/relatorios/vendas` abertos).
Impact: Qualquer cliente na rede apaga todo o banco ou lê/altera qualquer dado com uma requisição.
Recommendation: Manter as rotas, mas desabilitadas por padrão via `ENABLE_ADMIN_ROUTES=false` (resposta 403) e, quando habilitadas, exigir token admin (`ADMIN_TOKEN` via header) através de um decorator `@admin_required`; mover o SQL para o Model.
Playbook: P-07

### #3 [CRITICAL] Segredo hardcoded (AP-01)
File: app.py:7
File: controllers.py:289
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` está versionado no código, e o mesmo literal é repetido e devolvido pelo `health_check`.
Impact: Quem tem acesso ao repositório (ou ao `/health`) pode forjar sessões/cookies assinados; a chave não pode ser rotacionada sem deploy.
Recommendation: Ler `SECRET_KEY` de variável de ambiente num módulo `config` (`os.environ.get`), com default aleatório apenas para desenvolvimento, e documentar em `.env.example`.
Playbook: P-01

### #4 [CRITICAL] Senhas armazenadas em texto puro (AP-05)
File: models.py:109-111, 126-129
File: database.py:76-78
Description: `criar_usuario` grava `senha` do body sem hash; `login_usuario` compara a senha em texto puro dentro do SQL (`AND senha = '...'`); o seed insere `admin123`, `123456`, `senha123` em claro.
Impact: Qualquer vazamento do banco (ou do `/usuarios`, ver #5, ou via #1) expõe as senhas reais dos usuários.
Recommendation: Gravar com `werkzeug.security.generate_password_hash` (scrypt, com salt) e verificar com `check_password_hash`; para registros legados em texto puro, verificação legada + rehash no login.
Playbook: P-06

### #5 [CRITICAL] Exposição de dados sensíveis em respostas (AP-06)
File: models.py:83, 99
File: controllers.py:285-289
Description: `get_todos_usuarios` e `get_usuario_por_id` incluem o campo `"senha"` no dict serializado por `GET /usuarios` e `GET /usuarios/<id>`; `health_check` devolve `secret_key`, `db_path`, `debug` e `ambiente`.
Impact: Um GET anônimo entrega as senhas de todos os usuários e a chave de assinatura da aplicação.
Recommendation: Serializar usuários sem `senha`; `/health` devolve apenas status, conexão e contagens.
Playbook: P-06

### #6 [HIGH] Configuração de execução insegura (AP-12)
File: app.py:8, 9, 88
Description: `app.config["DEBUG"] = True` e `app.run(host="0.0.0.0", port=5000, debug=True)` fixos no código; `CORS(app)` libera todas as origens.
Impact: O debugger do Werkzeug exposto em todas as interfaces permite execução remota de código; qualquer site pode chamar a API pelo navegador da vítima.
Recommendation: `DEBUG`, `HOST`, `PORT` e `CORS_ORIGINS` vindos de variáveis de ambiente com defaults seguros (debug desligado, host `127.0.0.1`).
Playbook: P-01

### #7 [HIGH] Erro interno vazado ao cliente / tratamento descentralizado (AP-16)
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292
File: app.py:77-78
Description: Todos os 16 handlers repetem `except Exception as e: return jsonify({"erro": str(e)}), 500`, devolvendo a mensagem crua da exceção (incluindo erros de sintaxe SQL do sqlite). Severidade elevada de MEDIUM para HIGH porque vaza detalhes de SQL que facilitam explorar #1.
Impact: Atacante obtém feedback da estrutura das queries; erros de cliente (body inválido) viram 500; formato de erro inconsistente (`/health` usa `detalhes`).
Recommendation: Remover os try/except dos handlers e registrar `@app.errorhandler` centralizado: exceções de validação → 400 com mensagem clara; demais → 500 com mensagem genérica e log do stack no servidor.
Playbook: P-05

### #8 [HIGH] Escrita multi-etapa sem transação (AP-11)
File: models.py:133-169
File: models.py:65-70
Description: `criar_pedido` faz INSERT em `pedidos`, N INSERTs em `itens_pedido` e N UPDATEs de estoque sem `rollback`; como a conexão é global (#12), uma falha no meio deixa escritas pendentes que o próximo `commit` de outra requisição efetiva. A checagem de estoque (139-145) e o débito (163-166) são separados (TOCTOU). `deletar_produto` apaga o produto deixando `itens_pedido` órfãos.
Impact: Pedidos sem itens ou estoque debitado pela metade; overselling sob concorrência.
Recommendation: Envolver o caso de uso em transação (`with conn:` do sqlite3 — commit/rollback automático) e debitar com `UPDATE ... SET estoque = estoque - ? WHERE id = ? AND estoque >= ?`, verificando `rowcount`.
Playbook: P-09

### #9 [HIGH] God Module na camada de dados (AP-03)
File: models.py:1-314
Description: Um único módulo com CRUD de 3 entidades (produtos, usuários, pedidos), autenticação (`login_usuario`), regras de negócio (validação de estoque 139-146, faixas de desconto 256-262) e relatório financeiro. Rebaixado de CRITICAL para HIGH porque não contém rotas — fica todo numa camada, mas mistura domínios e regras.
Impact: Qualquer mudança em um domínio toca o arquivo de todos; regras de negócio não são testáveis sem banco.
Recommendation: Separar em `models/produto_model.py`, `usuario_model.py`, `pedido_model.py`, e mover regras (estoque, desconto) para `services/`.
Playbook: P-03

### #10 [HIGH] Lógica de negócio no controller (AP-07)
File: controllers.py:24-62, 64-96, 188-220, 237-255
Description: `criar_produto`/`atualizar_produto` contêm toda a regra de validação de produto (limites, lista de categorias); `criar_pedido` e `atualizar_status_pedido` disparam "notificações" (email/SMS/push simulados) e decidem efeitos de status (`aprovado`/`cancelado`) dentro do handler HTTP.
Impact: Regras não reutilizáveis nem testáveis sem HTTP; a mensagem "Devolver estoque" do cancelamento nunca é implementada.
Recommendation: Mover validação para `utils/validators.py` e regras/notificações para `services/` (produto, pedido, notificação); controllers só traduzem request → service → response.
Playbook: P-04

### #11 [HIGH] Acesso a dados fora da camada Model (AP-08)
File: controllers.py:3, 264-274
File: app.py:4, 47-57, 59-78
Description: `health_check` executa `SELECT COUNT(*)` diretamente; `app.py` (entry point) importa `get_db` e executa `DELETE FROM` e SQL arbitrário nas rotas admin.
Impact: SQL espalhado em três camadas; impossível trocar/isolar o acesso a dados.
Recommendation: Mover as consultas para funções do Model (`contar_registros`, `resetar_banco`, `executar_sql`) chamadas por controllers.
Playbook: P-04

### #12 [HIGH] Conexão global compartilhada (AP-09)
File: database.py:4-11
Description: `db_connection` é um global de módulo mutado via `global` e aberto com `check_same_thread=False`, compartilhado por todas as requisições e threads do servidor.
Impact: Race conditions entre requisições concorrentes; transação de uma requisição contamina outra (ver #8); testes não isolados.
Recommendation: Conexão por requisição em `flask.g`, fechada em `teardown_appcontext`.
Playbook: P-14

### #13 [HIGH] Acoplamento forte sem composition root (AP-10)
File: app.py:6-30
File: database.py:7-86
File: models.py:1
Description: `app = Flask(__name__)` criado no import, sem `create_app`; a primeira chamada a `get_db()` cria schema e popula seed como efeito colateral; models/controllers importam `get_db` diretamente.
Impact: Não dá para criar a app com outra configuração/banco (testes), e o schema/seed é acoplado ao acesso a dados.
Recommendation: `create_app(config)` montando config, banco (`init_db` explícito no boot), error handlers e Blueprints; schema/seed em módulo próprio.
Playbook: P-14

### #14 [MEDIUM] Validação de entrada ausente ou fraca (AP-15)
File: controllers.py:43-50, 118-121, 169-171, 195-201, 239-245
File: app.py:61-62
File: models.py:144-146
Description: `preco`/`estoque` não têm tipo checado (`"abc" < 0` → TypeError → 500); `float(preco_min)` sem tratamento → 500; `login`, `atualizar_status_pedido` e `/admin/query` chamam `dados.get` com body possivelmente `None` → 500; itens do pedido não são validados (`produto_id` ausente → KeyError 500; `quantidade` negativa aumenta o estoque); `atualizar_status_pedido` responde 200 para pedido inexistente.
Impact: Entradas inválidas geram 500 e corrompem estoque.
Recommendation: Validadores puros em `utils/validators.py` que lançam erro de validação → 400 pelo handler central.
Playbook: P-11

### #15 [MEDIUM] Queries N+1 e agregações separadas (AP-13)
File: models.py:139-141, 154-156, 187-193, 219-225, 239-254
Description: `get_pedidos_usuario`/`get_todos_pedidos` fazem 1 query por pedido + 1 por item (`cursor2`, `cursor3`); `criar_pedido` busca cada produto duas vezes; `relatorio_vendas` faz 5 consultas separadas que cabem em uma agregação.
Impact: `GET /pedidos` cresce como O(pedidos × itens) em queries.
Recommendation: Uma query com `JOIN` itens_pedido/produtos agrupada em memória; relatório com `COUNT`/`SUM(CASE WHEN ...)` numa única query.
Playbook: P-08

### #16 [MEDIUM] Código e validação duplicados (AP-14)
File: models.py:12-21, 31-40, 304-313, 79-86, 95-102, 171-201, 203-233
File: controllers.py:28-50, 72-90
Description: Conversão row→dict de produto repetida 3 vezes e de usuário 2 vezes; `get_pedidos_usuario` e `get_todos_pedidos` são idênticas exceto pelo WHERE; validação de create e update é copiada, mas o update perdeu as checagens de tamanho de nome e de categoria (divergência = bug).
Impact: Correções precisam ser feitas em vários lugares e já divergiram.
Recommendation: Funções únicas de serialização por entidade, uma consulta de pedidos com filtro opcional e um validador de produto compartilhado por create/update.
Playbook: P-11

### #17 [LOW] Magic numbers e strings (AP-19)
File: models.py:150, 247-262
File: controllers.py:47-52, 242
Description: Faixas de desconto `10000/5000/1000` e taxas `0.1/0.05/0.02`; limites de nome `2`/`200`; listas de categorias e status literais; strings de status (`'pendente'`, `'aprovado'`, `'cancelado'`) repetidas.
Impact: Regras de negócio escondidas e fáceis de divergir.
Recommendation: Constantes nomeadas em `utils/constants.py` (categorias, status, faixas de desconto).
Playbook: P-13

### #18 [LOW] Nomenclatura ruim (AP-20)
File: models.py:187-192, 219-224
File: controllers.py:14, 56, 64, 98, 136, 160
Description: `cursor2`/`cursor3`/`prod` com sufixos numéricos; parâmetro/variável `id` sombreando o builtin do Python.
Impact: Leitura mais lenta; risco de bug ao usar `id()`.
Recommendation: Nomes descritivos (`produto_id`, `itens_cursor`); manter os nomes dos parâmetros de rota/JSON do contrato.
Playbook: P-13

### #19 [LOW] Código morto (AP-21)
File: models.py:2
File: database.py:2
Description: `import sqlite3` em `models.py` e `import os` em `database.py` não são usados.
Impact: Ruído e falsa impressão de dependência.
Recommendation: Remover os imports não usados.
Playbook: P-15

### #20 [LOW] print() como mecanismo de log (AP-22)
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
File: app.py:56, 83-86
Description: Logs e "envio" de email/SMS/push feitos com `print`, sem nível nem timestamp; `criar_usuario` e `login` imprimem o email do usuário (PII).
Impact: Sem controle de nível/destino; PII em stdout.
Recommendation: `logging.getLogger(__name__)` configurado no composition root; notificações num serviço dedicado; não logar emails em claro.
Playbook: P-13

## Architecture Notes
- Pseudo-MVC: há `app.py` (rotas + config + SQL admin + boot), `controllers.py` (handlers com validação, regras e SQL do health) e `models.py` (dados + regras de 3 domínios); faltam `config/`, `services/`, `middlewares/` e rotas (Blueprints) separadas.
- `database.py` mistura conexão global, DDL e seed; deve virar `models/database.py` com conexão por requisição + `init_db` chamado explicitamente no `create_app`.
- Não existe autenticação na API; a Fase 3 protege apenas as rotas admin (flag + token). Proteger `/usuarios`, `/pedidos` e `/relatorios` exigiria um esquema de login/token que muda o contrato — fica como follow-up manual.
- APIs deprecated: verificado contra Python 3.14 / Flask 3.1 / sqlite3 — nenhum uso encontrado (0 achados AP-18). Também não há código assíncrono (AP-17 não se aplica).
- Não há suíte de testes no projeto.

================================
Total: 20 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
  y              → corrige todos os achados
  n              → encerra sem modificar nenhum arquivo
  y, skip 3,7    → corrige todos exceto os achados #3 e #7
