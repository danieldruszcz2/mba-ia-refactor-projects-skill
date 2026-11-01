# Stack: C# / .NET

## 1. Detecção

**Versão:** `<TargetFramework>` no `.csproj` (ex.: `net8.0`; `net4x` = .NET Framework legado), `global.json` (SDK).

| Framework | Sinal no código | Rotas (regex) | Porta padrão |
|---|---|---|---|
| ASP.NET Core Web API (controllers) | `[ApiController]`, `: ControllerBase` | `\[(HttpGet\|HttpPost\|HttpPut\|HttpPatch\|HttpDelete\|Route)\(` (somar o `[Route]` da classe) | `Properties/launchSettings.json` (`applicationUrl`), `ASPNETCORE_URLS`, `ASPNETCORE_HTTP_PORTS` |
| Minimal APIs | `WebApplication.CreateBuilder`, `app.Map*` | `\.Map(Get\|Post\|Put\|Patch\|Delete\|Group)\(` | idem |
| ASP.NET (.NET Framework) | `Global.asax`, `System.Web` | `\[Route\(`, `RouteConfig` | IIS/IIS Express |

**Entry point:** `Program.cs` (top-level statements ou `Main`), `Startup.cs` em projetos antigos. Com várias `.csproj` numa `.sln`, o servidor é o projeto `Microsoft.NET.Sdk.Web`.

## 2. Ambiente

- Instalar: `dotnet restore`. Build: `dotnet build`. Start: `dotnet run --project <Projeto.Web.csproj>` (ou `dotnet <artefato>.dll` após `dotnet publish`). Testes: `dotnet test`.
- Porta fixa para a validação: `ASPNETCORE_URLS=http://127.0.0.1:<porta>`.
- **Ignorar:** `bin/`, `obj/`, `.vs/`, `TestResults/`.

## 3. Padrões de busca

| AP | Padrões |
|---|---|
| AP-01 | `appsettings*.json` com `Password=[^;"]+`, chaves `Secret\|ApiKey\|Token` com valor literal; `ConnectionStrings` com credenciais |
| AP-02 | `new SqlCommand\(\s*\$?"[^"]*(\{\|"\s*\+)`, `CommandText\s*=\s*\$?".*(\{\|\+)`, `(FromSqlRaw\|ExecuteSqlRaw)\(\s*(\$"\|"[^"]*"\s*\+)`, `string\.Format\(\s*"(SELECT\|INSERT\|UPDATE\|DELETE)`. Obs.: `FromSqlInterpolated`/`ExecuteSqlInterpolated` são parametrizados |
| AP-05 | `(MD5\|SHA1\|SHA256)\.(Create\|HashData)` perto de senha, `Convert\.ToBase64String` sobre senha |
| AP-08 | `DbContext\|SqlConnection\|IDbConnection` injetado/usado em controllers ou endpoints |
| AP-09 | campos `static` não-`readonly`; serviços `AddSingleton` com estado mutável; `DbContext` registrado como singleton |
| AP-10 | `new \w+(Service\|Repository\|Context\|Client)\(` em controllers; `new HttpClient\(` por requisição |
| AP-12 | `AllowAnyOrigin\(\)`, `UseDeveloperExceptionPage\(\)` fora de `IsDevelopment()`, `"Urls"\s*:\s*"http://0\.0\.0\.0` |
| AP-13 | consultas EF dentro de `foreach`; acesso a navegação lazy em loop; `.ToList\(\)` seguido de `Where`/`Count` em memória |
| AP-15 | DTOs sem DataAnnotations/validador; `int\.Parse\(` sobre entrada; entidade como parâmetro de ação |
| AP-16 | `catch\s*(\(\s*Exception(\s+\w+)?\s*\))?\s*\{\s*\}`, `ex\.(Message\|ToString\(\)\|StackTrace)` em resposta |
| AP-17 | `async void`, `\.Result\b`, `\.Wait\(\)`, `Task\.Run\(` sem `await` |
| AP-22 | `Console\.Write(Line)?\(`, `Debug\.WriteLine\(` |

## 4. APIs deprecated

| Deprecated / removido | Moderno |
|---|---|
| `BinaryFormatter` (obsoleto .NET 5, removido .NET 9) | `System.Text.Json` / serializadores seguros |
| `WebClient`, `HttpWebRequest` (obsoletos .NET 6) | `HttpClient` via `IHttpClientFactory` |
| `RNGCryptoServiceProvider`, `SHA1Managed` etc. (obsoletos .NET 6) | `RandomNumberGenerator`, `SHA256.HashData` |
| Construtores de `Rfc2898DeriveBytes` (obsoletos .NET 7+) | `Rfc2898DeriveBytes.Pbkdf2(...)` |
| `System.Data.SqlClient` | `Microsoft.Data.SqlClient` |
| `ISystemClock` (obsoleto .NET 8) | `TimeProvider` |
| Hosting com `Startup` + `WebHost.CreateDefaultBuilder` (legado) | `WebApplication.CreateBuilder` (.NET 6+) — migrar só se trivial; senão Manual Follow-up |

## 5. Idiomas

| P | Mecanismo |
|---|---|
| P-01 | `appsettings.json` sem segredos + variáveis de ambiente (`Secao__Chave`) + classes de Options (`IOptions<T>`); user-secrets em dev. Documente variáveis num `.env.example` ou `appsettings.Example.json` sem valores reais |
| P-02 | `SqlParameter`/`@nome`; Dapper com objeto de parâmetros; EF LINQ ou `FromSqlInterpolated` |
| P-05 | `UseExceptionHandler` + `IExceptionHandler` (.NET 8) ou middleware próprio; exceções de domínio com status. Só use `ProblemDetails` se preservar o formato original |
| P-06 | `PasswordHasher<T>` (`Microsoft.AspNetCore.Identity`; `VerifyHashedPassword` retorna `SuccessRehashNeeded`) ou `Rfc2898DeriveBytes.Pbkdf2` + `CryptographicOperations.FixedTimeEquals`; respostas via DTO/`record` |
| P-07 | `[Authorize(Policy = ...)]`/`RequireAuthorization`; endpoint filter ou middleware checando flag + token |
| P-08 | `Include`/`ThenInclude`, projeção com `Select`, `AsSplitQuery`, `CountAsync`/`GroupBy` no banco |
| P-09 | `SaveChanges` único por caso de uso; `Database.BeginTransactionAsync()`; `TransactionScope` |
| P-10 | `async`/`await` de ponta a ponta, `Task.WhenAll`, sem `.Result`/`.Wait()` |
| P-11 | DataAnnotations + `[ApiController]` (400 automático); FluentValidation se presente |
| P-13 | `ILogger<T>`; constantes em `static class`/`enum` |
| P-14 | DI nativa em `Program.cs` (`AddScoped`/`AddSingleton` corretos; `DbContext` scoped) como composition root |

## 6. Estrutura alvo

- **Controllers:** `Controllers/` (finos) → `Services/` → `Repositories/` ou `Data/` (DbContext) + `Models/Entities` e `Models/Dtos`, `Middleware/`, `Options/` (config), `Exceptions/`.
- **Minimal APIs:** `Endpoints/` com métodos de extensão `Map<Domínio>Endpoints` (finos), demais camadas iguais.

## 7. Armadilhas

- Mover arquivo não muda o `namespace` automaticamente — ajuste namespaces e `using`.
- Serialização padrão é camelCase; ao trocar entidade por DTO, mantenha os mesmos nomes de campo JSON.
- `launchSettings.json` só vale para `dotnet run` com perfil — use `ASPNETCORE_URLS` para fixar a porta.
- `ASPNETCORE_ENVIRONMENT` muda comportamento (página de exceção, config) — use o mesmo valor na baseline e na validação.
