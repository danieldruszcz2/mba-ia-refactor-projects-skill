# Stack: Ruby

## 1. Detecção

**Versão:** diretiva `ruby` no `Gemfile`, `.ruby-version`, `.tool-versions`.

| Framework | Dependência | Rotas (regex) | Start / porta |
|---|---|---|---|
| Rails | `rails` | `config/routes.rb`: `(get\|post\|put\|patch\|delete\|resources?\|namespace\|scope)\b` (use `bin/rails routes` para a lista final) | `bin/rails server` (3000) |
| Sinatra | `sinatra` | `^\s*(get\|post\|put\|patch\|delete)\s+['"]/` | `ruby app.rb` (4567) / `rackup` (9292) |
| Grape / Roda / Hanami | nome da gem | DSL de rotas do framework | `rackup` / ver README |

## 2. Ambiente

- Instalar: `bundle install`. Sem build. Rails: `bin/rails db:prepare` se o banco precisar ser criado (apenas no ambiente de teste). Testes: `bundle exec rspec` / `bin/rails test`.
- **Ignorar:** `vendor/bundle/`, `.bundle/`, `tmp/`, `log/`, `node_modules/`, `public/assets/`.

## 3. Padrões de busca

| AP | Padrões |
|---|---|
| AP-01 | literais em `config/database.yml`, `config/secrets.yml`, inicializadores; `secret_key_base\s*=\s*['"]` |
| AP-02 | `(where\|find_by_sql\|execute\|exec_query\|order\|pluck\|select\|joins\|group)\(\s*["'][^"']*#\{`, `"(SELECT\|INSERT\|UPDATE\|DELETE)[^"]*#\{`, `` `.*#\{ `` (shell) |
| AP-05 | `Digest::(MD5\|SHA1\|SHA256)` perto de senha; `Base64` sobre senha |
| AP-06 | `render json: @?\w+` com model inteiro sem `only:`/`except:`/serializer; `e\.message` em resposta |
| AP-08 | consultas ActiveRecord não triviais ou `connection\.execute` em controllers/rotas |
| AP-09 | `\$\w+\s*=`, `@@\w+`, constantes mutáveis alteradas em runtime |
| AP-11 | vários `save!\|create!\|update!\|destroy` sem `transaction do` |
| AP-12 | `consider_all_requests_local\s*=\s*true` em produção, `origins\s+['"]\*` (rack-cors), `set :show_exceptions, true` |
| AP-13 | associação acessada dentro de `.each` sem `includes`/`preload`; `.length` em relação |
| AP-15 | `params\[:\w+\]` sem strong params; `params\.permit!` |
| AP-16 | `rescue\s*(=>\s*\w+)?\s*\n\s*(nil\|end)`, `rescue Exception`, `e\.(message\|backtrace)` em resposta |
| AP-22 | `^\s*(puts\|p\|pp\|print)\s` em código de aplicação |

## 4. APIs deprecated

| Deprecated / removido | Moderno |
|---|---|
| Rails: `update_attributes` (removido 6.1) | `update` |
| Rails: `before_filter`/`after_filter` (removidos 5.1) | `before_action`/`after_action` |
| Rails: `render text:` (removido 5.1) | `render plain:` |
| Rails: `attr_accessible` (removido 4) | strong parameters |
| Rails 7.1: `secrets.yml` / `Rails.application.secrets` | credentials / variáveis de ambiente |
| Ruby 3.0: `URI.escape` (removido) | `URI.encode_www_form_component` / `CGI.escape` |
| Ruby 3.2: `File.exists?`, `Dir.exists?`, `Fixnum`/`Bignum` (removidos) | `File.exist?`, `Dir.exist?`, `Integer` |

## 5. Idiomas

| P | Mecanismo |
|---|---|
| P-01 | `ENV.fetch` em config/inicializadores; Rails credentials; `dotenv` só se presente. Exemplo: `.env.example` |
| P-02 | `where("col = ?", v)` ou condições em hash; `sanitize_sql_array`; binds em `exec_query` |
| P-05 | `rescue_from` no `ApplicationController`; Sinatra: blocos `error` |
| P-06 | `has_secure_password` (bcrypt) / `BCrypt::Password`; serializers ou `as_json(only:)`; `ActiveSupport::SecurityUtils.secure_compare` para tokens |
| P-07 | `before_action :require_admin` + flag de config |
| P-08 | `includes`/`preload`/`eager_load`, `counter_cache`, `group(...).count` |
| P-09 | `ActiveRecord::Base.transaction do ... end` |
| P-11 | validações do model + strong params; `dry-validation` se presente |
| P-13 | `Rails.logger` / `Logger.new`; constantes em módulos |
| P-14 | Rails: convenções + objetos de serviço recebendo dependências; Sinatra: app modular composta no `config.ru` |

## 6. Estrutura alvo

- **Rails:** já é MVC — controllers finos, `app/services` (POROs) para regras, models com validações e escopos, serializers para respostas.
- **Sinatra / Rack:** `config.ru` (composition root) + `app/` ou `lib/` com `models/`, `controllers/` (módulos de rota), `services/`, `middlewares/`, `config/`.

## 7. Armadilhas

- Rails/Zeitwerk exige que o nome do arquivo corresponda à constante — renomeie ambos juntos.
- Preloaders (Spring, bootsnap) podem servir código antigo — reinicie o processo ao validar.
