# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Configuração

A configuração vem de variáveis de ambiente (ou de um arquivo `.env`, lido via `python-dotenv`). Veja `.env.example` para a lista completa:

| Variável | Default | Descrição |
|---|---|---|
| `SECRET_KEY` | aleatória por boot | Assina os tokens de login. **Defina em produção.** |
| `DATABASE_URL` | `sqlite:///tasks.db` | URL do banco |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Bind do servidor (use `HOST=0.0.0.0` só atrás de proxy/container) |
| `DEBUG` | `false` | Modo debug do Flask (nunca em produção) |
| `CORS_ORIGINS` | vazio | Origens permitidas, separadas por vírgula |
| `ENABLE_ADMIN_ROUTES` | `false` | Habilita operações administrativas (`DELETE /users/<id>` e atribuir `role: admin`). Com a flag ligada, exigem `Authorization: Bearer <token>` de um usuário admin (token obtido em `POST /login`). Desligada, respondem `403`. |
| `TOKEN_MAX_AGE_SECONDS` | `3600` | Validade do token de login |
| `LOG_LEVEL` | `INFO` | Nível de log |

## Estrutura

```
app.py          composition root (create_app) + start
config/         leitura das variáveis de ambiente
models/         entidades + acesso a dados (database.py: db, init, transação)
controllers/    fluxo de cada caso de uso
services/       relatórios e tokens de autenticação
routes/         blueprints (mapeamento HTTP → controller)
middlewares/    error handler central e autorização admin
utils/          constantes, validadores, erros de domínio, datas, hash de senha
```
