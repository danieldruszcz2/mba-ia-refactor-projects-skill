# Stack: Go

## 1. Detecção

**Versão:** diretivas `go 1.x` e `toolchain` no `go.mod`.

| Framework | Dependência | Rotas (regex) | Porta padrão |
|---|---|---|---|
| net/http | stdlib | `HandleFunc\(\|Handle\(` (Go 1.22+: padrões `"GET /caminho"`) | argumento de `ListenAndServe` |
| Gin | `github.com/gin-gonic/gin` | `\.(GET\|POST\|PUT\|PATCH\|DELETE)\(`, `\.Group\(` (prefixo) | 8080 (`r.Run()`) |
| Echo | `github.com/labstack/echo` | `\.(GET\|POST\|PUT\|PATCH\|DELETE)\(`, `\.Group\(` | argumento de `Start` |
| Fiber | `github.com/gofiber/fiber` | `\.(Get\|Post\|Put\|Patch\|Delete)\(`, `\.Group\(` | argumento de `Listen` |
| chi | `github.com/go-chi/chi` | `\.(Get\|Post\|Put\|Patch\|Delete)\(`, `\.Route\(`/`\.Mount\(` | argumento de `ListenAndServe` |

**Entry point:** `package main` com `func main()` — na raiz ou em `cmd/<app>/`.

## 2. Ambiente

- Instalar: `go mod download`. Build: `go build ./...`. Start: `go run .` ou `go run ./cmd/<app>` (ou o binário gerado). Testes: `go test ./...` (`-race` ajuda a achar AP-09).
- **Ignorar:** `vendor/` (dependências vendorizadas), `bin/`.

## 3. Padrões de busca

| AP | Padrões |
|---|---|
| AP-02 | `fmt\.Sprintf\(\s*"(SELECT\|INSERT\|UPDATE\|DELETE)`, `(Query\|QueryRow\|Exec)(Context)?\([^)]*"\s*\+`, GORM `\.(Where\|Raw\|Exec\|Order)\(\s*(fmt\.Sprintf\|"[^"]*"\s*\+)`, `exec\.Command\(\s*"(sh\|bash)",\s*"-c"` |
| AP-05 | `(md5\|sha1\|sha256)\.(Sum\w*\|New)\(` perto de senha; `base64` sobre senha |
| AP-08 | `\*sql\.DB\|\*gorm\.DB\|\*sqlx\.DB` usado em handlers |
| AP-09 | `^var \w+\s*=\s*(map\|\[\]\|make\()` mutado por handlers (data race); `var db \*` global |
| AP-10 | conexão aberta em `init()`; handlers usando globais em vez de struct com dependências |
| AP-12 | `AllowAllOrigins:\s*true`, `AllowOrigins:\s*\[\]string\{"\*"\}`, `gin\.SetMode\(gin\.DebugMode\)` fixo |
| AP-13 | consulta dentro de `for ... range` sobre resultados |
| AP-15 | erro de `Decode`/`Bind`/`strconv\.\w+` ignorado (`_ =`, `, _ :=`) |
| AP-16 | `_\s*=\s*\w+\(`/`, _\s*:?=` em funções que retornam erro; `if err != nil \{\s*\}`; `http\.Error\(w,\s*err\.Error\(\)`; `panic\(\|log\.Fatal` em handlers |
| AP-17 | `go func` sem `WaitGroup`/`errgroup`/canal de erro; `rows\.Close\(\)` ausente; `context` ignorado |
| AP-22 | `fmt\.Print(ln\|f)?\(` em código de aplicação; `log\.Print` sem níveis onde há logger estruturado |

## 4. APIs deprecated

| Deprecated | Moderno |
|---|---|
| `io/ioutil` (1.16) | funções equivalentes em `io` e `os` |
| `rand.Seed` (1.20) | gerador semeado automaticamente / `rand.New(rand.NewSource(..))`; `math/rand/v2` (1.22) |
| `math/rand` para tokens/segredos | `crypto/rand` |
| `strings.Title` (1.18) | `golang.org/x/text/cases` |
| `golang.org/x/net/context` | `context` |
| `httputil.ReverseProxy.Director` (1.20, preferir) | `Rewrite` |
| `github.com/dgrijalva/jwt-go` (sem manutenção) | `github.com/golang-jwt/jwt` |
| `log` sem níveis para logs de aplicação | `log/slog` (1.21+) |

## 5. Idiomas

| P | Mecanismo |
|---|---|
| P-01 | Pacote `config` com struct preenchida por `os.LookupEnv`/`os.Getenv` (ou `envconfig`/`viper` se presentes). Exemplo: `.env.example` |
| P-02 | `database/sql`: `?` (MySQL/SQLite) ou `$1` (Postgres); GORM `Where("col = ?", v)`; `sqlx` named params |
| P-05 | Handlers retornam `error`; um adaptador/middleware mapeia tipos de erro (`errors.As`) para status e formato único; Gin: `c.Error` + middleware; Echo: `HTTPErrorHandler`; Fiber: `ErrorHandler` |
| P-06 | `golang.org/x/crypto/bcrypt` (`GenerateFromPassword`/`CompareHashAndPassword`) ou `argon2`; `crypto/subtle.ConstantTimeCompare` para tokens |
| P-07 | Middleware `func(http.Handler) http.Handler`; grupo de rotas com middleware (Gin/Echo/chi) |
| P-08 | JOIN; `IN` com `sqlx.In`; GORM `Preload`/`Joins`; agregação no banco |
| P-09 | `db.BeginTx` + `defer tx.Rollback()` + `tx.Commit()`; GORM `db.Transaction(func(tx) error)` |
| P-10 | `errgroup.Group`, `sync.WaitGroup`, propagação de `context.Context` |
| P-11 | Tags do `go-playground/validator` (usadas pelo binding do Gin/Echo) ou métodos `Validate()` explícitos |
| P-13 | `log/slog` ou o logger já usado (zap, zerolog); blocos `const` / tipos com constantes |
| P-14 | `main()` monta config → db → repositórios → services → handlers → router; dependências como campos de struct; nada de globais de pacote |

## 6. Estrutura alvo

`cmd/<app>/main.go` (ou `main.go` na raiz, se o start original for `go run .`) + `internal/config`, `internal/model` ou `internal/repository` (Models), `internal/service`, `internal/handler` (Controllers), `internal/router` (Routes), `internal/middleware`. Pacotes por camada ou por domínio — siga o que o projeto usa.

## 7. Armadilhas

- Imports usam o caminho do módulo (`module` do `go.mod`) + pasta; ciclos de import são erro de compilação.
- Imports e variáveis não usados são erro de compilação — remova junto ao mover código.
- `internal/` só é visível dentro do módulo; identificadores exportados precisam de inicial maiúscula.
- `go run` compila num binário temporário — derrube pelo processo que escuta na porta.
