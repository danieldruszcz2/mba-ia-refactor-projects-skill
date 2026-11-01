# Análise de Projeto — Heurísticas (Fase 1)

Objetivo: descobrir **o que** é o projeto (stack, banco, domínio) e **como** ele está organizado hoje, com base em evidências do próprio repositório. Nunca presuma — confirme lendo arquivos.

Este arquivo é agnóstico. Os sinais concretos de cada framework (dependências, anotações/decorators de rota, padrões de busca de endpoints, comando de start, porta padrão) estão em `references/stacks/<stack>.md` — leia-o assim que a linguagem for detectada (seção 2).

## Sumário
1. Inventário de arquivos
2. Detecção de linguagem (e escolha do guia de stack)
3. Detecção de framework
4. Detecção de banco de dados e modo de acesso
5. Build, entry point, comando de start e porta
6. Inventário de endpoints
7. Inferência de domínio
8. Classificação da arquitetura atual
9. Armadilhas comuns

---

## 1. Inventário de arquivos

- Liste recursivamente os arquivos, excluindo: `.git/`, `.claude/`, `reports/`, diretórios de IDE, diretórios de dependências e de saída de build. O `.gitignore` do projeto é a melhor fonte para saber quais são; complemente com as convenções do guia da stack.
- **Arquivos-fonte** = extensões da linguagem detectada. Não conte lockfiles, documentação, dados, arquivos gerados ou vendorizados.
- Conte linhas (aproximado é aceitável, prefixe com `~`). Ex.: `git ls-files` filtrado pelas extensões + contagem de linhas, ou leia os arquivos e some.
- Anote também arquivos de apoio úteis: coleções de requisições (`*.http`, Postman, Insomnia), especificações OpenAPI/Swagger, `README`, exemplos de env, `Dockerfile`/`docker-compose`, seeds e migrations — eles revelam endpoints, variáveis, dependências externas e como rodar.

## 2. Detecção de linguagem (e escolha do guia de stack)

Use o **manifesto de build/dependências** como evidência principal e a contagem de extensões como confirmação:

| Evidência | Linguagem | Guia |
|---|---|---|
| `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` | Python | `stacks/python.md` |
| `package.json` (+ `tsconfig.json` → TypeScript) | JavaScript / TypeScript | `stacks/node.md` |
| `pom.xml`, `build.gradle(.kts)` | Java / Kotlin (JVM) | `stacks/java.md` |
| `*.csproj`, `*.sln` | C# / .NET | `stacks/dotnet.md` |
| `go.mod` | Go | `stacks/go.md` |
| `composer.json` | PHP | `stacks/php.md` |
| `Gemfile` | Ruby | `stacks/ruby.md` |
| outro | — | sem guia: use seu conhecimento (ver `SKILL.md`) |

**Versão da linguagem:** procure a declaração no manifesto ou em arquivos de versão da ferramenta (o guia da stack lista onde). Se não declarada, informe "versão não declarada" e use a versão instalada no ambiente apenas como referência para checar APIs deprecated.

A sintaxe também denuncia a "era" do código (útil para APIs deprecated): construções antigas que a própria linguagem já substituiu indicam código legado.

**Múltiplas linguagens:** se o backend combina linguagens (ex.: um serviço principal + scripts), o guia é o da linguagem do servidor HTTP; trate as demais como apoio.

## 3. Detecção de framework

Procure o nome da dependência no manifesto **e** o padrão de uso no código (tabela "Frameworks" do guia da stack). As duas evidências juntas evitam confundir uma dependência declarada e não usada com o framework real.

Versão: a do manifesto. Se houver lockfile, a versão resolvida é mais precisa. Registre também extensões relevantes (CORS, ORM, validação, auth, clientes HTTP, logging).

## 4. Detecção de banco de dados e modo de acesso

Evidências, em ordem de força: dependência de driver/ORM no manifesto; string/URL de conexão (`<esquema>://...`); arquivos de banco no repositório; `docker-compose` com serviço de banco; configuração de datasource.

Classifique:
- **Tipo de banco:** em arquivo (ex.: SQLite), servidor relacional, documento, chave-valor, **em memória** (dados somem ao reiniciar — relevante para validação).
- **Modo de acesso** (afeta o playbook): **SQL cru** (strings SQL passadas a um driver), **ORM** (entidades mapeadas) ou **query builder**.
- **Tabelas/entidades:** procure DDL (`CREATE TABLE`), classes/structs de entidade mapeadas, schemas, migrations e seeds.

Anote onde a conexão é criada e se ela é global/compartilhada (alimenta o anti-pattern de estado global) e se o banco é **servidor externo** (afeta a estratégia de proteção de dados na validação).

## 5. Build, entry point, comando de start e porta

- **Build:** linguagens compiladas precisam de um passo de build antes de subir; registre o comando (wrapper do projeto, se existir, tem preferência sobre a ferramenta global).
- **Entry point:** a função/arquivo principal que cria o servidor HTTP. Fontes: scripts declarados no manifesto, `README`, `Procfile`, `Dockerfile` (`CMD`/`ENTRYPOINT`), configuração de execução da IDE commitada.
- **Porta:** argumento explícito no código, variável de ambiente lida no boot, arquivo de configuração, ou o default do framework (ver guia da stack).
- Anote se o boot faz efeitos colaterais (cria tabelas, roda seed, apaga dados) — importante para a baseline.

## 6. Inventário de endpoints

Busque as declarações de rota (padrões no guia da stack) e registre **método + caminho completo + arquivo:linha**. Caminho completo = prefixos acumulados (prefixo global, de módulo/router/grupo, de classe) + caminho do handler.

Rotas podem ser registradas dinamicamente (loops, registro programático, classes que montam rotas no construtor, convenções por nome) — leia o código além do grep. Se existir coleção de requisições ou especificação OpenAPI, use-a para confirmar e para obter **exemplos de body** válidos para o smoke test.

Para cada endpoint, anote se é **destrutivo/perigoso** (DELETE, reset, execução de SQL, cobrança real, envio de mensagens reais) — o smoke test trata esses com cuidado.

## 7. Inferência de domínio

Combine: nomes de tabelas/entidades, substantivos das rotas, nomes de funções de negócio (verbos do domínio) e o README. Descreva em uma linha: tipo de sistema + entidades principais (ex.: "API de <domínio> — <entidade>, <entidade> e <entidade>"). Não use o nome da pasta como prova única.

## 8. Classificação da arquitetura atual

Escolha a categoria que melhor descreve **o que o código faz**, não o que as pastas sugerem:

| Classificação | Sinais |
|---|---|
| **Monolito de arquivo único** | Rotas, acesso a dados, regras e config no mesmo arquivo |
| **God Class / God Module** | Uma classe/módulo concentra banco + rotas + regras de vários domínios; os demais arquivos são satélites |
| **Camadas nominais (pseudo-MVC)** | Existem pastas/arquivos com nomes de camadas, mas as responsabilidades vazam: SQL no controller, regra de negócio nas rotas, models anêmicos ou "faz-tudo", controllers que só repassam |
| **Parcialmente em camadas** | Parte do código respeita as camadas; ainda há lógica nas rotas, helpers/serviços ignorados, duplicação |
| **Em camadas (MVC/Clean/Hexagonal)** | Rotas finas, controllers/services com regras, camada de dados isolada; problemas pontuais |

Justifique com evidência concreta (tamanho do arquivo, quantos domínios ele cobre, quais camadas mistura, quem chama quem). Registre também **código morto estrutural**: módulos/serviços/helpers que existem mas nunca são importados — é sinal forte de camadas nominais.

## 9. Armadilhas comuns

- **Não confie no nome do arquivo.** Um arquivo de "models" pode conter controllers; um de "utils" pode conter config com segredos.
- **Monorepos / multi-módulo**: se houver vários manifestos ou módulos de build, identifique qual contém o servidor HTTP do diretório atual; analise-o e mencione os demais.
- **Código gerado ou vendorizado** (minificados, clientes gerados, migrations automáticas) não entra na auditoria de estilo.
- **Versões com faixa** (`^`, `~`, `>=`): use a major/minor mínima para checar APIs deprecated; o lockfile, se houver, dá a versão real.
- **Banco em memória ou criado no boot**: a baseline e a validação precisam subir a app do zero (ver `validation.md`).
