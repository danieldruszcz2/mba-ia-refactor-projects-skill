# Guidelines de Arquitetura — Camadas Alvo (Fase 3)

Este é o padrão de **responsabilidades** para onde todo projeto deve convergir, independentemente da stack. Em uma API, a "View" é a camada de **rotas + serialização da resposta** (não há templates) — por isso chamamos a camada de **Views/Routes**.

Os nomes de pastas e mecanismos concretos (como declarar rotas, onde fica a config, como o framework injeta dependências) estão na seção **"Estrutura alvo"** e **"Idiomas"** do guia da stack (`references/stacks/<stack>.md`). O que é obrigatório são as responsabilidades e a regra de dependência; os nomes seguem a convenção da stack.

## Sumário
1. Visão geral e regra de dependência
2. Responsabilidades por camada
3. Camadas de suporte
4. Estrutura de diretórios
5. Projetos parcialmente organizados ou já em camadas
6. Convenções
7. Checklist de conformidade

---

## 1. Visão geral e regra de dependência

```
  HTTP request
       │
       ▼
┌──────────────┐   middlewares (auth, error handler, logging) envolvem tudo
│ Views/Routes │   mapeia método+caminho → controller; nada de regra ou SQL
└──────┬───────┘
       ▼
┌──────────────┐
│ Controllers  │   fluxo da aplicação: extrai/valida entrada, chama models/services,
└──────┬───────┘   decide o status, devolve dados serializáveis
       ▼
┌──────────────┐
│ (Services)   │   opcional: regras de negócio que envolvem várias entidades/efeitos
└──────┬───────┘
       ▼
┌──────────────┐
│   Models     │   entidades + acesso a dados (queries parametrizadas, transações)
└──────┬───────┘
       ▼
    Banco de dados          config é lida por todos; ninguém lê variáveis de ambiente direto
```

**Regra de dependência:** cada camada só conhece a(s) de baixo. Models não importam controllers nem objetos HTTP (requisição, resposta, helpers de serialização HTTP). Controllers não escrevem SQL nem usam o ORM diretamente. Routes não contêm condicionais de regra de negócio. Nenhum módulo além do de configuração lê variáveis de ambiente.

**Composition root:** um único ponto (entry point / app factory / container de DI do framework) cria a app, carrega config, inicializa o banco, registra middlewares e rotas. Dependências são passadas para baixo (injeção), não importadas como globais mutáveis. Se o framework já tem container de DI, use-o — não crie outro.

## 2. Responsabilidades por camada

### Models
**Faz:**
- Define entidades (classe mapeada, schema, struct ou registro) e suas regras intrínsecas (ex.: cálculo derivado de um único registro, verificação de estado).
- Encapsula **todo** acesso a dados: CRUD, consultas específicas, agregações. Pode ser separado em *repository* (acesso a dados) + *entity* (dados) quando a stack tem essa convenção.
- Usa queries parametrizadas, transações para escritas multi-etapa e consultas eficientes (JOIN/IN, agregação no banco, paginação).
- Serializa sem campos sensíveis (a representação pública nunca contém senha/hash).

**Não faz:** ler a requisição, devolver respostas HTTP, decidir status code, enviar email, escrever na saída padrão.

### Views / Routes
**Faz:**
- Declara as rotas (método + caminho) exatamente como no contrato original.
- Aplica middlewares/filtros/guards por rota (auth, rate-limit).
- Encaminha para o controller e converte o retorno em resposta HTTP (JSON + status).

**Não faz:** SQL, regras de negócio, validação complexa, captura de exceção por rota (o error handler central cuida disso).

> Em frameworks onde rota e controller vivem na mesma classe/função anotada, essa unidade cumpre os dois papéis: mantenha-a **fina** (extrai entrada → chama service → devolve resposta) e mova regras para services e dados para repositórios.

### Controllers
**Faz:**
- Concentra o **fluxo da aplicação** para cada caso de uso: extrai dados da requisição, valida (via schema/DTO/validator), chama models/services na ordem certa, trata "não encontrado"/"conflito" lançando erros de domínio, e devolve o resultado + status.
- Pode conter regras de negócio simples do caso de uso. Quando a regra cresce, envolve várias entidades ou efeitos externos (pagamento, notificação), extraia para um **service** e o controller apenas orquestra.

**Não faz:** SQL/ORM direto, montar conexões, conhecer detalhes do framework além do objeto de requisição/resposta, engolir exceções.

## 3. Camadas de suporte

| Camada | Responsabilidade |
|---|---|
| **config** | Lê variáveis de ambiente (e/ou arquivo de config idiomático com placeholders de env), define defaults **seguros** para dev, expõe um objeto/estrutura de configuração. Único lugar que lê o ambiente. Flags típicas: `DEBUG`, `ENABLE_ADMIN_ROUTES`, `CORS_ORIGINS`, `DATABASE_URL`, `SECRET_KEY`, `PORT`. |
| **middlewares** (filtros, interceptors, guards) | Error handler centralizado (formato de erro único), autenticação/autorização, logging de requisição. |
| **services** | Regras de negócio entre entidades e integrações externas (pagamento, email, notificação). Opcional — crie só quando houver lógica que justifique. |
| **utils / helpers** | Funções puras e genéricas (datas, formatação, hashing de senha, validadores reutilizáveis). Nada de estado, nada de config. |
| **database** | Criação da conexão/pool/sessão, schema e seed. Fica junto da camada de dados ou da config, conforme a convenção da stack. |
| **errors** | Tipos de erro de domínio (validação, não encontrado, proibido, conflito) que o error handler converte em status HTTP. |

## 4. Estrutura de diretórios

Estrutura **lógica** de referência — traduza nomes, casing, agrupamento (por camada ou por domínio) e localização (`src/`, pacote raiz, namespace) para a convenção da stack descrita no guia:

```
<raiz do código>/
├── <entry point>        # composition root fino: monta tudo e inicia o servidor
├── config/              # leitura do ambiente + objeto de config
├── models/              # entidades + acesso a dados (ou entities/ + repositories/)
│   └── database         # conexão/pool, schema, seed
├── controllers/         # fluxo de cada caso de uso
├── services/            # opcional: regras entre entidades / integrações
├── routes/ (ou views/)  # mapeamento HTTP → controller
├── middlewares/         # error handler, auth, logging
├── errors/              # erros de domínio (pode ficar em utils/)
└── utils/               # funções puras
<arquivo de exemplo de variáveis de ambiente, sem valores reais>
```

- **Por camada vs. por domínio:** ambos são válidos. Siga o que a stack/projeto já usa; em projetos grandes, agrupar por domínio (cada domínio com suas camadas) costuma ser mais idiomático em algumas stacks.
- **Entry point:** mantenha o arquivo/comando de start original funcionando — se o arquivo de entrada mudar de lugar, ele vira uma ponte ou o manifesto passa a apontar para o novo.
- **Frameworks que já impõem estrutura:** não crie pastas paralelas às da convenção do framework. Mapeie as camadas acima para os conceitos do framework (o guia da stack traz esse mapeamento) e corrija os vazamentos dentro dela.

## 5. Projetos parcialmente organizados ou já em camadas

Quando já existem pastas/pacotes de camadas:
1. **Mapeie** cada pasta existente para uma camada do alvo. Não crie uma pasta nova paralela a uma existente que cumpre o mesmo papel — renomear sem ganho só gera ruído.
2. **Crie apenas o que falta** (normalmente controllers, config, middlewares).
3. **Mova o conteúdo errado**: lógica de negócio das rotas → controllers/services; queries das rotas → models; constantes repetidas → config/utils.
4. **Reconecte o código morto útil**: helpers e serviços que existiam mas não eram usados devem passar a ser usados (ou removidos, se redundantes).
5. **Separe domínios misturados**: um arquivo de rotas que cuida de duas entidades vira dois.

**Projeto já em camadas** (MVC, Clean, Hexagonal...): **não** converta para outra arquitetura. Preserve a estrutura e aplique apenas as correções dos achados aprovados nos lugares onde estão.

## 6. Convenções

- **Um domínio por arquivo/classe** em cada camada.
- **Nomes** seguem a convenção da linguagem (casing, sufixos idiomáticos); mantenha o idioma do domínio que o projeto já usa para entidades, mas nomes claros (sem abreviações crípticas).
- **Contrato JSON**: nomes de campos de entrada/saída não mudam, mesmo que sejam ruins — mapeie internamente.
- **Erros**: formato único definido no error handler, preservando a chave que o projeto já usava nas respostas de erro.
- **Sem efeitos colaterais no import/carregamento**: criar tabela/seed/conectar acontece na inicialização chamada pelo composition root.
- **Segredos**: só via config/ambiente. O arquivo de exemplo lista as variáveis sem valores reais. Não versione o arquivo com valores reais.

## 7. Checklist de conformidade (use na validação)

- [ ] Estrutura segue as camadas alvo na convenção da stack
- [ ] Configuração extraída para o módulo de config (nenhum segredo hardcoded; arquivo de exemplo de variáveis presente)
- [ ] Models abstraem todo o acesso a dados (nenhum SQL/ORM fora da camada de dados)
- [ ] Views/Routes apenas roteiam (sem regra de negócio)
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado (sem captura copiada por rota; sem mensagem/stack de exceção para o cliente)
- [ ] Entry point claro (composition root) e comandos de build/start originais funcionando
- [ ] Nenhum estado global mutável compartilhado entre requisições
