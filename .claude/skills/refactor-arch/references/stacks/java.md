# Stack: Java / Kotlin (JVM)

## 1. Detecção

**Versão:** Maven — `<java.version>`, `<maven.compiler.release>`/`source`/`target`, versão do `spring-boot-starter-parent`; Gradle — `java { toolchain { languageVersion } }`, `sourceCompatibility`, `jvmTarget` (Kotlin). Também `.java-version`, `.sdkmanrc`, imagem do `Dockerfile`.

| Framework | Dependência | Sinal no código | Rotas (regex) | Porta padrão |
|---|---|---|---|---|
| Spring Boot (MVC/WebFlux) | `spring-boot-starter-web` / `-webflux` | `@SpringBootApplication`, `@RestController` | `@(Get\|Post\|Put\|Patch\|Delete\|Request)Mapping\(` (somar o `@RequestMapping` da classe) | 8080 (`server.port`) |
| Jakarta EE / JAX-RS | `jakarta.ws.rs`, `jersey`, `resteasy` | `@Path(` em classe | `@(GET\|POST\|PUT\|PATCH\|DELETE)` + `@Path\(` | do servidor |
| Quarkus | `io.quarkus:*` | `@Path(`, `application.properties` | igual JAX-RS | 8080 (`quarkus.http.port`) |
| Micronaut | `io.micronaut:*` | `@Controller(` | `@(Get\|Post\|Put\|Patch\|Delete)\(` | 8080 |
| Javalin / Spark | `io.javalin` / `com.sparkjava` | `Javalin.create(` | `\.(get\|post\|put\|patch\|delete)\(\s*"/` | ver código |
| Ktor (Kotlin) | `io.ktor:*` | `embeddedServer(`, `routing {` | `(get\|post\|put\|patch\|delete)\(\s*"/` | ver `application.conf` |
| Servlet puro | `jakarta.servlet`/`javax.servlet` | `extends HttpServlet` | `@WebServlet\(`, `web.xml` | do container |

**Entry point:** classe com `public static void main` (`@SpringBootApplication`), `Main-Class` no manifesto do jar, `Dockerfile`. Porta: `application.properties`/`application.yml` (`server.port`), variável `SERVER_PORT`, ou default do framework.

## 2. Ambiente

| Build (evidência) | Build sem testes | Start | Testes |
|---|---|---|---|
| Maven (`pom.xml`, `mvnw`) | `./mvnw -q -DskipTests package` | `java -jar target/<artefato>.jar` ou `./mvnw spring-boot:run` / `./mvnw quarkus:dev` | `./mvnw test` |
| Gradle (`build.gradle(.kts)`, `gradlew`) | `./gradlew build -x test` | `java -jar build/libs/<artefato>.jar` ou `./gradlew bootRun` / `./gradlew run` | `./gradlew test` |

Prefira o wrapper do projeto (`mvnw`/`gradlew`; no Windows `mvnw.cmd`/`gradlew.bat`). O JDK instalado precisa atender à versão declarada — se não atender, registre como bloqueio em vez de mudar a versão do projeto. Use o comando de start documentado no README quando houver.
**Ignorar:** `target/`, `build/`, `.gradle/`, `out/`, `bin/`, `.idea/`, `*.iml`.

## 3. Padrões de busca

| AP | Padrões |
|---|---|
| AP-01 | Em `application*.properties`/`*.yml`: chaves `password\|secret\|key\|token` com valor literal (não `${...}`); `DriverManager\.getConnection\(.*"[^"]+"\s*,\s*"[^"]+"\s*\)` |
| AP-02 | `(executeQuery\|executeUpdate\|execute\|prepareStatement\|createQuery\|createNativeQuery)\(\s*"[^"]*"\s*\+`, `"\s*(SELECT\|INSERT\|UPDATE\|DELETE)[^"]*"\s*\+`, `String\.format\(\s*"(SELECT\|INSERT\|UPDATE\|DELETE)`, `jdbcTemplate\.\w+\(\s*"[^"]*"\s*\+`, `@Query\(.*nativeQuery\s*=\s*true` (conferir concatenação/SpEL), Kotlin `"\$\{?\w+` dentro de SQL, `Runtime\.getRuntime\(\)\.exec\(`, `ProcessBuilder\(` com entrada |
| AP-03 | classe `@RestController`/`@Path` que também usa `JdbcTemplate`/`EntityManager`/`Connection` e contém regras |
| AP-04 | `permitAll\(\)` em caminhos admin; ausência de configuração de segurança com rotas destrutivas; `@CrossOrigin` + rotas admin |
| AP-05 | `MessageDigest\.getInstance\(\s*"(MD5\|SHA-1\|SHA1\|SHA-256)"`, `Base64\.getEncoder\(\)` perto de senha, `NoOpPasswordEncoder`, `password\.equals\(` |
| AP-06 | `@Entity` com campo de senha devolvido direto pelo controller (sem DTO/`@JsonIgnore`); `e\.getMessage\(\)` em `ResponseEntity`; `server\.error\.include-stacktrace=always` |
| AP-08 | `JdbcTemplate\|EntityManager\|DriverManager\|DataSource\|Connection\b` em classes `@RestController`/`@Controller`/`@Path` |
| AP-09 | `static\s+(?!final)[\w<>,\s\[\]]+\s+\w+\s*=`; coleções `static final (Map\|List\|Set)` mutadas em métodos; campos de instância mutáveis em beans singleton escritos durante requisições |
| AP-10 | `new \w+(Service\|Repository\|Dao\|Client)\(` dentro de beans; `@Autowired` em campo (preferir construtor); service locator (`getBean(` em código de negócio) |
| AP-11 | várias chamadas `save\|update\|delete\|executeUpdate` no mesmo método sem `@Transactional`; `@Transactional` em método `private` ou chamado de dentro da própria classe (não tem efeito) |
| AP-12 | `allowedOrigins\(\s*"\*"\)`, `@CrossOrigin\(\s*(origins\s*=\s*"\*")?\s*\)`, `management\.endpoints\.web\.exposure\.include\s*=\s*\*`, `spring\.h2\.console\.enabled\s*=\s*true`, `server\.error\.include-(stacktrace\|message)=always` |
| AP-13 | acesso a relacionamento lazy ou chamada de repositório dentro de `for`/`forEach`/`stream().map`; `findAll\(\)` seguido de `stream\(\)\.filter`; `.size\(\)` em coleção para contar; `FetchType\.EAGER` generalizado |
| AP-15 | `@RequestBody` sem `@Valid`; `Integer\.parseInt\(\|Long\.parseLong\(` sobre parâmetros sem tratamento; entidade usada como corpo de entrada |
| AP-16 | `catch\s*\(\s*(Exception\|Throwable\|RuntimeException)\s+\w+\s*\)\s*\{\s*\}`, `\.printStackTrace\(\)`, try/catch em cada endpoint devolvendo 500; ausência de `@ControllerAdvice`/`ExceptionMapper` |
| AP-17 | `new Thread\(`, `CompletableFuture` sem `exceptionally`/`handle`/`join`, `@Async` com retorno `void` que engole erros, `.block\(\)` em código WebFlux |
| AP-22 | `System\.(out\|err)\.print` |

## 4. APIs deprecated

| Deprecated / removido | Moderno |
|---|---|
| Spring Security: `WebSecurityConfigurerAdapter` (deprecated 5.7, removido 6.0) | bean `SecurityFilterChain` |
| Spring Security 6: `antMatchers`/`mvcMatchers` (removidos), `authorizeRequests` (deprecated) | `requestMatchers`, `authorizeHttpRequests` |
| Spring Boot 3 / Jakarta EE 9+: pacotes `javax.persistence`, `javax.servlet`, `javax.validation` | `jakarta.*` |
| Spring Data JPA: `getOne` (deprecated 2.5), `getById` (deprecated 2.7) | `getReferenceById` / `findById` |
| Spring 6.1: `RestTemplate` em modo manutenção | `RestClient` (síncrono) / `WebClient` |
| Spring Boot 3.4: `@MockBean`/`@SpyBean` | `@MockitoBean`/`@MockitoSpyBean` |
| `java.util.Date`, `Calendar`, `SimpleDateFormat` | `java.time.*` (`Instant`, `LocalDateTime`, `DateTimeFormatter`) |
| Construtores de wrappers `new Integer(..)` etc. (deprecated for removal 16) | `Integer.valueOf(..)` / autoboxing |
| `Class.newInstance()` (deprecated 9) | `getDeclaredConstructor().newInstance()` |
| `Object.finalize()` (deprecated for removal 18) | `try-with-resources` / `java.lang.ref.Cleaner` |
| Construtores `new URL(String)` (deprecated 20) | `URI.create(..).toURL()` |
| `Thread.stop/suspend/resume` | interrupção cooperativa / `ExecutorService` |

## 5. Idiomas

| P | Mecanismo |
|---|---|
| P-01 | `application.yml`/`.properties` com placeholders `${VAR:default-dev}` + classe `@ConfigurationProperties` (ou `@Value` centralizado); segredos só por variável de ambiente. Documente as variáveis num `.env.example` (útil com `docker-compose`) ou seção do README — siga o que o projeto já usa |
| P-02 | JDBC `PreparedStatement` com `?`; `JdbcTemplate` com args; `NamedParameterJdbcTemplate` com `:nome`; JPQL/HQL com `:param` + `setParameter`; Spring Data: métodos derivados ou `@Query` com `:param`; ordenação dinâmica via `Sort` com allowlist |
| P-05 | `@RestControllerAdvice` + `@ExceptionHandler`; exceções de domínio estendendo `RuntimeException` com status; `server.error.include-message/stacktrace=never`. Só use `ProblemDetail` se preservar o formato de erro original. JAX-RS: `ExceptionMapper` |
| P-06 | Spring Security Crypto: `PasswordEncoderFactories.createDelegatingPasswordEncoder()` (BCrypt por padrão, aceita prefixos legados, `upgradeEncoding` para rehash); sem Spring Security, `spring-security-crypto` ou jBCrypt (dependência leve). Respostas via DTO/`record` sem senha ou `@JsonIgnore` |
| P-07 | Com Spring Security: `SecurityFilterChain` com `hasRole("ADMIN")` + flag; sem: `OncePerRequestFilter`/`HandlerInterceptor` checando flag + token comparado com `MessageDigest.isEqual` |
| P-08 | `JOIN FETCH`, `@EntityGraph`, `@BatchSize`, projeções/consultas agregadas, métodos `countBy...` |
| P-09 | `@Transactional` em método **público** de `@Service` chamado de fora da classe; `TransactionTemplate`; JDBC puro: `setAutoCommit(false)` + `commit`/`rollback` em `try`/`catch` |
| P-10 | `CompletableFuture` compostos com tratamento de erro; `ExecutorService` gerenciado (ou `@Async` com executor configurado); threads virtuais (Java 21+) se o projeto já estiver nessa versão; WebFlux sem `.block()` |
| P-11 | Bean Validation (`jakarta.validation`): DTOs com `@NotNull`, `@Size`, `@Pattern`... + `@Valid` no controller; grupos de validação para create vs. update |
| P-13 | SLF4J `LoggerFactory.getLogger(X.class)` (ou `@Slf4j` se Lombok já existir); constantes em `final class` ou `enum` |
| P-14 | Injeção por construtor (campos `final`), `@Configuration` + `@Bean` para objetos de infraestrutura; sem estado mutável em beans singleton. Sem framework de DI: composição manual no `main` |

## 6. Estrutura alvo

Spring (e frameworks análogos) já impõem a convenção **controller → service → repository**. Mapeamento das camadas do `mvc-guidelines.md`:

| Camada alvo | Spring | JAX-RS / Quarkus / Micronaut |
|---|---|---|
| Views/Routes + Controller | `@RestController` **fino** (entrada → service → `ResponseEntity`) | resource `@Path` fino |
| Services (regras/fluxo) | `@Service` | bean `@ApplicationScoped`/`@Singleton` |
| Models | `@Entity` + `Repository` (Spring Data) ou DAO com `JdbcTemplate` | entidade + repositório/Panache |
| DTOs | `record`s de request/response | idem |
| Middlewares | `Filter`/`HandlerInterceptor`, `@RestControllerAdvice`, `SecurityFilterChain` | `ContainerRequestFilter`, `ExceptionMapper` |
| Config | `@Configuration`, `@ConfigurationProperties` | `@ConfigProperty` / `@ConfigurationProperties` |

Pacotes sob o pacote raiz existente: por camada (`controller`, `service`, `repository`, `model`/`entity`, `dto`, `config`, `exception`, `security`) ou por funcionalidade — siga o que o projeto já usa. A classe `main` continua no pacote raiz.

## 7. Armadilhas

- Component scan só enxerga subpacotes da classe `@SpringBootApplication` — não mova classes para fora dela.
- Mover classe = mudar a declaração `package` e todos os imports; o compilador acusa, então compile a cada passo.
- `@Transactional` não funciona em métodos privados nem em autochamada (proxy).
- Trocar entidade por DTO na resposta precisa manter **os mesmos nomes de campo JSON** (Jackson usa nomes de getters/campos; use `@JsonProperty` se necessário) e evitar `LazyInitializationException`/recursão infinita em relacionamentos bidirecionais.
- `spring-boot:run`/`bootRun` iniciam a app num processo filho do Maven/Gradle — derrube pelo processo que escuta na porta.
- Boot lento: aumente o `--timeout` do `wait`.
