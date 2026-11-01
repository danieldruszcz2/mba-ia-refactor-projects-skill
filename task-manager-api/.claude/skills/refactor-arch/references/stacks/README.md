# Guias por stack

Cada arquivo concretiza, para uma stack, os conceitos agnósticos do núcleo da skill. Leia **apenas** o da stack detectada na Fase 1.

| Arquivo | Stack |
|---|---|
| `python.md` | Python (Flask, FastAPI, Django, ...) |
| `node.md` | JavaScript / TypeScript em Node.js (Express, NestJS, Fastify, Koa, ...) |
| `java.md` | Java / Kotlin na JVM (Spring Boot, Jakarta EE, Micronaut, Quarkus, Javalin, Ktor, ...) |
| `dotnet.md` | C# / .NET (ASP.NET Core Web API, Minimal APIs) |
| `go.md` | Go (net/http, Gin, Echo, Fiber, chi) |
| `php.md` | PHP (Laravel, Symfony, Slim, PHP puro) |
| `ruby.md` | Ruby (Rails, Sinatra, ...) |

## Formato (use-o para criar um guia novo)

Todo guia tem as mesmas seções, para que o núcleo possa referenciá-las por nome:

1. **Detecção** — onde está a versão da linguagem; tabela de frameworks (dependência + sinal no código); padrões de busca de rotas; entry point e porta padrão.
2. **Ambiente** — instalar dependências, build, start, testes; diretórios a ignorar.
3. **Padrões de busca** — regex/sinais por `AP-xx` (complementam os genéricos do catálogo).
4. **APIs deprecated** — tabela "deprecated → moderno (versão)". Não exaustiva.
5. **Idiomas** — mecanismo idiomático por `P-xx` do playbook.
6. **Estrutura alvo** — como as camadas do `mvc-guidelines.md` se mapeiam para a convenção da stack.
7. **Armadilhas** — erros comuns ao mover código nessa stack.

Regras para manter os guias genéricos: nada de nomes de projetos, entidades ou domínios específicos; nomes de APIs/ferramentas sim, trechos de código de aplicação não.
