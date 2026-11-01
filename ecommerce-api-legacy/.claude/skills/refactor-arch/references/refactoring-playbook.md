# Playbook de Refatoração (Fase 3)

Procedimentos de transformação, descritos de forma **independente de linguagem**: estado antes, estado depois, passos e cuidados. Para cada padrão, o mecanismo concreto da stack (qual API de hash, como declarar transação, como registrar o error handler...) está na seção **"Idiomas"** do guia `references/stacks/<stack>.md`, indexada pelos mesmos IDs `P-xx`. Sem guia para a stack, use o mecanismo idiomático que você conhece — nunca o de outra stack.

Regra geral: prefira o que **já existe** no projeto (libs de validação, auth, logging, helpers) antes de introduzir algo novo.

## Sumário

| ID | Padrão | Corrige |
|---|---|---|
| P-01 | Extrair configuração e segredos para variáveis de ambiente | AP-01, AP-12 |
| P-02 | Queries parametrizadas | AP-02 |
| P-03 | Decompor God Class/Module em camadas | AP-03 |
| P-04 | Afinar a rota: lógica → controller/service, dados → model | AP-07, AP-08 |
| P-05 | Error handler centralizado + erros de domínio | AP-16, AP-06 |
| P-06 | Hash forte de senha + serialização segura | AP-05, AP-06 |
| P-07 | Proteger endpoints perigosos (flag + auth) | AP-04 |
| P-08 | Eliminar N+1 (JOIN/IN/eager loading/agregação no banco) | AP-13 |
| P-09 | Transações em escritas multi-etapa | AP-11 |
| P-10 | Fluxo assíncrono estruturado | AP-17 |
| P-11 | Centralizar validação e eliminar duplicação | AP-14, AP-15 |
| P-12 | Substituir APIs deprecated | AP-18 |
| P-13 | Constantes nomeadas, nomes claros e logger | AP-19, AP-20, AP-22 |
| P-14 | Composition root + injeção de dependência + fim do estado global | AP-09, AP-10 |
| P-15 | Remover código morto | AP-21 |

Ordem recomendada de aplicação: P-01 → P-14 → P-03 → P-02/P-06/P-09 (models) → P-04/P-11 (controllers) → P-07/P-05 (middlewares) → P-08/P-10/P-12 → P-13/P-15.

---

## P-01 — Extrair configuração e segredos para variáveis de ambiente

**Antes:** segredos, caminho/URL do banco, modo debug, host, porta e origens CORS escritos como literais no código ou em arquivo de config versionado.

**Depois:**
- Um único módulo/objeto de configuração lê cada valor de uma variável de ambiente, com default **seguro e só para desenvolvimento** (debug desligado, bind local, admin desabilitado, segredo vazio ou de dev).
- O resto do código recebe a config (injeção) ou a importa desse módulo — ninguém mais lê o ambiente.
- Um arquivo de exemplo documenta cada variável, sem valores reais, no formato idiomático da stack.

**Passos:**
1. Liste todos os literais de configuração encontrados nos achados AP-01/AP-12.
2. Crie o módulo de config (ou use o mecanismo de configuração do framework, com placeholders de ambiente).
3. Substitua cada literal pela leitura da config.
4. Crie/atualize o arquivo de exemplo e garanta que o arquivo com valores reais está ignorado no versionamento.

**Cuidados:** nunca reutilize como default o valor real antigo — ele está comprometido. Se a app depende do valor para funcionar localmente sem configuração (porta, caminho do banco), mantenha o mesmo default para não quebrar o start. Carregar arquivo `.env` via biblioteca é opcional — só use se a dependência já existir ou o framework já fizer isso.

---

## P-02 — Queries parametrizadas

**Antes:** a consulta é montada concatenando/interpolando valores externos na string SQL (ou no filtro NoSQL/comando).

**Depois:** a string da consulta é **constante**; os valores vão como **parâmetros** separados para o driver/ORM, usando o placeholder que ele suporta (posicional ou nomeado — ver guia da stack).

**Passos:**
1. Para cada consulta do achado, troque cada valor interpolado por um placeholder e passe o valor na lista/mapa de parâmetros.
2. Padrões com curinga (`LIKE`): o curinga vai no **valor** do parâmetro, não na string SQL.
3. Listas variáveis (`IN`): gere um placeholder por item ou use o recurso de expansão do driver/ORM.
4. Filtros opcionais: construa a lista de condições e a lista de parâmetros em paralelo.

**Cuidados:** nomes de colunas, tabelas e direção de ordenação **não** podem ser parametrizados — valide contra uma **allowlist** e rejeite (400) o resto. Preferir a API de consulta do ORM, quando o projeto já usa um, também resolve.

---

## P-03 — Decompor God Class/Module em camadas

**Antes:** uma classe/arquivo cria conexão, schema e seed, declara rotas, aplica regras de vários domínios e formata respostas.

**Depois:** uma responsabilidade por arquivo, por domínio:
- módulo de banco → conexão/pool, schema, seed (chamados pelo composition root);
- um model/repositório por entidade → todas as consultas daquela entidade;
- services → fluxos que envolvem várias entidades ou integrações (pagamento, notificação);
- controllers → fluxo de cada caso de uso;
- routes → mesmas URLs e métodos de antes, delegando ao controller;
- composition root → monta banco, models, services, controllers, rotas e error handler.

**Procedimento:**
1. Liste cada função/método do God Module e classifique: dado / regra / rota / config / util.
2. Crie os arquivos-destino por domínio e camada; mova o código **sem alterar comportamento** primeiro.
3. Ajuste imports/registro e o composition root; compile/suba a app para confirmar que nada quebrou.
4. Só então aplique as demais correções (P-02, P-06, ...) nos arquivos novos.
5. Apague o arquivo original quando estiver vazio (ou deixe-o como ponte de entry point, se for o arquivo de start).

---

## P-04 — Afinar a rota: lógica → controller/service, dados → model

**Antes:** o handler da rota lê o body, abre conexão, consulta o banco, valida, aplica regras (ex.: devolver estoque ao cancelar), grava, imprime uma "notificação" e monta a resposta.

**Depois:**
- **Rota:** uma linha de delegação — passa os parâmetros do caminho e o body ao controller e devolve o resultado.
- **Controller:** valida a entrada (P-11), busca a entidade via model, lança erro de domínio se não existe ou se a entrada é inválida, chama o model/service que executa a operação, dispara efeitos (notificação) via service, devolve resultado + status **idênticos** aos originais.
- **Model:** um método por operação de dados (`buscar por id`, `mudar status com reposição de estoque`), executando escritas relacionadas dentro de uma transação (P-09).

**Cuidados:** se o projeto já tem helpers/serviços com a lógica (um serviço de notificação ou de validação não usado), **use-os** em vez de reescrever. A resposta HTTP final é idêntica à original.

---

## P-05 — Error handler centralizado + erros de domínio

**Antes:** cada handler captura exceções genéricas e devolve a mensagem da exceção com status 500; formatos de erro variam entre rotas; alguns caminhos de erro não respondem.

**Depois:**
- **Erros de domínio:** uma hierarquia pequena (base com mensagem + status + detalhes opcionais; subtipos para validação → 400, não encontrado → 404, proibido → 403, conflito → 409).
- **Handler global** registrado pelo mecanismo do framework (ver guia da stack): converte erro de domínio em `{<chave de erro original>: mensagem}` + status; converte rota inexistente em 404 no mesmo formato; para qualquer outra exceção, **loga com stack no servidor** e responde 500 com mensagem genérica.
- Handlers e controllers não capturam exceções só para formatar resposta — lançam erros de domínio e deixam propagar.

**Cuidados:** preserve a chave de erro que o projeto já usava e os status de erro originais quando faziam sentido. Nunca devolva mensagem de exceção, stack ou SQL ao cliente. Em stacks onde erros assíncronos não chegam ao handler global automaticamente, use o mecanismo de encaminhamento indicado no guia.

---

## P-06 — Hash forte de senha + serialização segura

**Antes:** senha gravada em texto puro, com hash rápido (MD5/SHA) ou codificação reversível; comparação direta de strings; entidade serializada inteira (com senha/hash); dados de cartão e segredos em logs.

**Depois:**
- **Hash:** algoritmo lento e com salt (bcrypt, scrypt, Argon2 ou PBKDF2) — preferencialmente o que a stack/framework já oferece nativamente (ver guia). Funções `hash(senha)` e `verify(senha, armazenado)` em um único helper; a verificação usa a função da lib (tempo constante).
- **Compatibilidade com dados legados:** `verify` reconhece o formato do hash forte; se o valor armazenado está no formato antigo, valida pelo método antigo e, se passar, regrava com o hash forte (rehash no login).
- **Serialização:** a representação pública da entidade lista campos explicitamente e nunca inclui senha/hash/tokens. Consultas que vão para a resposta selecionam colunas explícitas.
- **Logs:** dados de cartão mascarados (só os 4 últimos dígitos); chaves e senhas nunca logadas.

**Cuidados:**
- Senha padrão quando o usuário não informa → passe a exigir senha (400). Se isso quebrar um fluxo do contrato que hoje funciona sem senha, gere uma senha aleatória e registre como mudança de comportamento.
- Seeds com senha em texto puro devem gravar hash.
- Dados já persistidos em formato inseguro: use rehash no login e registre a migração em "Manual Follow-ups".

---

## P-07 — Proteger endpoints perigosos (flag + auth)

**Antes:** rota que executa SQL arbitrário, reseta o banco ou faz operação administrativa, aberta a qualquer um.

**Depois:**
- A rota **continua existindo** (contrato), protegida por um middleware/filtro/guard `admin`:
  1. se a flag de config `ENABLE_ADMIN_ROUTES` está desligada (default) → `403` no formato de erro padrão;
  2. se ligada, exige credencial: o mecanismo de auth real do projeto, se houver; senão, um token de admin vindo da config, comparado em tempo constante → `403` se ausente/errado.
- Execução de SQL arbitrário: além da proteção, restrinja a leitura (`SELECT`) ou remova a capacidade e documente.
- Campos de privilégio (papel, flag de admin) não são aceitos do body em cadastro público — ignore-os ou exija admin.

**Cuidados:** registre cada rota afetada em "Behavior Changes". No smoke test, a rota deve responder `403` com a flag desligada.

---

## P-08 — Eliminar N+1

**Antes:** busca a lista e, dentro do loop, faz uma consulta por item (e às vezes outra por sub-item); ou carrega todas as linhas para contar/filtrar em memória.

**Depois (uma das opções, na ordem de preferência):**
1. **Uma consulta com JOIN** trazendo pai + filhos, agrupando em memória por id do pai (preservando a ordem original).
2. **Duas consultas**: a lista + uma consulta `IN (ids)` para os filhos, montando um mapa id → filhos.
3. **Eager loading** do ORM para os relacionamentos usados no loop.
4. **Agregação no banco** (`COUNT`, `SUM`, `GROUP BY`) em vez de carregar coleções para contar ou somar.

**Cuidados:** o JSON de saída deve ser idêntico (mesmas chaves, mesma ordem de itens, mesmo tratamento de pais sem filhos). Paginação só se puder ser **opcional** (parâmetros com default que devolve o mesmo resultado de antes).

---

## P-09 — Transações em escritas multi-etapa

**Antes:** várias escritas relacionadas (cabeçalho + itens + baixa de estoque; usuário + matrícula + pagamento) executadas em sequência, sem transação, às vezes com commit no meio ou dentro do loop.

**Depois:**
- Um helper/mecanismo de transação único na camada de dados (bloco, função de ordem superior ou anotação — ver guia da stack): inicia, executa, faz commit no sucesso e rollback em qualquer erro, relançando o erro.
- O método do model que implementa o caso de uso executa **todas** as escritas relacionadas dentro de uma transação.
- Verificações de concorrência entram na própria escrita quando possível (ex.: decrementar estoque só se houver saldo e checar linhas afetadas; se zero, lançar erro de validação → rollback).
- Deleções com dependentes: apague/cascateie os filhos na mesma transação.

---

## P-10 — Fluxo assíncrono estruturado

**Antes:** callbacks aninhados, contadores manuais de pendências, erros que não chegam à resposta, operações assíncronas disparadas sem aguardar, I/O bloqueante em servidor assíncrono.

**Depois:**
- Use o modelo assíncrono **moderno da linguagem** (async/await, futures compostos, goroutines com sincronização, etc. — ver guia). Drivers só com API de callback ganham um adaptador fino na camada de dados.
- Fluxo sequencial: passos aguardados em ordem, dentro de uma transação quando há escritas (P-09); erros propagam até o handler global (P-05).
- Contadores manuais → primitiva de "aguardar todos" da linguagem, preservando a ordem dos resultados. Melhor ainda: substituir o loop por uma única consulta (P-08).
- I/O bloqueante em handler assíncrono → a versão não bloqueante da API.

---

## P-11 — Centralizar validação e eliminar duplicação

**Antes:** create e update validam de formas diferentes (update mais fraco); listas de valores válidos repetidas; conversões que estouram em 500; conversão registro→representação copiada em vários lugares.

**Depois:**
- **Um validador por entidade/caso de uso** (no mecanismo da stack: schema, DTO anotado ou função pura — prefira a lib que o projeto já usa), com modo **parcial** para update: valida apenas os campos presentes, com as mesmas regras do create.
- O validador checa body ausente/não-objeto, presença, tipo, formato, faixa e valores permitidos; acumula erros por campo e lança **um** erro de validação (→ 400) com os detalhes.
- Listas de valores válidos viram constantes únicas (P-13).
- Conversão registro→representação vira **uma** função/método reutilizada; métodos que já existiam no model são reaproveitados em vez das cópias.

**Cuidados:** mantenha as **mensagens de erro e status** originais quando o cliente pode depender delas.

---

## P-12 — Substituir APIs deprecated

**Procedimento:**
1. Para cada achado AP-18, confirme que a alternativa moderna existe **na versão fixada** da linguagem/lib (guia da stack + manifesto).
2. Se existe, substitua todas as ocorrências — centralize num helper quando a API é usada em vários lugares (ex.: geração de timestamps), para não misturar comportamentos antigo e novo.
3. Se a alternativa exige upgrade de versão, **não** altere o manifesto: registre o upgrade como "Manual Follow-up".
4. Depois do boot, confirme que os avisos de depreciação correspondentes sumiram do log de build/execução.

**Cuidados:** atenção a mudanças sutis de semântica (ex.: datas sem fuso vs. com fuso) — normalize num único ponto e preserve o formato serializado no JSON.

---

## P-13 — Constantes nomeadas, nomes claros e logger

**Depois:**
- **Constantes:** limites, taxas, status e papéis viram constantes/enums nomeados num único módulo (ou no próprio domínio a que pertencem).
- **Nomes:** identificadores internos crípticos ganham nomes descritivos na convenção da linguagem; campos do JSON (contrato) mantêm os nomes originais — mapeie-os na fronteira.
- **Logger:** escrita na saída padrão vira o logger idiomático da stack (com nível), configurado uma vez no composition root com nível vindo da config.
- "Envios" simulados de email/SMS no meio da regra viram chamadas a um service de notificação que usa o logger.

---

## P-14 — Composition root + injeção de dependência + fim do estado global

**Antes:** conexão global criada no carregamento do módulo; caches/contadores em variáveis globais ou estáticas; rotas registradas como efeito colateral de import; serviços instanciados dentro dos métodos que os usam.

**Depois:**
- **Composition root:** uma função/fábrica (ou o container de DI do framework) cria a app a partir da config, inicializa o banco (pool ou conexão por requisição/escopo, conforme a stack), instancia models → services → controllers passando as dependências, registra rotas, middlewares e o error handler. Retorna a app; o entry point só a inicia.
- **Conexões:** gerenciadas por escopo (pool do driver, sessão por requisição, ciclo de vida do container) — nunca uma conexão global compartilhada sem controle de concorrência.
- **Estado:** caches realmente necessários viram um objeto injetado com interface explícita; os demais globais mutáveis são removidos.

**Cuidados:** caches/contadores globais escritos e nunca lidos → remova (P-15). Um banco em memória pode continuar como default se era o comportamento original, mas o endereço vem da config.

---

## P-15 — Remover código morto

**Procedimento:**
1. Para cada símbolo candidato, confirme com busca que não há referências — incluindo referências dinâmicas (reflexão, registro por nome/string, carregamento dinâmico de módulos, injeção por convenção, arquivos de config que apontam para classes).
2. Remova funções, variáveis, imports, módulos não usados e blocos de código comentado.

**Exceção importante:** helpers/serviços mortos que implementam algo que **deveria** acontecer (ex.: notificação ao concluir uma operação, validação de formato) não são apagados — são **reconectados** no controller/service correto (P-04). Decida pelo que o domínio exige e registre a decisão no resumo.
