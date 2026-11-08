# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Configuração

Todas as configurações vêm de variáveis de ambiente (veja `.env.example`):

| Variável | Default | Descrição |
|---|---|---|
| `PORT` | `3000` | Porta HTTP |
| `DATABASE_PATH` | `:memory:` | Caminho do banco SQLite |
| `PAYMENT_GATEWAY_KEY` | vazio | Chave do gateway de pagamento |
| `ENABLE_ADMIN_ROUTES` | `false` | Habilita `GET /api/admin/financial-report` e `DELETE /api/users/:id` (desligadas → `403`) |
| `ADMIN_TOKEN` | vazio | Token exigido no header `X-Admin-Token` das rotas administrativas |
| `LOG_LEVEL` | `info` | `debug`, `info`, `warn` ou `error` |

Exemplo com rotas administrativas:

```bash
ENABLE_ADMIN_ROUTES=true ADMIN_TOKEN=troque-me npm start
```

## Estrutura

```
src/
├── app.js          # entry point: config → banco → createApp → listen
├── createApp.js    # composition root
├── config/         # variáveis de ambiente e constantes
├── models/         # conexão SQLite, schema/seed e repositórios
├── services/       # regras de checkout, relatório, usuários e gateway
├── controllers/    # validação de entrada e resposta HTTP
├── routes/         # mapeamento método + caminho → controller
├── middlewares/    # asyncHandler, requireAdmin, errorHandler
└── utils/          # erros, logger, hash de senha, máscara, validadores
```
