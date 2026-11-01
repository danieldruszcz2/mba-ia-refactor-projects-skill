# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

## Configuração

Toda a configuração vem de variáveis de ambiente, documentadas em [`.env.example`](.env.example). Os defaults são seguros para desenvolvimento local:

- `DEBUG=false` e `HOST=127.0.0.1` (para expor na rede, defina `HOST=0.0.0.0` conscientemente).
- `SECRET_KEY` vazia gera uma chave aleatória por boot — defina uma fixa em produção.
- `CORS_ORIGINS` vazio desabilita CORS; informe as origens permitidas separadas por vírgula.
- Rotas `/admin/*` respondem `403` até que `ENABLE_ADMIN_ROUTES=true` e `ADMIN_TOKEN` sejam definidos; o token vai no header `X-Admin-Token`. `/admin/query` aceita apenas `SELECT` (somente leitura).

Senhas são armazenadas com hash (scrypt). Bancos antigos com senhas em texto puro são migrados automaticamente no boot.

## Estrutura

```
app.py          composition root (create_app) e start
config/         leitura das variáveis de ambiente
models/         conexão/schema/seed (database.py) e acesso a dados por entidade
services/       regras de pedido, relatório e notificações
controllers/    fluxo de cada caso de uso
routes/         Blueprints: mapeamento HTTP → controller
middlewares/    error handler central e proteção das rotas admin
utils/          constantes, erros de domínio, validadores e hashing de senha
```
