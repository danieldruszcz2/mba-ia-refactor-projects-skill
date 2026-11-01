# Catálogo de Anti-Patterns (Fase 2)

Cada entrada tem: **o que é**, **sinais de detecção**, **severidade** e o **padrão do playbook** que corrige.

Os sinais são descritos em termos de conceitos, válidos para qualquer linguagem. Para transformá-los em buscas concretas use:
- os **padrões genéricos** marcados com 🔎 neste arquivo (independem de linguagem);
- a seção **"Padrões de busca"** do guia da stack detectada (`references/stacks/<stack>.md`), indexada pelos mesmos IDs `AP-xx`.

Busca textual é ponto de partida: sempre confirme lendo o trecho para descartar falsos positivos (ex.: a palavra "password" num comentário) e para achar casos estruturais que grep não pega.

## Escala de severidade

| Severidade | Critério |
|---|---|
| **CRITICAL** | Falha grave de segurança ou arquitetura: expõe dados sensíveis, permite ataque direto (injeção, credencial exposta, endpoint destrutivo aberto) ou viola completamente a separação de responsabilidades (God Class com banco + regras + rotas). |
| **HIGH** | Violação forte de MVC/SOLID que dificulta muito manutenção e testes: regra de negócio no controller/rota, acoplamento sem injeção de dependência, estado global mutável, escrita multi-etapa sem transação. |
| **MEDIUM** | Padronização, duplicação, performance moderada: N+1, validação ausente, tratamento de erro inconsistente, APIs deprecated, fluxo assíncrono frágil. |
| **LOW** | Legibilidade: nomes ruins, magic numbers, código morto, saída padrão como log. |

**Ajuste de contexto:** suba ou desça **um** nível quando o contexto justificar e diga o porquê no relatório. Ex.: uma API deprecated que já foi *removida* na versão em uso (quebra o build/boot) sobe para HIGH; um segredo apenas num script de seed local pode descer para HIGH.

## Índice

| ID | Anti-pattern | Severidade | Playbook |
|---|---|---|---|
| AP-01 | Credenciais e segredos hardcoded | CRITICAL | P-01 |
| AP-02 | Injeção (SQL/NoSQL/comando) por concatenação | CRITICAL | P-02 |
| AP-03 | God Class / God Module | CRITICAL | P-03 |
| AP-04 | Endpoint perigoso ou administrativo sem proteção | CRITICAL | P-07 |
| AP-05 | Armazenamento inseguro de senhas | CRITICAL | P-06 |
| AP-06 | Exposição de dados sensíveis (respostas e logs) | CRITICAL | P-06 |
| AP-07 | Lógica de negócio no controller/rota (Fat Controller) | HIGH | P-04 |
| AP-08 | Acesso a dados fora da camada Model | HIGH | P-04 |
| AP-09 | Estado global mutável / conexão compartilhada | HIGH | P-14 |
| AP-10 | Acoplamento forte sem injeção de dependência | HIGH | P-14 |
| AP-11 | Escrita multi-etapa sem transação | HIGH | P-09 |
| AP-12 | Configuração insegura de execução (debug, CORS, bind) | HIGH | P-01 |
| AP-13 | Queries N+1 e carga desnecessária | MEDIUM | P-08 |
| AP-14 | Código e validação duplicados | MEDIUM | P-11 |
| AP-15 | Validação de entrada ausente ou fraca | MEDIUM | P-11 |
| AP-16 | Tratamento de erro descentralizado / vazamento de erro interno | MEDIUM | P-05 |
| AP-17 | Fluxo assíncrono frágil (callback hell, promessas/tarefas sem tratamento) | MEDIUM | P-10 |
| AP-18 | Uso de APIs deprecated | MEDIUM | P-12 |
| AP-19 | Magic numbers e strings | LOW | P-13 |
| AP-20 | Nomenclatura ruim | LOW | P-13 |
| AP-21 | Código morto (funções, módulos, variáveis não usados) | LOW | P-15 |
| AP-22 | Saída padrão como mecanismo de log | LOW | P-13 |

---

## CRITICAL

### AP-01 — Credenciais e segredos hardcoded
Segredos (chaves de API, chaves de assinatura de sessão/token, senhas de banco ou de serviços externos, tokens de gateway) escritos no código-fonte ou em arquivos de configuração versionados. Qualquer pessoa com acesso ao repositório os obtém; não dá para rotacionar sem deploy.

**Sinais:**
- 🔎 Atribuição de literal a nome sensível (case-insensitive): `(secret|password|passwd|pwd|api[_-]?key|token|private[_-]?key|access[_-]?key|client[_-]?secret)\s*[:=]\s*['"][^'"]{3,}['"]`
- 🔎 Prefixos de chaves reais: `sk_live_|pk_live_|sk_test_|AKIA[0-9A-Z]{16}|ghp_|xox[bp]-|AIza|-----BEGIN (RSA |EC )?PRIVATE KEY`
- 🔎 Strings de conexão com senha embutida: `://[^:/\s]+:[^@\s]+@`
- Arquivos de configuração versionados (propriedades, YAML, JSON, `.env` commitado) com valores reais em chaves sensíveis.
- Estrutural: segredo devolvido por endpoint (ex.: health/status retornando a config) → registre também em AP-06.

**Severidade:** CRITICAL. Pode descer para HIGH se for claramente um valor de desenvolvimento usado só em seed/teste local.
**Correção:** P-01.

### AP-02 — Injeção (SQL/NoSQL/comando)
Consultas ou comandos montados concatenando/interpolando entrada externa. Permite ler, alterar ou apagar o banco, burlar login ou executar comandos no servidor.

**Sinais:**
- 🔎 Palavra-chave SQL dentro de string que é concatenada/interpolada: `(SELECT|INSERT|UPDATE|DELETE|WHERE|ORDER BY)[^;\n]*['"\x60]\s*(\+|\.|%|\$\{|\{|#\{)` e o inverso (variável concatenada antes do fechamento da string).
- Strings SQL construídas por formatação/interpolação de strings e então passadas ao driver/ORM (método de execução de SQL cru, query nativa, consulta textual do ORM).
- Filtros NoSQL montados a partir de objetos/strings vindos direto do body (operadores injetáveis, avaliação de expressão).
- Execução de processos/shell com argumentos concatenados a partir da entrada.
- Estrutural: o projeto usa placeholders/parâmetros em um lugar e concatenação em outro — o contraste é evidência forte.

**Severidade:** CRITICAL sempre que um valor externo (body, query, params, headers, cookies) chega à string.
**Correção:** P-02.

### AP-03 — God Class / God Module
Uma classe ou arquivo concentra responsabilidades de várias camadas e/ou vários domínios: conexão com banco, criação de schema/seed, rotas, regras de negócio, formatação.

**Sinais estruturais (leitura):**
- Um arquivo com > ~200–300 linhas misturando: definição de rotas + acesso a dados + regras + config.
- Uma classe cujo construtor/inicialização cria conexão, cria tabelas, popula dados e registra rotas.
- Um módulo de dados que contém CRUD de 3+ entidades diferentes junto com regras de negócio, notificações e relatórios.
- Funções/métodos com > ~50 linhas fazendo validação + persistência + efeitos colaterais (God Method).
- Auxiliar: contar funções/métodos por arquivo; arquivos que importam ao mesmo tempo o framework HTTP **e** o driver/ORM de banco.

**Severidade:** CRITICAL quando mistura rotas + banco + regras; HIGH quando é um único domínio grande mas ainda em uma camada.
**Correção:** P-03.

### AP-04 — Endpoint perigoso ou administrativo sem proteção
Rotas que executam SQL/comandos arbitrários, resetam/derrubam o banco, apagam usuários, expõem relatórios financeiros ou mudam papéis sem autenticação/autorização.

**Sinais:**
- 🔎 Caminhos: `/admin|/debug|/reset|/query|/exec|/drop|/seed|/internal|/financial|/console`
- 🔎 Operações: `DROP TABLE|TRUNCATE|DELETE FROM \w+\s*['"\x60;)]` (sem WHERE); execução dinâmica de código/SQL recebido na requisição.
- Ausência do mecanismo de auth do projeto (decorator, anotação, middleware, filtro, guard) em rotas de escrita/admin enquanto outras rotas o usam — ou ausência total de auth.
- Campo de privilégio (papel, flag de admin) aceito diretamente do body em criação/edição de usuário (escalada de privilégio).
- Token falso ou previsível (literal fixo, derivado do id, sem assinatura).

**Severidade:** CRITICAL.
**Correção:** P-07.

### AP-05 — Armazenamento inseguro de senhas
Senhas em texto puro, hash rápido sem salt (MD5, SHA-1, SHA-256 simples), "criptografia" caseira/reversível (base64, XOR, truncar string), senha padrão quando o usuário não informa.

**Sinais:**
- 🔎 Algoritmos rápidos perto de senha: `(md5|sha1|sha-?1|sha256|sha-?256)` na mesma linha/função que `pass|senha|pwd`.
- 🔎 Codificação reversível aplicada a senha: `base64` na mesma função que `pass|senha|pwd`.
- Insert/update de usuário gravando o valor da senha recebido do body sem passar por função de hash.
- Comparação de igualdade direta entre a senha recebida e a armazenada (sem função de verificação de hash, sem comparação em tempo constante).
- Default de senha quando o campo está ausente.

**Severidade:** CRITICAL.
**Correção:** P-06.

### AP-06 — Exposição de dados sensíveis
Senha/hash, tokens, segredos, número de cartão, documentos pessoais, stack traces, caminhos internos ou flags de debug devolvidos em respostas HTTP ou escritos em logs.

**Sinais:**
- Serialização de entidade inteira (método genérico de conversão para dict/JSON, `SELECT *` devolvido direto) incluindo colunas sensíveis.
- 🔎 Logs com dado sensível: chamada de log/print na mesma linha que `card|cartao|cvv|password|senha|token|secret|key`.
- Respostas contendo a mensagem/stack da exceção (ver também AP-16).
- Endpoints de health/status retornando config, segredos, caminho do banco, modo debug.

**Severidade:** CRITICAL para senhas/cartões/segredos; HIGH para metadados internos.
**Correção:** P-06 (serialização segura) + P-05 (erros).

---

## HIGH

### AP-07 — Lógica de negócio no controller/rota (Fat Controller)
O handler da rota valida, calcula, aplica regras (descontos, status, estoque, permissões), dispara notificações e monta a resposta. Impossível reutilizar/testar sem HTTP.

**Sinais:**
- Handlers de rota com > ~30 linhas, cadeias de condicionais de regra de negócio, cálculos, loops sobre resultados de banco.
- Rotas que montam representações de entidades à mão em vez de usar o model.
- Helpers/serviços existentes que **não são usados** enquanto a rota reimplementa a mesma lógica.

**Severidade:** HIGH.
**Correção:** P-04.

### AP-08 — Acesso a dados fora da camada Model
Rotas/controllers executam SQL ou chamam o ORM/driver diretamente, ou abrem conexões por conta própria.

**Sinais:** imports de driver/ORM/conexão em arquivos de rota/controller; chamadas de execução de consulta ou de sessão/contexto do ORM fora da camada de dados (padrões no guia da stack).

**Severidade:** HIGH.
**Correção:** P-04 (mover para model/repositório).

### AP-09 — Estado global mutável / conexão compartilhada
Variáveis de módulo/estáticas mutáveis usadas como cache, contador ou sessão; uma única conexão de banco global compartilhada por todas as requisições sem pool nem controle de concorrência; singletons que guardam estado de requisição.

**Sinais:** declarações mutáveis no escopo de módulo/classe (coleções vazias, contadores, `null`) escritas por handlers; campos estáticos não-finais/não-constantes; desativação explícita de checagens de thread-safety do driver; objeto exportado/registrado como singleton com estado de requisição.

**Severidade:** HIGH (race conditions, vazamento entre requisições, testes não isolados).
**Correção:** P-14.

### AP-10 — Acoplamento forte sem injeção de dependência
Dependências criadas dentro das funções/classes que as usam (instanciar banco, cliente HTTP ou serviço dentro do método/construtor), módulo global importado e usado em toda parte, efeitos colaterais no import/carregamento (conectar banco, criar tabelas), ausência de composition root, ou contorno do container de DI que o framework já oferece.

**Sinais:** instanciação de classes `*Service|*Repository|*Client|*Database|*Manager` dentro de métodos de negócio; conexão aberta no topo do módulo; app criada como efeito de import sem função de fábrica; classe que é ao mesmo tempo servidor, repositório e serviço; lookup estático/service locator onde o framework tem injeção.

**Severidade:** HIGH.
**Correção:** P-14.

### AP-11 — Escrita multi-etapa sem transação
Fluxos que gravam em várias tabelas ou vários registros dependentes sem transação; falha no meio deixa dados pela metade. Inclui deleções que deixam órfãos (sem cascade nem limpeza).

**Sinais:** sequência de 2+ operações de escrita na mesma função/caso de uso sem bloco/anotação de transação; commit dentro de loop; escritas encadeadas em callbacks/futures sem rollback; mensagens de log/erro admitindo dados parciais.

**Severidade:** HIGH.
**Correção:** P-09.

### AP-12 — Configuração insegura de execução
Modo debug ligado fixo no código, bind em todas as interfaces fixo, CORS liberando qualquer origem com credenciais, cookies sem flags de segurança, porta fixa no código, endpoints de diagnóstico do framework expostos sem proteção.

**Sinais:** 🔎 `debug\s*[:=]\s*(true|True|1)`; 🔎 `0\.0\.0\.0`; 🔎 origem CORS `\*`; flags de cookie seguro desligadas; padrões específicos no guia da stack.

**Severidade:** HIGH (alguns modos debug permitem execução remota de código). MEDIUM se só CORS aberto.
**Correção:** P-01.

---

## MEDIUM

### AP-13 — Queries N+1 e carga desnecessária
Uma query para a lista e mais uma (ou várias) por item; carregar todas as linhas para contar/filtrar em memória; listagens sem paginação; relacionamentos carregados preguiçosamente dentro de loops.

**Sinais:** chamada de consulta/repositório **dentro** de um loop/iteração sobre resultados; carregar coleção inteira para obter seu tamanho; filtro em memória após buscar tudo; várias contagens separadas que caberiam numa agregação (`GROUP BY`); contadores manuais de operações pendentes.

**Severidade:** MEDIUM.
**Correção:** P-08.

### AP-14 — Código e validação duplicados
Mesma lógica copiada em vários lugares (conversão registro→representação, cálculos derivados, validação de criar vs. atualizar, listas de valores válidos), frequentemente com pequenas divergências — o que já é um bug.

**Sinais:** blocos de 5+ linhas quase idênticos; constantes/listas literais repetidas; funções de consulta idênticas exceto pelo filtro; métodos já existentes no model reimplementados em rotas/controllers.

**Severidade:** MEDIUM.
**Correção:** P-11.

### AP-15 — Validação de entrada ausente ou fraca
Body/params usados sem checar presença, tipo, formato e faixa; conversões que lançam exceção (número, data) sem tratamento → `500`; body possivelmente nulo acessado direto; validação mais fraca no update que no create; mecanismo de validação do framework disponível e não usado.

**Sinais:** acesso direto a campos do body/params seguido de uso em lógica ou query sem checagem prévia; conversões de tipo sobre entrada sem tratamento; ausência de schema/DTO validado.

**Severidade:** MEDIUM (HIGH se a falta de validação leva a injeção ou escalada — nesse caso registre também o AP correspondente).
**Correção:** P-11.

### AP-16 — Tratamento de erro descentralizado / vazamento de erro interno
Bloco de captura de exceção copiado em todo handler, captura genérica que engole o erro, mensagem/stack da exceção devolvida ao cliente, formatos de erro inconsistentes entre rotas, caminhos de erro que nunca enviam resposta, stack trace impresso na saída padrão.

**Sinais:** captura genérica com corpo vazio ou só `return`/`pass`; resposta construída com a mensagem da exceção; ausência do mecanismo de tratamento global de erros do framework; padrões específicos no guia da stack.

**Severidade:** MEDIUM (sobe para HIGH se vaza stack trace/SQL).
**Correção:** P-05.

### AP-17 — Fluxo assíncrono frágil
Callbacks aninhados 3+ níveis, contadores manuais para saber quando terminou, erros não propagados, ordem de resultados não determinística; promessas/futures/tarefas sem tratamento de erro ou nunca aguardadas; I/O bloqueante dentro de servidor assíncrono; threads criadas manualmente por requisição sem controle.

**Sinais:** indentação crescente de funções de callback com parâmetro de erro; decremento manual de contador para detectar fim; operação assíncrona disparada sem `await`/join/tratamento; chamadas síncronas bloqueantes em handlers assíncronos.

**Severidade:** MEDIUM.
**Correção:** P-10.

### AP-18 — Uso de APIs deprecated
APIs obsoletas, removidas ou desaconselhadas na versão detectada da linguagem/framework/lib. Geram warnings, quebram em upgrades ou já quebram hoje.

**Como detectar:** compare a versão detectada na Fase 1 com a seção **"APIs deprecated"** do guia da stack (não exaustiva) e com seu conhecimento das libs usadas. Para cada caso, cite a API, a versão em que foi deprecada/removida e a alternativa moderna disponível **na versão em uso**. Avisos de depreciação no log de build/boot também são evidência.

**Severidade:** MEDIUM. Sobe para HIGH se a API já foi **removida** na versão em uso (quebra) ou se é insegura (ex.: primitiva criptográfica sem IV/salt).
**Correção:** P-12.

---

## LOW

### AP-19 — Magic numbers e strings
Números/strings com significado de negócio soltos no código: limites de desconto, tamanhos de página, códigos de status de domínio, strings de status/papéis repetidas, timeouts, portas.

**Sinais:** literais numéricos (exceto 0, 1, -1) em condições/cálculos; strings de status/papéis comparadas em vários lugares.

**Severidade:** LOW.
**Correção:** P-13.

### AP-20 — Nomenclatura ruim
Variáveis/funções/campos crípticos (1–3 letras fora de loops curtos, abreviações não óbvias, sufixos numéricos), nomes que mentem (função chamada de "criptografia" que não criptografa; módulo de "utilitários" que guarda config), mistura de convenções no mesmo escopo.

**Sinais:** identificadores muito curtos fora de escopos triviais; convenções de caixa misturadas na mesma linguagem; nome de função que não descreve o que ela faz.

**Severidade:** LOW. **Atenção:** nomes de campos de **contrato da API** (JSON de entrada/saída) não podem ser renomeados — mapeie-os para nomes claros internamente.
**Correção:** P-13.

### AP-21 — Código morto
Funções, classes, módulos, serviços, variáveis e imports nunca usados; caches escritos e nunca lidos; código comentado em blocos; rotas duplicadas.

**Sinais:** símbolos definidos sem referências (busque pelo nome); imports não usados (avisos do compilador/linter ajudam); módulos de serviços/utilitários nunca importados; variáveis atribuídas e nunca lidas.

**Severidade:** LOW (registre como HIGH/AP-07 se o código morto for a lógica que **deveria** estar sendo usada — ex.: um serviço de notificação ou de validação ignorado).
**Correção:** P-15.

### AP-22 — Saída padrão como mecanismo de log
Logs escritos direto na saída padrão/erro sem nível, timestamp ou estrutura; efeitos de negócio (envio de email/SMS) "simulados" com print no meio da regra; logger do projeto existente e não usado.

**Sinais:** chamadas de impressão na saída padrão em código de aplicação (fora de scripts CLI) — padrões no guia da stack; existência de um logger/helper de log não usado.

**Severidade:** LOW (se logar dados sensíveis, é AP-06 CRITICAL).
**Correção:** P-13.
