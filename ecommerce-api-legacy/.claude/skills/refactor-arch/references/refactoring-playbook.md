# Playbook de Refatoração (Fase 3)

Padrões concretos de transformação: para cada um, **estado antes, estado depois, passos, cuidados e um exemplo de código antes/depois**.

Os exemplos usam **Python** e **JavaScript (Node)** apenas como ilustração. Entidades e nomes são genéricos (`user`, `item`, `order`), não de um projeto específico. Ao aplicar um padrão, use o mecanismo idiomático da stack detectada, que está na seção **"Idiomas"** do guia `references/stacks/<stack>.md`, indexada pelos mesmos IDs `P-xx`. Nunca copie o idioma de outra stack. Sem guia para a stack, use o mecanismo idiomático que você conhece e mantenha a mesma forma de transformação do exemplo.

Regra geral: prefira o que **já existe** no projeto (libs de validação, auth, logging, helpers) antes de introduzir algo novo.

## Sumário

| ID | Padrão | Corrige |
|---|---|---|
| P-01 | Extrair configuração e segredos para variáveis de ambiente | AP-01, AP-12 |
| P-02 | Queries parametrizadas | AP-02 |
| P-03 | Decompor God Class/Module em camadas | AP-03 |
| P-04 | Afinar a rota: lógica → controller/service, dados → model | AP-07, AP-08 |
| P-05 | Error handler centralizado + erros de domínio | AP-16, AP-06 |
| P-06 | Hash forte de senha + serialização segura | AP-05, AP-06 |
| P-07 | Proteger endpoints perigosos (flag + auth) | AP-04 |
| P-08 | Eliminar N+1 (JOIN/IN/eager loading/agregação no banco) | AP-13 |
| P-09 | Transações em escritas multi-etapa | AP-11 |
| P-10 | Fluxo assíncrono estruturado | AP-17 |
| P-11 | Centralizar validação e eliminar duplicação | AP-14, AP-15 |
| P-12 | Substituir APIs deprecated | AP-18 |
| P-13 | Constantes nomeadas, nomes claros e logger | AP-19, AP-20, AP-22 |
| P-14 | Composition root + injeção de dependência + fim do estado global | AP-09, AP-10 |
| P-15 | Remover código morto | AP-21 |

Ordem recomendada de aplicação: P-01 → P-14 → P-03 → P-02/P-06/P-09 (models) → P-04/P-11 (controllers) → P-07/P-05 (middlewares) → P-08/P-10/P-12 → P-13/P-15.

---

## P-01 — Extrair configuração e segredos para variáveis de ambiente

**Antes:** segredos, caminho/URL do banco, modo debug, host, porta e origens CORS escritos como literais no código ou em arquivo de config versionado.

**Depois:**
- Um único módulo/objeto de configuração lê cada valor de uma variável de ambiente, com default **seguro e só para desenvolvimento** (debug desligado, bind local, admin desabilitado, segredo vazio ou de dev).
- O resto do código recebe a config (injeção) ou a importa desse módulo. Ninguém mais lê o ambiente.
- Um arquivo de exemplo documenta cada variável, sem valores reais, no formato idiomático da stack.

**Passos:**
1. Liste todos os literais de configuração encontrados nos achados AP-01/AP-12.
2. Crie o módulo de config (ou use o mecanismo de configuração do framework, com placeholders de ambiente).
3. Substitua cada literal pela leitura da config.
4. Crie/atualize o arquivo de exemplo e garanta que o arquivo com valores reais está ignorado no versionamento.

**Cuidados:** nunca reutilize como default o valor real antigo, porque ele está comprometido. Se a app depende do valor para funcionar localmente sem configuração (porta, caminho do banco), mantenha o mesmo default para não quebrar o start. Carregar arquivo `.env` via biblioteca é opcional: só use se a dependência já existir ou o framework já fizer isso.

**Exemplo — antes:**

```python
# app.py
app = Flask(__name__)
app.config["SECRET_KEY"] = "minha-chave-123"
CORS(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

**Exemplo — depois:**

```python
# config/settings.py
import os

def _bool(name, default="false"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "app.db")
    DEBUG = _bool("APP_DEBUG")
    HOST = os.environ.get("APP_HOST", "127.0.0.1")
    PORT = int(os.environ.get("APP_PORT", "5000"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")

# app.py
from config.settings import Config

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, origins=config.CORS_ORIGINS)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
```

```dotenv
# .env.example (sem valores reais)
SECRET_KEY=
DATABASE_PATH=app.db
APP_DEBUG=false
APP_HOST=127.0.0.1
APP_PORT=5000
CORS_ORIGINS=http://localhost:3000
```

---

## P-02 — Queries parametrizadas

**Antes:** a consulta é montada concatenando/interpolando valores externos na string SQL (ou no filtro NoSQL/comando).

**Depois:** a string da consulta é **constante**; os valores vão como **parâmetros** separados para o driver/ORM, usando o placeholder que ele suporta (posicional ou nomeado, ver guia da stack).

**Passos:**
1. Para cada consulta do achado, troque cada valor interpolado por um placeholder e passe o valor na lista/mapa de parâmetros.
2. Padrões com curinga (`LIKE`): o curinga vai no **valor** do parâmetro, não na string SQL.
3. Listas variáveis (`IN`): gere um placeholder por item ou use o recurso de expansão do driver/ORM.
4. Filtros opcionais: construa a lista de condições e a lista de parâmetros em paralelo.

**Cuidados:** nomes de colunas, tabelas e direção de ordenação **não** podem ser parametrizados. Valide-os contra uma **allowlist** e rejeite (400) o resto. Usar a API de consulta do ORM, quando o projeto já tem um, também resolve.

**Exemplo — antes:**

```python
def find_by_email(email):
    cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
    return cursor.fetchone()

def search(term, category=None, order="name"):
    sql = f"SELECT * FROM items WHERE name LIKE '%{term}%'"
    if category:
        sql += f" AND category = '{category}'"
    sql += f" ORDER BY {order}"
    return cursor.execute(sql).fetchall()
```

**Exemplo — depois:**

```python
ALLOWED_ORDER = {"name", "price", "created_at"}

def find_by_email(conn, email):
    return conn.execute("SELECT id, name, email FROM users WHERE email = ?", (email,)).fetchone()

def search(conn, term, category=None, order="name"):
    if order not in ALLOWED_ORDER:
        raise ValidationError("invalid order field")
    conditions, params = ["name LIKE ?"], [f"%{term}%"]
    if category:
        conditions.append("category = ?")
        params.append(category)
    sql = f"SELECT * FROM items WHERE {' AND '.join(conditions)} ORDER BY {order}"  # só identificadores da allowlist
    return conn.execute(sql, params).fetchall()
```

```javascript
// Node (sqlite3 / mysql2 usam "?", pg usa "$1")
// antes
db.get(`SELECT * FROM users WHERE email = '${email}'`, cb);
// depois
const user = await db.get('SELECT id, name, email FROM users WHERE email = ?', [email]);
```

---

## P-03 — Decompor God Class/Module em camadas

**Antes:** uma classe/arquivo cria conexão, schema e seed, declara rotas, aplica regras de vários domínios e formata respostas.

**Depois:** uma responsabilidade por arquivo, por domínio:
- módulo de banco → conexão/pool, schema, seed (chamados pelo composition root);
- um model/repositório por entidade → todas as consultas daquela entidade;
- services → fluxos que envolvem várias entidades ou integrações (pagamento, notificação);
- controllers → fluxo de cada caso de uso;
- routes → mesmas URLs e métodos de antes, delegando ao controller;
- composition root → monta banco, models, services, controllers, rotas e error handler.

**Procedimento:**
1. Liste cada função/método do God Module e classifique: dado / regra / rota / config / util.
2. Crie os arquivos-destino por domínio e camada; mova o código **sem alterar comportamento** primeiro.
3. Ajuste imports/registro e o composition root; compile/suba a app para confirmar que nada quebrou.
4. Só então aplique as demais correções (P-02, P-06, ...) nos arquivos novos.
5. Apague o arquivo original quando estiver vazio (ou deixe-o como ponte de entry point, se for o arquivo de start).

**Exemplo — antes:**

```javascript
// src/AppManager.js — uma classe faz tudo
class AppManager {
  constructor() {
    this.db = new sqlite3.Database(':memory:');
    this.db.run('CREATE TABLE users (...)');          // schema + seed
  }
  setupRoutes(app) {
    app.post('/api/orders', (req, res) => {           // rota
      this.db.get('SELECT * FROM items WHERE id = ?', [req.body.itemId], (err, item) => {
        const total = item.price * req.body.qty * 0.9; // regra de negócio
        this.db.run('INSERT INTO orders ...', [/*...*/], () => res.json({ total }));
      });
    });
  }
}
```

**Exemplo — depois:**

```javascript
// src/models/database.js        → conexão, schema e seed
// src/models/itemRepository.js
class ItemRepository {
  constructor(db) { this.db = db; }
  findById(id) { return this.db.get('SELECT * FROM items WHERE id = ?', [id]); }
}

// src/services/orderService.js  → regra de negócio
class OrderService {
  constructor({ itemRepository, orderRepository }) { Object.assign(this, { itemRepository, orderRepository }); }
  async create({ itemId, qty }) {
    const item = await this.itemRepository.findById(itemId);
    if (!item) throw new NotFoundError('item not found');
    const total = item.price * qty * (1 - BULK_DISCOUNT);
    return this.orderRepository.insert({ itemId, qty, total });
  }
}

// src/controllers/orderController.js → fluxo HTTP do caso de uso
const makeOrderController = (orderService) => ({
  create: async (req, res) => res.json(await orderService.create(req.body)),
});

// src/routes/index.js → só mapeamento
router.post('/api/orders', asyncHandler(orderController.create));
```

---

## P-04 — Afinar a rota: lógica → controller/service, dados → model

**Antes:** o handler da rota lê o body, abre conexão, consulta o banco, valida, aplica regras (ex.: devolver estoque ao cancelar), grava, imprime uma "notificação" e monta a resposta.

**Depois:**
- **Rota:** uma linha de delegação: passa os parâmetros do caminho e o body ao controller e devolve o resultado.
- **Controller:** valida a entrada (P-11), busca a entidade via model, lança erro de domínio se não existe ou se a entrada é inválida, chama o model/service que executa a operação, dispara efeitos (notificação) via service, devolve resultado + status **idênticos** aos originais.
- **Model:** um método por operação de dados (`buscar por id`, `mudar status com reposição de estoque`), executando escritas relacionadas dentro de uma transação (P-09).

**Cuidados:** se o projeto já tem helpers/serviços com a lógica (um serviço de notificação ou de validação não usado), **use-os** em vez de reescrever. A resposta HTTP final é idêntica à original.

**Exemplo — antes:**

```python
@bp.route("/orders/<int:order_id>/status", methods=["PUT"])
def update_status(order_id):
    data = request.get_json()
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        return jsonify({"erro": "Pedido não encontrado"}), 404
    if data["status"] == "cancelado":
        for it in db.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)):
            db.execute("UPDATE items SET stock = stock + ? WHERE id = ?", (it["qty"], it["item_id"]))
    db.execute("UPDATE orders SET status = ? WHERE id = ?", (data["status"], order_id))
    db.commit()
    print(f"Enviando email: pedido {order_id} -> {data['status']}")
    return jsonify({"mensagem": "Status atualizado"}), 200
```

**Exemplo — depois:**

```python
# routes/order_routes.py — View: só mapeamento HTTP
@bp.route("/orders/<int:order_id>/status", methods=["PUT"])
def update_status(order_id):
    return order_controller.update_status(order_id, request.get_json(silent=True))

# controllers/order_controller.py — fluxo do caso de uso
def update_status(order_id, payload):
    status = validate_status_payload(payload)              # P-11 → ValidationError (400)
    if not order_model.exists(order_id):
        raise NotFoundError("Pedido não encontrado")       # P-05 → 404
    order_model.change_status(order_id, status)            # escrita em transação no model
    notification_service.order_status_changed(order_id, status)
    return jsonify({"mensagem": "Status atualizado"}), 200

# models/order_model.py — dados
def change_status(order_id, status):
    with transaction() as db:                              # P-09
        if status == OrderStatus.CANCELLED:
            db.execute("""UPDATE items SET stock = stock + oi.qty
                          FROM order_items oi
                          WHERE oi.item_id = items.id AND oi.order_id = ?""", (order_id,))
        db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
```

---

## P-05 — Error handler centralizado + erros de domínio

**Antes:** cada handler captura exceções genéricas e devolve a mensagem da exceção com status 500; formatos de erro variam entre rotas; alguns caminhos de erro não respondem.

**Depois:**
- **Erros de domínio:** uma hierarquia pequena (base com mensagem + status + detalhes opcionais; subtipos para validação → 400, não encontrado → 404, proibido → 403, conflito → 409).
- **Handler global** registrado pelo mecanismo do framework (ver guia da stack): converte erro de domínio em `{<chave de erro original>: mensagem}` + status; converte rota inexistente em 404 no mesmo formato; para qualquer outra exceção, **loga com stack no servidor** e responde 500 com mensagem genérica.
- Handlers e controllers não capturam exceções só para formatar resposta: lançam erros de domínio e deixam propagar.

**Cuidados:** preserve a chave de erro que o projeto já usava e os status de erro originais quando faziam sentido. Nunca devolva mensagem de exceção, stack ou SQL ao cliente. Em stacks onde erros assíncronos não chegam ao handler global automaticamente, use o mecanismo de encaminhamento indicado no guia.

**Exemplo — antes:**

```python
@bp.route("/items/<int:item_id>")
def get_item(item_id):
    try:
        item = item_model.find(item_id)
        if not item:
            return jsonify({"erro": "não encontrado"}), 404
        return jsonify(item), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500      # vaza SQL/stack ao cliente
```

**Exemplo — depois:**

```python
# utils/errors.py
class AppError(Exception):
    status = 500
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message, self.details = message, details

class ValidationError(AppError): status = 400
class ForbiddenError(AppError):  status = 403
class NotFoundError(AppError):   status = 404

# middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        body = {"erro": err.message}
        if err.details:
            body["detalhes"] = err.details
        return jsonify(body), err.status

    @app.errorhandler(404)
    def handle_not_found(_):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("Unhandled error")     # stack só no log do servidor
        return jsonify({"erro": "Erro interno do servidor"}), 500

# controllers/item_controller.py
def get_item(item_id):
    item = item_model.find(item_id)
    if not item:
        raise NotFoundError("não encontrado")
    return jsonify(item), 200
```

```javascript
// Express: middleware de erro com 4 parâmetros, registrado por último
// antes
app.get('/items/:id', (req, res) => {
  db.get('...', [req.params.id], (err, row) => {
    if (err) return res.status(500).send(err.message);
    res.json(row);
  });
});
// depois
function errorHandler(err, req, res, next) {
  if (err instanceof AppError) return res.status(err.status).json({ error: err.message });
  logger.error(err.stack);
  return res.status(500).json({ error: 'Internal server error' });
}
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next); // Express 4
app.get('/items/:id', asyncHandler(itemController.get));
app.use(errorHandler);
```

---

## P-06 — Hash forte de senha + serialização segura

**Antes:** senha gravada em texto puro, com hash rápido (MD5/SHA) ou codificação reversível; comparação direta de strings; entidade serializada inteira (com senha/hash); dados de cartão e segredos em logs.

**Depois:**
- **Hash:** algoritmo lento e com salt (bcrypt, scrypt, Argon2 ou PBKDF2), de preferência o que a stack/framework já oferece nativamente (ver guia). Funções `hash(senha)` e `verify(senha, armazenado)` em um único helper; a verificação usa a função da lib (tempo constante).
- **Compatibilidade com dados legados:** `verify` reconhece o formato do hash forte; se o valor armazenado está no formato antigo, valida pelo método antigo e, se passar, regrava com o hash forte (rehash no login).
- **Serialização:** a representação pública da entidade lista campos explicitamente e nunca inclui senha/hash/tokens. Consultas que vão para a resposta selecionam colunas explícitas.
- **Logs:** dados de cartão mascarados (só os 4 últimos dígitos); chaves e senhas nunca logadas.

**Cuidados:**
- Senha padrão quando o usuário não informa → passe a exigir senha (400). Se isso quebrar um fluxo do contrato que hoje funciona sem senha, gere uma senha aleatória e registre como mudança de comportamento.
- Seeds com senha em texto puro devem gravar hash.
- Dados já persistidos em formato inseguro: use rehash no login e registre a migração em "Manual Follow-ups".

**Exemplo — antes:**

```python
def create_user(name, email, password):
    db.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
               (name, email, hashlib.md5(password.encode()).hexdigest()))

def login(email, password):
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user and user["password"] == hashlib.md5(password.encode()).hexdigest():
        return dict(user)                            # inclui o hash na resposta
```

**Exemplo — depois:**

```python
# utils/security.py
import hashlib, hmac
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(raw):
    return generate_password_hash(raw)               # scrypt/pbkdf2 com salt

def verify_password(raw, stored):
    """Retorna (ok, needs_rehash)."""
    if stored.startswith(("scrypt:", "pbkdf2:")):
        return check_password_hash(stored, raw), False
    legacy = hashlib.md5(raw.encode()).hexdigest()   # formato antigo
    return hmac.compare_digest(legacy, stored), True

# models/user_model.py
PUBLIC_FIELDS = "id, name, email, created_at"

def to_public(row):
    return {"id": row["id"], "name": row["name"], "email": row["email"], "created_at": row["created_at"]}

def login(email, password):
    row = db.execute("SELECT id, password FROM users WHERE email = ?", (email,)).fetchone()
    if not row:
        return None
    ok, needs_rehash = verify_password(password, row["password"])
    if not ok:
        return None
    if needs_rehash:
        db.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(password), row["id"]))
    return to_public(db.execute(f"SELECT {PUBLIC_FIELDS} FROM users WHERE id = ?", (row["id"],)).fetchone())
```

```javascript
// Node sem dependência extra: crypto.scrypt + timingSafeEqual; mascarar cartão no log
// antes
console.log(`Pagamento com cartão ${card} da chave ${PAYMENT_KEY}`);
// depois
const maskCard = (card) => `**** **** **** ${String(card).slice(-4)}`;
logger.info(`Pagamento com cartão ${maskCard(card)}`);
```

---

## P-07 — Proteger endpoints perigosos (flag + auth)

**Antes:** rota que executa SQL arbitrário, reseta o banco ou faz operação administrativa, aberta a qualquer um.

**Depois:**
- A rota **continua existindo** (contrato), protegida por um middleware/filtro/guard `admin`:
  1. se a flag de config `ENABLE_ADMIN_ROUTES` está desligada (default) → `403` no formato de erro padrão;
  2. se ligada, exige credencial: o mecanismo de auth real do projeto, se houver; senão, um token de admin vindo da config, comparado em tempo constante → `403` se ausente/errado.
- Execução de SQL arbitrário: além da proteção, restrinja a leitura (`SELECT`) ou remova a capacidade e documente.
- Campos de privilégio (papel, flag de admin) não são aceitos do body em cadastro público: ignore-os ou exija admin.

**Cuidados:** registre cada rota afetada em "Behavior Changes". No smoke test, a rota deve responder `403` com a flag desligada.

**Exemplo — antes:**

```python
@app.route("/admin/reset-db", methods=["POST"])
def reset_db():
    db.execute("DELETE FROM orders"); db.execute("DELETE FROM users")
    return jsonify({"mensagem": "Banco resetado"})

@app.route("/admin/query", methods=["POST"])
def run_query():
    return jsonify(db.execute(request.json["sql"]).fetchall())
```

**Exemplo — depois:**

```python
# middlewares/auth.py
import hmac
from functools import wraps

def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        cfg = current_app.config
        if not cfg["ENABLE_ADMIN_ROUTES"]:
            raise ForbiddenError("Rotas administrativas desabilitadas")
        token = request.headers.get("X-Admin-Token", "")
        if not cfg["ADMIN_TOKEN"] or not hmac.compare_digest(token, cfg["ADMIN_TOKEN"]):
            raise ForbiddenError("Acesso negado")
        return view(*args, **kwargs)
    return wrapper

# routes/admin_routes.py
@bp.route("/admin/reset-db", methods=["POST"])
@admin_required
def reset_db():
    return admin_controller.reset_db()

@bp.route("/admin/query", methods=["POST"])
@admin_required
def run_query():
    return admin_controller.run_read_only_query(request.get_json(silent=True))  # aceita só SELECT
```

```javascript
// Express
const requireAdmin = (config) => (req, res, next) => {
  if (!config.enableAdminRoutes) return next(new ForbiddenError('Admin routes disabled'));
  const token = Buffer.from(req.get('x-admin-token') || '');
  const expected = Buffer.from(config.adminToken || '');
  if (!expected.length || token.length !== expected.length || !crypto.timingSafeEqual(token, expected))
    return next(new ForbiddenError('Forbidden'));
  next();
};
router.delete('/api/admin/reset', requireAdmin(config), asyncHandler(adminController.reset));
```

---

## P-08 — Eliminar N+1

**Antes:** busca a lista e, dentro do loop, faz uma consulta por item (e às vezes outra por sub-item); ou carrega todas as linhas para contar/filtrar em memória.

**Depois (uma das opções, na ordem de preferência):**
1. **Uma consulta com JOIN** trazendo pai + filhos, agrupando em memória por id do pai (preservando a ordem original).
2. **Duas consultas**: a lista + uma consulta `IN (ids)` para os filhos, montando um mapa id → filhos.
3. **Eager loading** do ORM para os relacionamentos usados no loop.
4. **Agregação no banco** (`COUNT`, `SUM`, `GROUP BY`) em vez de carregar coleções para contar ou somar.

**Cuidados:** o JSON de saída deve ser idêntico (mesmas chaves, mesma ordem de itens, mesmo tratamento de pais sem filhos). Paginação só se puder ser **opcional** (parâmetros com default que devolve o mesmo resultado de antes).

**Exemplo — antes:**

```python
orders = db.execute("SELECT * FROM orders").fetchall()
result = []
for o in orders:
    items = db.execute("SELECT * FROM order_items WHERE order_id = ?", (o["id"],)).fetchall()
    for it in items:
        it["name"] = db.execute("SELECT name FROM items WHERE id = ?", (it["item_id"],)).fetchone()["name"]
    result.append({**o, "items": items})

total_users = len(User.query.all())                  # carrega tudo para contar
```

**Exemplo — depois:**

```python
orders = db.execute("SELECT * FROM orders ORDER BY id").fetchall()
ids = [o["id"] for o in orders]
by_order = {i: [] for i in ids}
if ids:
    placeholders = ",".join("?" * len(ids))
    rows = db.execute(f"""SELECT oi.*, i.name FROM order_items oi
                          JOIN items i ON i.id = oi.item_id
                          WHERE oi.order_id IN ({placeholders})""", ids).fetchall()
    for r in rows:
        by_order[r["order_id"]].append(dict(r))
result = [{**dict(o), "items": by_order[o["id"]]} for o in orders]   # mesma ordem, pais sem filhos → []

total_users = db.session.query(func.count(User.id)).scalar()        # agregação no banco
# ORM: Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
```

---

## P-09 — Transações em escritas multi-etapa

**Antes:** várias escritas relacionadas (cabeçalho + itens + baixa de estoque; usuário + matrícula + pagamento) executadas em sequência, sem transação, às vezes com commit no meio ou dentro do loop.

**Depois:**
- Um helper/mecanismo de transação único na camada de dados (bloco, função de ordem superior ou anotação, ver guia da stack): inicia, executa, faz commit no sucesso e rollback em qualquer erro, relançando o erro.
- O método do model que implementa o caso de uso executa **todas** as escritas relacionadas dentro de uma transação.
- Verificações de concorrência entram na própria escrita quando possível (ex.: decrementar estoque só se houver saldo e checar linhas afetadas; se zero, lançar erro de validação → rollback).
- Deleções com dependentes: apague/cascateie os filhos na mesma transação.

**Exemplo — antes:**

```python
def create_order(user_id, items):
    cur = db.execute("INSERT INTO orders (user_id) VALUES (?)", (user_id,))
    db.commit()
    for it in items:
        db.execute("INSERT INTO order_items (order_id, item_id, qty) VALUES (?, ?, ?)",
                   (cur.lastrowid, it["item_id"], it["qty"]))
        db.execute("UPDATE items SET stock = stock - ? WHERE id = ?", (it["qty"], it["item_id"]))
        db.commit()                                   # falha no 2º item deixa pedido pela metade
```

**Exemplo — depois:**

```python
# models/database.py
from contextlib import contextmanager

@contextmanager
def transaction():
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise

# models/order_model.py
def create_order(user_id, items):
    with transaction() as db:
        order_id = db.execute("INSERT INTO orders (user_id) VALUES (?)", (user_id,)).lastrowid
        for it in items:
            updated = db.execute("UPDATE items SET stock = stock - ? WHERE id = ? AND stock >= ?",
                                 (it["qty"], it["item_id"], it["qty"])).rowcount
            if updated == 0:
                raise ValidationError(f"Estoque insuficiente para o item {it['item_id']}")  # → rollback
            db.execute("INSERT INTO order_items (order_id, item_id, qty) VALUES (?, ?, ?)",
                       (order_id, it["item_id"], it["qty"]))
        return order_id
```

```javascript
// Node: helper BEGIN/COMMIT/ROLLBACK
async function withTransaction(db, fn) {
  await db.run('BEGIN');
  try { const result = await fn(db); await db.run('COMMIT'); return result; }
  catch (err) { await db.run('ROLLBACK'); throw err; }
}
```

---

## P-10 — Fluxo assíncrono estruturado

**Antes:** callbacks aninhados, contadores manuais de pendências, erros que não chegam à resposta, operações assíncronas disparadas sem aguardar, I/O bloqueante em servidor assíncrono.

**Depois:**
- Use o modelo assíncrono **moderno da linguagem** (async/await, futures compostos, goroutines com sincronização etc., ver guia). Drivers só com API de callback ganham um adaptador fino na camada de dados.
- Fluxo sequencial: passos aguardados em ordem, dentro de uma transação quando há escritas (P-09); erros propagam até o handler global (P-05).
- Contadores manuais → primitiva de "aguardar todos" da linguagem, preservando a ordem dos resultados. Melhor ainda: substituir o loop por uma única consulta (P-08).
- I/O bloqueante em handler assíncrono → a versão não bloqueante da API.

**Exemplo — antes:**

```javascript
app.get('/api/report', (req, res) => {
  db.all('SELECT * FROM courses', [], (err, courses) => {
    let pending = courses.length;
    const out = [];
    courses.forEach((c) => {
      db.all('SELECT * FROM enrollments WHERE course_id = ?', [c.id], (err2, rows) => {
        out.push({ course: c.title, students: rows.length });   // ordem não garantida, err2 ignorado
        if (--pending === 0) res.json(out);                     // lista vazia nunca responde
      });
    });
  });
});
```

**Exemplo — depois:**

```javascript
// src/models/database.js — adaptador fino do driver de callback
const { promisify } = require('util');
const wrap = (db) => ({
  all: promisify(db.all.bind(db)),
  get: promisify(db.get.bind(db)),
  run: (sql, params = []) => new Promise((resolve, reject) =>
    db.run(sql, params, function (err) { err ? reject(err) : resolve({ lastID: this.lastID, changes: this.changes }); })),
});

// src/models/reportRepository.js — uma consulta agregada em vez do loop (P-08)
const studentsPerCourse = (db) => db.all(`
  SELECT c.title AS course, COUNT(e.id) AS students
  FROM courses c LEFT JOIN enrollments e ON e.course_id = c.id
  GROUP BY c.id ORDER BY c.id`);

// src/controllers/reportController.js — erros seguem para o errorHandler (P-05)
const report = async (req, res) => res.json(await reportService.studentsPerCourse());

// quando várias chamadas independentes são necessárias:
const results = await Promise.all(ids.map((id) => repo.findById(id)));   // preserva a ordem
```

---

## P-11 — Centralizar validação e eliminar duplicação

**Antes:** create e update validam de formas diferentes (update mais fraco); listas de valores válidos repetidas; conversões que estouram em 500; conversão registro→representação copiada em vários lugares.

**Depois:**
- **Um validador por entidade/caso de uso** (no mecanismo da stack: schema, DTO anotado ou função pura; prefira a lib que o projeto já usa), com modo **parcial** para update: valida apenas os campos presentes, com as mesmas regras do create.
- O validador checa body ausente/não-objeto, presença, tipo, formato, faixa e valores permitidos; acumula erros por campo e lança **um** erro de validação (→ 400) com os detalhes.
- Listas de valores válidos viram constantes únicas (P-13).
- Conversão registro→representação vira **uma** função/método reutilizada; métodos que já existiam no model são reaproveitados em vez das cópias.

**Cuidados:** mantenha as **mensagens de erro e status** originais quando o cliente pode depender delas.

**Exemplo — antes:**

```python
def create_task():
    data = request.get_json()
    if not data.get("title"):
        return jsonify({"error": "title required"}), 400
    if data.get("status") not in ["pending", "in_progress", "done"]:
        return jsonify({"error": "invalid status"}), 400
    due = datetime.strptime(data["due_date"], "%Y-%m-%d")      # formato inválido → 500
    ...

def update_task(task_id):
    data = request.get_json()
    task.status = data.get("status", task.status)              # sem validação nenhuma
    task.priority = int(data["priority"])                      # "alta" → 500
```

**Exemplo — depois:**

```python
# utils/constants.py
TASK_STATUSES = ("pending", "in_progress", "done")
PRIORITY_RANGE = (1, 5)

# utils/validators.py
def validate_task(data, partial=False):
    if not isinstance(data, dict):
        raise ValidationError("Corpo da requisição inválido")
    errors = {}
    if not partial or "title" in data:
        if not isinstance(data.get("title"), str) or not data["title"].strip():
            errors["title"] = "title required"
    if "status" in data and data["status"] not in TASK_STATUSES:
        errors["status"] = "invalid status"
    if "priority" in data:
        p = data["priority"]
        if not isinstance(p, int) or not PRIORITY_RANGE[0] <= p <= PRIORITY_RANGE[1]:
            errors["priority"] = f"priority must be an integer between {PRIORITY_RANGE[0]} and {PRIORITY_RANGE[1]}"
    if data.get("due_date") is not None:
        try:
            datetime.strptime(data["due_date"], "%Y-%m-%d")
        except (TypeError, ValueError):
            errors["due_date"] = "due_date must be YYYY-MM-DD"
    if errors:
        raise ValidationError(next(iter(errors.values())), details=errors)
    return data

# controllers/task_controller.py
def create_task(payload):
    data = validate_task(payload)
    return jsonify(task_model.create(data).to_dict()), 201

def update_task(task_id, payload):
    data = validate_task(payload, partial=True)               # mesmas regras do create
    return jsonify(task_model.update(task_id, data).to_dict()), 200
```

---

## P-12 — Substituir APIs deprecated

**Procedimento:**
1. Para cada achado AP-18, confirme que a alternativa moderna existe **na versão fixada** da linguagem/lib (guia da stack + manifesto).
2. Se existe, substitua todas as ocorrências. Centralize num helper quando a API é usada em vários lugares (ex.: geração de timestamps), para não misturar comportamentos antigo e novo.
3. Se a alternativa exige upgrade de versão, **não** altere o manifesto: registre o upgrade como "Manual Follow-up".
4. Depois do boot, confirme que os avisos de depreciação correspondentes sumiram do log de build/execução.

**Cuidados:** atenção a mudanças sutis de semântica (ex.: datas sem fuso vs. com fuso). Normalize num único ponto e preserve o formato serializado no JSON.

**Exemplo — antes:**

```python
from datetime import datetime

task.created_at = datetime.utcnow()                    # deprecated desde Python 3.12
user = User.query.get(user_id)                         # legado no SQLAlchemy 2.0 / Flask-SQLAlchemy 3
```

```javascript
const raw = new Buffer(token, 'base64');               // deprecated (DEP0005)
const { query } = url.parse(req.url, true);            // legado
```

**Exemplo — depois:**

```python
# utils/dates.py — ponto único de geração de timestamps
from datetime import datetime, timezone

def utc_now():
    # naive em UTC, para manter o mesmo formato serializado de antes
    return datetime.now(timezone.utc).replace(tzinfo=None)

task.created_at = utc_now()
user = db.session.get(User, user_id)
```

```javascript
const raw = Buffer.from(token, 'base64');
const query = Object.fromEntries(new URL(req.url, 'http://localhost').searchParams);
```

---

## P-13 — Constantes nomeadas, nomes claros e logger

**Depois:**
- **Constantes:** limites, taxas, status e papéis viram constantes/enums nomeados num único módulo (ou no próprio domínio a que pertencem).
- **Nomes:** identificadores internos crípticos ganham nomes descritivos na convenção da linguagem; campos do JSON (contrato) mantêm os nomes originais. Mapeie-os na fronteira.
- **Logger:** escrita na saída padrão vira o logger idiomático da stack (com nível), configurado uma vez no composition root com nível vindo da config.
- "Envios" simulados de email/SMS no meio da regra viram chamadas a um service de notificação que usa o logger.

**Exemplo — antes:**

```javascript
function proc(u, e, p, cc) {
  if (p.length < 6) return null;
  const d = cc.startsWith('4') ? 0.05 : 0;
  console.log('pagamento ok', u, cc);
  setTimeout(() => {}, 3000);
  return 100 * (1 - d);
}
```

**Exemplo — depois:**

```javascript
// src/config/constants.js
module.exports = Object.freeze({
  MIN_PASSWORD_LENGTH: 6,
  VISA_PREFIX: '4',
  VISA_DISCOUNT_RATE: 0.05,
  BASE_PRICE: 100,
});

// src/services/paymentService.js
const { MIN_PASSWORD_LENGTH, VISA_PREFIX, VISA_DISCOUNT_RATE, BASE_PRICE } = require('../config/constants');

function processPayment({ userName, email, password, cardNumber }) {
  if (password.length < MIN_PASSWORD_LENGTH) return null;
  const discountRate = cardNumber.startsWith(VISA_PREFIX) ? VISA_DISCOUNT_RATE : 0;
  logger.info(`Payment approved for ${userName} (card ${maskCard(cardNumber)})`);
  return BASE_PRICE * (1 - discountRate);
}
```

```python
# antes
print("Usuario criado:", user_id)
# depois — logging configurado uma vez no create_app com o nível da config
logger = logging.getLogger(__name__)
logger.info("Usuário criado: %s", user_id)
```

---

## P-14 — Composition root + injeção de dependência + fim do estado global

**Antes:** conexão global criada no carregamento do módulo; caches/contadores em variáveis globais ou estáticas; rotas registradas como efeito colateral de import; serviços instanciados dentro dos métodos que os usam.

**Depois:**
- **Composition root:** uma função/fábrica (ou o container de DI do framework) cria a app a partir da config, inicializa o banco (pool ou conexão por requisição/escopo, conforme a stack), instancia models → services → controllers passando as dependências, registra rotas, middlewares e o error handler. Retorna a app; o entry point só a inicia.
- **Conexões:** gerenciadas por escopo (pool do driver, sessão por requisição, ciclo de vida do container), nunca uma conexão global compartilhada sem controle de concorrência.
- **Estado:** caches realmente necessários viram um objeto injetado com interface explícita; os demais globais mutáveis são removidos.

**Cuidados:** caches/contadores globais escritos e nunca lidos → remova (P-15). Um banco em memória pode continuar como default se era o comportamento original, mas o endereço vem da config.

**Exemplo — antes:**

```python
# database.py
conn = sqlite3.connect("app.db", check_same_thread=False)   # conexão global compartilhada
request_count = 0

# app.py
app = Flask(__name__)
import routes                                                # rotas registradas por efeito colateral
```

**Exemplo — depois:**

```python
# models/database.py — conexão por requisição
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        create_schema(get_db())

# app.py — composition root
def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    database.init_app(app)
    register_error_handlers(app)
    app.register_blueprint(item_routes.bp)
    app.register_blueprint(order_routes.bp)
    return app

if __name__ == "__main__":
    create_app().run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
```

```javascript
// src/createApp.js — dependências injetadas, sem `new` dentro dos handlers
function createApp({ config, db }) {
  const app = express();
  app.use(express.json());
  const userRepository = new UserRepository(db);
  const userService = new UserService({ userRepository });
  app.use('/api', buildRoutes({ userController: makeUserController(userService), config }));
  app.use(errorHandler);
  return app;
}
// src/app.js — entry point só faz listen
createApp({ config, db: await openDatabase(config.dbPath) }).listen(config.port);
```

---

## P-15 — Remover código morto

**Procedimento:**
1. Para cada símbolo candidato, confirme com busca que não há referências, incluindo referências dinâmicas (reflexão, registro por nome/string, carregamento dinâmico de módulos, injeção por convenção, arquivos de config que apontam para classes).
2. Remova funções, variáveis, imports, módulos não usados e blocos de código comentado.

**Exceção importante:** helpers/serviços mortos que implementam algo que **deveria** acontecer (ex.: notificação ao concluir uma operação, validação de formato) não são apagados: são **reconectados** no controller/service correto (P-04). Decida pelo que o domínio exige e registre a decisão no resumo.

**Exemplo — antes:**

```python
import os, sys, json, time                               # os, sys, time nunca usados
from utils.helpers import validate_email                 # helper existe, mas a rota não chama

cache = {}                                               # escrito, nunca lido

def create_user(data):
    # old_hash = md5(data["password"])                   # bloco comentado
    if "@" not in data["email"]:                         # validação reimplementada pior
        return {"error": "email inválido"}, 400
    cache[data["email"]] = data
    ...

def legacy_export():                                     # nenhuma referência no projeto
    ...
```

**Exemplo — depois:**

```python
import json
from utils.validators import validate_email              # helper reconectado em vez de duplicado

def create_user(data):
    if not validate_email(data.get("email")):
        raise ValidationError("email inválido")
    ...
# `cache`, `legacy_export`, imports não usados e o bloco comentado foram removidos.
```
