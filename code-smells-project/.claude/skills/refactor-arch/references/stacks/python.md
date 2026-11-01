# Stack: Python

## 1. Detecção

**Versão:** `requires-python` (`pyproject.toml`), `python_requires` (`setup.py`), `.python-version`, `runtime.txt`, imagem base do `Dockerfile`.

| Framework | Dependência | Sinal no código | Rotas (regex) | Porta padrão |
|---|---|---|---|---|
| Flask | `flask` | `Flask(__name__)`, `Blueprint(` | `@\w+\.(route\|get\|post\|put\|patch\|delete)\(`, `register_blueprint\(.*url_prefix`, `add_url_rule\(` | 5000 |
| FastAPI | `fastapi` | `FastAPI()`, `APIRouter(` | `@\w+\.(get\|post\|put\|patch\|delete)\(`, `include_router\(.*prefix` | 8000 (uvicorn) |
| Django / DRF | `django`, `djangorestframework` | `manage.py`, `settings.py`, `urls.py` | `path\(`, `re_path\(`, `router\.register\(` | 8000 |
| Outros (Bottle, Falcon, Sanic, aiohttp, Starlette) | nome do pacote | instância da app | decorators/`add_route` | ver código |

**Entry point:** `if __name__ == "__main__":` com `app.run(...)`/`uvicorn.run(...)`, `manage.py`, `create_app()` usado por `flask run`, `Procfile`/`Dockerfile`.

## 2. Ambiente

| Gerenciador (evidência) | Instalar | Executar |
|---|---|---|
| pip (`requirements.txt`) | `python -m venv .venv` + `<venv>/pip install -r requirements.txt` | `<venv>/python <entry>` |
| Poetry (`poetry.lock`) | `poetry install` | `poetry run <start>` |
| Pipenv (`Pipfile.lock`) | `pipenv install` | `pipenv run <start>` |
| uv (`uv.lock`) | `uv sync` | `uv run <start>` |

`<venv>` = `.venv/bin` (Linux/macOS) ou `.venv\Scripts` (Windows). Sem build. **Testes:** `pytest`, `python -m unittest`, `python manage.py test`.
**Ignorar:** `venv/`, `.venv/`, `env/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `*.egg-info/`, `dist/`, `build/`.

## 3. Padrões de busca

| AP | Padrões |
|---|---|
| AP-01 | `app\.config\[['"]SECRET_KEY['"]\]\s*=\s*['"]`, `secret_key\s*=\s*['"]`, `SECRET_KEY\s*=\s*['"]` (Django settings) |
| AP-02 | `execute\(\s*f["']`, `execute\([^,)]*(\+\|%\s*\(\|\.format\()`, `text\(\s*f["']`, `\.raw\(\s*f?["'].*(\{\|%\|\+)`, `\.extra\(` |
| AP-05 | `hashlib\.(md5\|sha1\|sha256)\(`, `base64\.\w*encode\(.*pass` |
| AP-06 | `to_dict`/`__dict__`/`model_to_dict` incluindo `password`; `jsonify\(.*str\(e\)` |
| AP-08 | `cursor\.execute\|\.execute\(\|db\.session\|\.query\.\|\.objects\.` em arquivos de rotas/views |
| AP-09 | `^global \w+`, `check_same_thread\s*=\s*False`, `^\w+\s*=\s*(\[\]\|\{\}\|0\|None)` em módulo usado por handlers |
| AP-10 | conexão criada no topo do módulo; `app = Flask(` em nível de módulo sem `create_app`; `import routes` por efeito colateral |
| AP-12 | `debug\s*=\s*True`, `host\s*=\s*['"]0\.0\.0\.0`, `CORS\(app\)\s*$`, `DEBUG\s*=\s*True`, `ALLOWED_HOSTS\s*=\s*\[\s*['"]\*` |
| AP-13 | `execute`/`.query`/`.get(`/`.objects.` dentro de `for`; `len\(\w+\.query\.all\(\)\)`; `len\(\w+\.\w+\)` em relacionamento |
| AP-15 | `request\.json\[`, `request\.get_json\(\)\[`, `int\(request\.`, `datetime\.strptime\(.*request` |
| AP-16 | `except:\s*$`, `except Exception( as \w+)?:\s*(pass\|return)`, `str\(e\)` em resposta, `traceback\.format_exc\(\)` em resposta |
| AP-17 | `requests\.\|time\.sleep\(` dentro de `async def`; `asyncio\.get_event_loop\(\)` |
| AP-22 | `^\s*print\(` |

## 4. APIs deprecated

| Deprecated / removido | Moderno |
|---|---|
| `datetime.utcnow()`, `datetime.utcfromtimestamp()` (deprecated 3.12) | `datetime.now(timezone.utc)`, `datetime.fromtimestamp(ts, timezone.utc)` |
| `distutils`, `imp`, `asyncore`, `asynchat` (removidos 3.12) | `setuptools`/`packaging`, `importlib`, `asyncio` |
| `asyncio.get_event_loop()` sem loop ativo (3.10+) | `asyncio.run()` / `asyncio.get_running_loop()` |
| `pkg_resources` | `importlib.metadata` / `importlib.resources` |
| `collections.Mapping` etc. (removidos 3.10) | `collections.abc.*` |
| Flask: `@app.before_first_request` (removido 2.3), `app.json_encoder` | inicialização na app factory; `app.json` provider |
| Flask: `send_file(attachment_filename=)` (2.2) | `download_name=` |
| Werkzeug: `safe_str_cmp` (removido 2.1) | `hmac.compare_digest` |
| SQLAlchemy 2.0 / Flask-SQLAlchemy 3: `Model.query.get(id)`, `session.query().get()` | `db.session.get(Model, id)` |
| SQLAlchemy 2.0: `engine.execute()`, SQL string sem `text()`, API `Query` legada | `with engine.connect()` + `text()`; `select()` + `session.execute(...).scalars()` |
| marshmallow 3.13+: `default=`, `missing=` | `dump_default=`, `load_default=` |
| Pydantic v2: `.dict()`, `.json()`, `@validator`, `class Config` | `.model_dump()`, `.model_dump_json()`, `@field_validator`, `model_config` |
| FastAPI: `@app.on_event("startup")` | `lifespan` |
| Django 4.0: `url()` (removido), `ugettext*` (removido) | `path()`/`re_path()`, `gettext*` |

## 5. Idiomas

| P | Mecanismo |
|---|---|
| P-01 | Módulo `config` lendo `os.environ.get(...)`; Flask `app.config.from_object(Config)`; Django `settings.py` lendo `os.environ`; `pydantic-settings`/`python-dotenv` só se já existirem. Exemplo: `.env.example` |
| P-02 | `sqlite3`: `?` ou `:nome`; `psycopg`/`mysql-connector`/`PyMySQL`: `%s`; SQLAlchemy `text()` com `:nome`; ORM/QuerySet com filtros |
| P-05 | Flask: `@app.errorhandler(Exc)`/`register_error_handler`; FastAPI: `@app.exception_handler`; Django: middleware; DRF: `EXCEPTION_HANDLER` |
| P-06 | Flask/Werkzeug: `generate_password_hash`/`check_password_hash`; Django: `make_password`/`check_password` (rehash nativo); stdlib: `hashlib.scrypt` + `secrets.token_bytes` + `hmac.compare_digest`; `bcrypt`/`argon2-cffi` se presentes |
| P-07 | Decorator `@admin_required` (Flask) com `functools.wraps`; FastAPI `Depends`; DRF `permission_classes` |
| P-08 | JOIN em SQL cru; SQLAlchemy `joinedload`/`selectinload`, `func.count` + `group_by`; Django `select_related`/`prefetch_related`, `annotate`/`Count` |
| P-09 | `sqlite3`: conexão como context manager ou `commit`/`rollback` explícitos; SQLAlchemy `with session.begin():`; Django `transaction.atomic()` |
| P-10 | `async`/`await`, `asyncio.gather`; libs HTTP assíncronas (`httpx.AsyncClient`) em handlers async |
| P-11 | marshmallow / Pydantic / Django Forms/Serializers se já usados; senão funções puras em `utils/validators` |
| P-13 | `logging.getLogger(__name__)`, configurado uma vez no composition root (`logging.basicConfig` com nível da config); constantes em módulo ou `enum.Enum` |
| P-14 | Flask: `create_app(config)`, conexão por requisição em `flask.g` + `teardown_appcontext`, Blueprints registrados na factory; FastAPI: `Depends` + `lifespan`; Django: `AppConfig.ready` só para wiring |

## 6. Estrutura alvo

- **Flask / FastAPI / similares:** `app.py` (composition root fino, start original preservado) + `config/`, `models/` (com `database.py`), `controllers/`, `services/` (opcional), `views/` ou `routes/` (Blueprints/APIRouters), `middlewares/`, `utils/`. Pacotes com `__init__.py`. Se o projeto já usa `src/` ou um pacote nomeado, coloque as camadas dentro dele.
- **Django:** MVT já é a convenção — `models.py` (Model), `views.py` (Controller), `urls.py` + serializers (View). Mova regras pesadas das views para `services.py` por app; não crie pastas MVC paralelas.

## 7. Armadilhas

- Pacotes precisam de `__init__.py`; rode a partir da raiz; imports circulares (models nunca importam controllers/routes).
- O reloader do modo debug cria um processo filho — derrube pelo processo que escuta na porta.
- Banco SQLite com caminho relativo muda de lugar quando o código é movido — resolva o caminho a partir da config.
- Misturar datetimes naive e aware após corrigir `utcnow()` — normalize num helper único.
