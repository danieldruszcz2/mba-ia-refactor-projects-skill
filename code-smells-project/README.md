# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo (senhas gravadas com hash).

## Configuração

Toda a configuração vem de variáveis de ambiente (ver `.env.example`):

| Variável | Default | Descrição |
|---|---|---|
| `SECRET_KEY` | aleatória por processo | Chave de sessão do Flask. **Defina em produção.** |
| `DEBUG` | `false` | Modo debug do Flask. Nunca ligue em produção. |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Endereço de bind. Use `HOST=0.0.0.0` em container. |
| `APP_ENV` | `producao` | Valor exibido em `/health`. |
| `LOG_LEVEL` | `INFO` | Nível do `logging`. |
| `DATABASE_PATH` | `<projeto>/loja.db` | Arquivo SQLite. |
| `CORS_ORIGINS` | `*` | Origens permitidas, separadas por vírgula. |
| `ENABLE_ADMIN_ROUTES` | `false` | Liga `/admin/reset-db` e `/admin/query` (desligadas respondem `403`). |
| `ADMIN_TOKEN` | vazio | Token exigido no header `X-Admin-Token` quando as rotas admin estão ligadas. |

`/admin/query` aceita apenas uma instrução `SELECT`, executada numa conexão somente leitura.

## Estrutura

```
app.py          composition root (create_app)
config/         leitura do ambiente
models/         conexão SQLite por requisição, schema/seed e acesso a dados
services/       regras de pedido, relatório e notificações
controllers/    fluxo de cada caso de uso
routes/         Blueprints (mapeamento HTTP → controller)
middlewares/    error handler central e proteção das rotas admin
utils/          validação, constantes, erros de domínio e hash de senha
```
