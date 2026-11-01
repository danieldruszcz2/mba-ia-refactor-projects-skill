# Stack: PHP

## 1. Detecção

**Versão:** `require.php` no `composer.json`, `config.platform.php`, imagem do `Dockerfile`.

| Framework | Dependência | Rotas (regex) | Start / porta |
|---|---|---|---|
| Laravel / Lumen | `laravel/framework` / `laravel/lumen-framework` | `Route::(get\|post\|put\|patch\|delete\|apiResource\|resource\|prefix\|group)\(` em `routes/*.php` | `php artisan serve` (8000) |
| Symfony | `symfony/framework-bundle` | `#\[Route\(`, `@Route\(`, `config/routes*.yaml` | `symfony serve` / `php -S` |
| Slim | `slim/slim` | `\$app->(get\|post\|put\|patch\|delete\|group)\(` | `php -S` |
| PHP puro | — | `\$_SERVER\['REQUEST_METHOD'\]`, `switch`/`if` sobre a URI em `index.php` | `php -S 127.0.0.1:8000 -t <docroot>` |

## 2. Ambiente

- Instalar: `composer install`. Sem build. Testes: `vendor/bin/phpunit` / `php artisan test` / `vendor/bin/pest`.
- Laravel: `.env` a partir de `.env.example` + `php artisan key:generate` se faltar a chave (apenas no ambiente de teste).
- **Ignorar:** `vendor/`, `storage/framework/`, `bootstrap/cache/`, `var/cache/`, `var/log/`.

## 3. Padrões de busca

| AP | Padrões |
|---|---|
| AP-01 | `.env` versionado; `define\(\s*['"]\w*(PASS\|KEY\|SECRET\|TOKEN)\w*['"]\s*,\s*['"]`; literais sensíveis em `config/*.php` |
| AP-02 | `(mysqli_query\|->query\|->exec)\(\s*["'].*(\$\w+\|\.\s*\$)`, `"(SELECT\|INSERT\|UPDATE\|DELETE)[^"]*\$\w+`, `DB::(select\|statement\|unprepared)\(\s*["'].*\$`, `(whereRaw\|orderByRaw\|selectRaw)\(.*\$` |
| AP-05 | `(md5\|sha1\|crypt)\(\|hash\(\s*['"](md5\|sha1\|sha256)` perto de senha; `base64_encode\(.*pass` |
| AP-06 | modelo inteiro em resposta sem `$hidden`/Resource; `->getMessage\(\)` em resposta |
| AP-08 | `DB::\|->query\(\|new PDO\(` em controllers ou closures de rota |
| AP-09 | `global \$`, `\$GLOBALS\[`, `static \$\w+` mutável |
| AP-12 | `APP_DEBUG=true` versionado, `display_errors\s*=\s*(On\|1)`, `ini_set\(\s*['"]display_errors['"],\s*['"]?1` |
| AP-15 | `\$_(GET\|POST\|REQUEST)\[` usado direto; `\$request->(input\|get\|all)\(` sem validação |
| AP-16 | `catch\s*\(\s*\\?(Exception\|Throwable)\s+\$\w+\s*\)\s*\{\s*\}`, operador `@` suprimindo erro, `die\(\|exit\(` com mensagens |
| AP-22 | `echo \|var_dump\(\|print_r\(` fora de views; `error_log\(` como log de aplicação |

## 4. APIs deprecated

| Deprecated / removido | Moderno |
|---|---|
| `mysql_*` (removido 7.0) | PDO / mysqli com prepared statements |
| `create_function`, `each()` (removidos 8.0) | closures, `foreach` |
| `FILTER_SANITIZE_STRING`, `strftime` (deprecated 8.1) | `htmlspecialchars`/validação; `DateTime::format`/`IntlDateFormatter` |
| Interpolação `${var}`, propriedades dinâmicas, `utf8_encode/decode` (deprecated 8.2) | `{$var}`, propriedades declaradas, `mb_convert_encoding` |
| Tipo nullable implícito em parâmetro (deprecated 8.4) | `?Tipo` explícito |
| Laravel: `$dates` no model (removido 10) | `$casts` |
| Symfony: anotações de rota/Doctrine | atributos PHP 8 |

## 5. Idiomas

| P | Mecanismo |
|---|---|
| P-01 | `.env` + `.env.example`; Laravel: `env()` só dentro de `config/*.php`, código usa `config()`; Symfony: `%env(VAR)%`; puro: classe de config lendo `getenv`/`$_ENV` |
| P-02 | PDO `prepare` + `execute` com `?` ou `:nome`; bindings do query builder/Eloquent; `DB::select('... ?', [$v])` |
| P-05 | Laravel: handler de exceções (`bootstrap/app.php` `withExceptions` no 11+, ou `App\Exceptions\Handler`); Symfony: listener de `kernel.exception`; Slim: `ErrorMiddleware`; puro: `set_exception_handler` |
| P-06 | `password_hash(PASSWORD_DEFAULT)`, `password_verify`, `password_needs_rehash` (rehash nativo); Laravel `Hash::make`; `$hidden` no Eloquent ou API Resources; `hash_equals` para tokens |
| P-07 | Middleware de rota; Laravel Gates/Policies; Symfony `IS_GRANTED` |
| P-08 | Eloquent `with()`/`withCount()`; Doctrine `JOIN FETCH`; agregação no banco |
| P-09 | `$pdo->beginTransaction()`/`commit()`/`rollBack()`; `DB::transaction(fn)`; Doctrine `wrapInTransaction` |
| P-11 | Laravel `FormRequest`/`$request->validate`; Symfony Validator; validadores puros |
| P-13 | Logger PSR-3 (Monolog, `Log::`); constantes de classe / `enum` (8.1+) |
| P-14 | Container do framework (service container Laravel, autowiring Symfony, PHP-DI); puro: arquivo de bootstrap que monta as dependências |

## 6. Estrutura alvo

- **Laravel / Symfony:** já são MVC — controllers finos, `Services`/`Actions`, models/repositories, `FormRequest`/DTOs, middleware. Corrija vazamentos dentro da convenção.
- **PHP puro / Slim:** `public/index.php` (front controller), `src/Config`, `src/Models` (ou `Repositories`), `src/Controllers`, `src/Services`, `src/Middleware`, arquivo de rotas; autoload PSR-4 pelo Composer.

## 7. Armadilhas

- Namespace PSR-4 precisa casar com o caminho — rode `composer dump-autoload` após mover classes.
- Laravel: caches de config/rotas (`php artisan config:clear`, `route:clear`) mascaram mudanças.
- Docroot (`public/`) e reescrita de URL mudam os caminhos — valide com o mesmo servidor da baseline.
