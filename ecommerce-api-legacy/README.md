# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000` (ou na porta de `PORT`). O banco SQLite é em memória por padrão e já carrega seeds automaticamente no boot.

## Configuração

Variáveis de ambiente (veja `.env.example`):

| Variável | Default | Descrição |
|---|---|---|
| `PORT` | `3000` | Porta HTTP |
| `DB_PATH` | `:memory:` | Caminho do banco SQLite |
| `PAYMENT_GATEWAY_KEY` | vazio | Chave do gateway de pagamento |
| `ENABLE_ADMIN_ROUTES` | `false` | Habilita `GET /api/admin/financial-report` e `DELETE /api/users/:id` (desabilitadas respondem `403`) |
| `ADMIN_TOKEN` | vazio | Token exigido em `Authorization: Bearer <token>` nas rotas admin |
| `LOG_LEVEL` | `info` | `debug`, `info`, `warn` ou `error` |

Exemplo com rotas admin habilitadas:

```bash
ENABLE_ADMIN_ROUTES=true ADMIN_TOKEN=troque-me npm start
```

## Estrutura

```
src/
├── app.js          # entry point: carrega config, abre o banco e sobe o servidor
├── createApp.js    # composition root: models → services → controllers → rotas
├── config/         # leitura do ambiente e constantes de domínio
├── models/         # conexão SQLite (Promises + transações), schema/seed e repositórios
├── services/       # checkout, gateway de pagamento, relatório financeiro, usuários
├── controllers/    # fluxo HTTP de cada caso de uso
├── routes/         # mapeamento método + caminho → controller
├── middlewares/    # error handler, proteção admin, async handler
└── utils/          # erros, validação, hash de senha, logger, máscara de cartão
```

Exemplos de requisições estão em `api.http`.
