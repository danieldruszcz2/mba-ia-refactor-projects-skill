# task-manager-api

API de Task Manager em Python/Flask (tasks, usuários, categorias e relatórios), organizada em camadas:

```
app.py            composition root (create_app) — monta config, banco, error handlers e rotas
config/           leitura de variáveis de ambiente (único módulo que lê o ambiente)
models/           entidades SQLAlchemy + todo o acesso a dados (database.py: db, transaction)
controllers/      casos de uso e regras de negócio
routes/           Blueprints finos: HTTP → controller
middlewares/      error handler central e autenticação/autorização
utils/            constantes, validadores, datas, hash de senha/tokens, erros de domínio
```

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # opcional: ajuste as variáveis
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`instance/tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Configuração

Todas as variáveis estão documentadas em `.env.example`. As principais:

| Variável | Default | Descrição |
|---|---|---|
| `SECRET_KEY` | aleatória por boot | Assina os tokens de login. Defina em produção. |
| `DATABASE_URL` | `sqlite:///tasks.db` | URI do banco. |
| `DEBUG` / `HOST` / `PORT` | `false` / `127.0.0.1` / `5000` | Execução do servidor. |
| `CORS_ORIGINS` | vazio (CORS desligado) | Origens permitidas, separadas por vírgula. |
| `ENABLE_ADMIN_ROUTES` | `false` | Habilita operações administrativas. |
| `TOKEN_MAX_AGE_SECONDS` | `3600` | Validade do token de login. |
| `LOG_LEVEL` | `INFO` | Nível de log. |

## Autenticação e operações administrativas

`POST /login` devolve um `token` assinado. Envie-o como `Authorization: Bearer <token>`.

As operações abaixo exigem `ENABLE_ADMIN_ROUTES=true` **e** o token de um usuário `admin`; caso contrário respondem `403`:

- `DELETE /users/<id>`
- criar usuário com role `admin`/`manager` (`POST /users`)
- alterar o role de um usuário para/de `admin`/`manager` (`PUT /users/<id>`)

Senhas são armazenadas com hash scrypt (Werkzeug). Hashes MD5 legados continuam aceitos no login e são convertidos automaticamente.
