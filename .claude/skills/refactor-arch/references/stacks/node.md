# Stack: Node.js (JavaScript / TypeScript)

## 1. Detecção

**Versão:** `engines.node` (`package.json`), `.nvmrc`, `.node-version`, `.tool-versions`, imagem base do `Dockerfile`. `tsconfig.json` → TypeScript. `"type": "module"` → ESM; senão CommonJS.

| Framework | Dependência | Sinal no código | Rotas (regex) | Porta padrão |
|---|---|---|---|---|
| Express | `express` | `express()`, `express.Router()` | `\.(get\|post\|put\|patch\|delete\|all)\(\s*['"\x60]/`, `app\.use\(\s*['"\x60]/` (prefixo) | nenhuma (ver `listen`) |
| NestJS | `@nestjs/core` | `@Module(`, `@Injectable(` | `@Controller\(`, `@(Get\|Post\|Put\|Patch\|Delete)\(` | 3000 (convenção) |
| Fastify | `fastify` | `fastify()` | `\.(get\|post\|put\|patch\|delete\|route)\(`, `register\(.*prefix` | nenhuma |
| Koa | `koa`, `@koa/router` | `new Koa()` | `router\.(get\|post\|put\|patch\|delete)\(` | nenhuma |
| Hapi | `@hapi/hapi` | `Hapi.server(` | `server\.route\(` | ver código |

**Entry point:** `scripts.start`/`main` no `package.json`; arquivo com `.listen(`.

## 2. Ambiente

| Gerenciador (lockfile) | Instalar | Build (se houver script) | Start | Testes |
|---|---|---|---|---|
| npm (`package-lock.json`) | `npm ci` (ou `npm install`) | `npm run build` | `npm start` | `npm test` |
| Yarn (`yarn.lock`) | `yarn install` | `yarn build` | `yarn start` | `yarn test` |
| pnpm (`pnpm-lock.yaml`) | `pnpm install` | `pnpm build` | `pnpm start` | `pnpm test` |

TypeScript normalmente exige build antes do start (ou roda com `ts-node`/`tsx` — veja o script).
**Ignorar:** `node_modules/`, `dist/`, `build/`, `coverage/`, `.next/`, `.turbo/`.

## 3. Padrões de busca

| AP | Padrões |
|---|---|
| AP-02 | `` `\s*(SELECT\|INSERT\|UPDATE\|DELETE)[^`]*\$\{ ``, `["'](SELECT\|INSERT\|UPDATE\|DELETE)[^"']*["']\s*\+`, `\.(query\|run\|all\|get\|exec)\(\s*["'\x60].*(\+\|\$\{)`, `sequelize\.query\(\s*\x60.*\$\{`, `knex\.raw\(\s*\x60.*\$\{`, `\$where`, `child_process.*exec\(.*(\+\|\$\{)` |
| AP-05 | `createHash\(\s*['"](md5\|sha1\|sha256)`, `Buffer\.from\(.*\)\.toString\(\s*['"]base64`, `btoa\(` perto de senha |
| AP-08 | `db\.(run\|all\|get\|query\|exec)\(`, `\.(findAll\|findOne\|findMany\|create)\(` em arquivos de rotas; `require\(['"](sqlite3\|pg\|mysql2\|mongoose)` em rotas |
| AP-09 | `^(let\|var)\s+\w+\s*=\s*(\{\}\|\[\]\|0\|null)`, `module\.exports\s*=\s*new\s` com estado |
| AP-10 | `new \w+(Service\|Repository\|Database\|Client\|Manager)\(` dentro de métodos/handlers; conexão aberta no topo do módulo |
| AP-12 | `cors\(\)`, `origin:\s*['"]\*`, `\.listen\(\s*\d+` (porta fixa) |
| AP-15 | `req\.(body\|query\|params)\.\w+` usado direto em lógica/query; `parseInt\(req\.` sem checagem |
| AP-16 | `catch\s*(\(\w*\))?\s*\{\s*\}`, `res\.status\(500\)\.(send\|json)\(\s*err`, `err\.(message\|stack)` em resposta; `if \(err\)` sem resposta |
| AP-17 | `function\s*\(err`/`\(err,\s*\w+\)\s*=>` aninhados; `--\w+\|\w+--` como contador de pendências; `\.then\(` sem `\.catch\(`; `\w+Sync\(` em handlers |
| AP-22 | `console\.(log\|error\|warn\|info)\(` |

## 4. APIs deprecated

| Deprecated / removido | Moderno |
|---|---|
| `new Buffer()` | `Buffer.from()` / `Buffer.alloc()` |
| `url.parse()`, `querystring` | `new URL()`, `URLSearchParams` |
| `crypto.createCipher()` (removido Node 22) | `crypto.createCipheriv()` com IV aleatório |
| `fs.exists()`, `util.isArray()` e demais `util.is*` | `fs.promises.access()`/`fs.existsSync()`, `Array.isArray()` |
| Módulo `punycode` embutido | pacote `punycode` do userland |
| Pacote `request` (deprecated) | `fetch` nativo (Node 18+) ou cliente HTTP já presente |
| `body-parser` como pacote separado | `express.json()` / `express.urlencoded()` |
| Express 4→5: `res.send(status, body)`, `res.json(status, obj)`, `req.param()`, `app.del()` | `res.status(s).send()`, `res.status(s).json()`, `req.params`/`req.query`/`req.body`, `app.delete()` |
| Mongoose 7+: API de callbacks (removida); opções `useNewUrlParser`/`useUnifiedTopology` | Promises/`async`; remover as opções |
| `var`; callbacks em APIs com versão Promise (`fs`, drivers) | `const`/`let`; `async`/`await`, `fs.promises`, `util.promisify` |

## 5. Idiomas

| P | Mecanismo |
|---|---|
| P-01 | `src/config/index` lendo `process.env`; NestJS `ConfigModule`; `dotenv` só se já existir. Exemplo: `.env.example` |
| P-02 | `sqlite3`/`mysql2`: `?` + array; `pg`: `$1..$n`; Sequelize `replacements`/`bind`; knex bindings `?`; ORM/query builder com filtros |
| P-05 | Express: middleware de erro com 4 parâmetros registrado por último; em Express 4, envolver handlers `async` para encaminhar rejeições a `next` (Express 5 faz isso nativamente); NestJS: Exception Filters; Fastify: `setErrorHandler` |
| P-06 | `crypto.scrypt` com salt de `crypto.randomBytes` + `crypto.timingSafeEqual` (sem dependência); `bcrypt`/`argon2` se presentes. Mascarar cartão antes de logar |
| P-07 | Middleware `requireAdmin` (Express/Koa); NestJS Guard; Fastify `preHandler` |
| P-08 | JOIN/`IN`; Sequelize `include`; Prisma `include`/`_count`; TypeORM `relations`/`leftJoinAndSelect`; Mongoose `populate`/aggregation |
| P-09 | Helper `BEGIN`/`COMMIT`/`ROLLBACK`; `sequelize.transaction()`; `prisma.$transaction`; `knex.transaction`; sessão Mongoose |
| P-10 | APIs Promise ou `util.promisify` no driver; `async`/`await`; `Promise.all` (preserva ordem) |
| P-11 | `joi`/`zod`/`class-validator`/`express-validator` se já existirem; senão validadores puros em `utils/validators` aplicados via middleware |
| P-13 | `pino`/`winston` se presentes; senão um logger fino com níveis; constantes em `config/constants` com `Object.freeze` (ou `enum`/`as const` em TS) |
| P-14 | `createApp({ db, config })` monta models → controllers → routers e devolve a app; `server` só faz `listen`; NestJS: módulos e providers |

## 6. Estrutura alvo

- **Express / Koa / Fastify:** `package.json` (start aponta para o entry real) + `src/` com `app` (cria app, registra middlewares e rotas), `server` (opcional: `listen`), `config/`, `models/` (repositórios + conexão), `controllers/`, `services/` (opcional), `routes/` (camada View), `middlewares/`, `utils/`.
- **NestJS:** módulos por domínio (`*.module`, `*.controller` fino, `*.service`, `*.repository`/entity, DTOs). Corrija vazamentos dentro dessa convenção.

## 7. Armadilhas

- Ordem de middlewares: parsing do body antes das rotas; error handler por último.
- Prefixo de router (`app.use('/api', router)`) somado ao caminho do handler — compare com o inventário.
- Não misture `require` e `import` — siga o sistema de módulos do projeto.
- TypeScript: recompile antes de validar; verifique `outDir` e o caminho do start.
- `npm start` pode lançar um processo filho — derrube pelo processo que escuta na porta.
