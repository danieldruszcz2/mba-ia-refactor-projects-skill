# Template do Relatório de Auditoria (Fase 2)

Use **exatamente** esta estrutura. O mesmo texto é impresso no terminal e salvo em `<raiz do repositório>/reports/audit-project-<N>.md` (regra completa de caminho e numeração no `SKILL.md`, Fase 2, passo 2; crie a pasta se não existir). O relatório é Markdown válido mesmo quando impresso.

## Regras de preenchimento

- **Ordem:** CRITICAL → HIGH → MEDIUM → LOW. Dentro da mesma severidade, ordene pelo impacto (segurança antes de estrutura).
- **Numeração:** `#1`, `#2`, ... contínua no relatório inteiro — o usuário usa esses números no `skip`.
- **Location (tabela do Summary):** o mesmo `arquivo:linha` real do achado. **Nunca use curingas** (`routes/*.py`, `models/`, `vários arquivos`) nem um arquivo sem linha. Se o achado abrange muitos arquivos, liste os principais com linha e indique o resto: `routes/task_routes.py:11-63; routes/user_routes.py:42-90 (+1 arquivo)`.
- **File:** caminho relativo à raiz do projeto + linha(s) reais: `<arquivo>:45`, `<arquivo>:45-62`, ou várias ocorrências separadas por vírgula: `<arquivo>:45, 88, 120-131`. Se o achado abrange vários arquivos, uma linha `File:` por arquivo.
- **Description:** o que está errado, citando o trecho/identificador concreto (nome da função, variável, valor). 1–3 frases.
- **Impact:** a consequência real (o que um atacante/usuário/mantenedor sofre). 1–2 frases.
- **Recommendation:** a correção concreta, no vocabulário da stack detectada. 1–2 frases.
- **Playbook:** o ID do padrão de transformação (`P-xx`) — e o ID do catálogo (`AP-xx`) no título.
- **Deprecated APIs:** use o título `Deprecated API: <api>` e inclua na recomendação o equivalente moderno e a versão em que mudou.
- **Summary:** as contagens devem bater com os achados listados. `Total` = soma.
- Sem achados de uma severidade? Mostre `0` no summary — não invente achados para "distribuir" severidades.

## Template

O **arquivo salvo** começa com o bloco da Fase 1 (o mesmo texto impresso na Fase 1, com a tabela de endpoints, dentro de um bloco de código), seguido de uma linha em branco e do relatório abaixo. No terminal, a mensagem da Fase 2 também traz o bloco da Fase 1 antes do relatório.


````markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório do projeto>
Stack:   <Linguagem> <versão> + <Framework> <versão> | DB: <banco>
Files:   <n> analyzed | ~<n> lines of code
Date:    <AAAA-MM-DD>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

| # | Severity | Anti-pattern | Location |
|---|----------|--------------|----------|
| 1 | CRITICAL | <título curto> | <arquivo:linha> |
| ... | | | |

## Findings

### #1 [CRITICAL] <Título do anti-pattern> (AP-xx)
File: <arquivo>:<linhas>
Description: <o que foi encontrado, com o trecho/identificador>
Impact: <consequência>
Recommendation: <correção concreta>
Playbook: P-xx

### #2 [CRITICAL] ...

### #n [LOW] ...

## Architecture Notes
<2–5 bullets sobre a arquitetura atual vs. MVC alvo: quais camadas existem, quais faltam, o que está no lugar errado, código/estrutura morta. Isso antecipa o plano da Fase 3.>

================================
Total: <n> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
  y              → corrige todos os achados
  n              → encerra sem modificar nenhum arquivo
  y, skip 3,7    → corrige todos exceto os achados #3 e #7
````

> No arquivo salvo, inclua a pergunta de confirmação também — ela documenta que a auditoria parou aguardando aprovação.

## Exemplo de achados bem escritos

Os exemplos abaixo mostram o **nível de detalhe** esperado. Arquivos, identificadores e APIs são fictícios — no relatório real, use os nomes e o vocabulário da stack detectada.

```markdown
### #1 [CRITICAL] SQL Injection (AP-02)
File: <camada-de-dados>/user_repository.<ext>:28, 47, 63-66, 102
Description: `findUserByEmail` e outras 3 funções montam a consulta concatenando o parâmetro `email` (vindo do body) diretamente na string SQL passada ao driver.
Impact: Um atacante burla o login com `' OR '1'='1` e pode ler ou apagar qualquer tabela.
Recommendation: Usar consultas parametrizadas (placeholders do driver/ORM em uso) em todas as consultas, dentro da camada Model.
Playbook: P-02

### #9 [MEDIUM] Deprecated API: <nome da API> (AP-18)
File: <arquivo>:14, 15; <outro arquivo>:52
Description: `<API>` é usada para gerar timestamps de criação/atualização; está deprecated desde <lib/linguagem> <versão> e <problema concreto, ex.: retorna data sem fuso>.
Impact: Gera avisos de depreciação e será removida; <consequência concreta no projeto>.
Recommendation: Substituir por `<API moderna>` (disponível desde <versão>), centralizada em um helper único.
Playbook: P-12

### #14 [LOW] Nomenclatura críptica (AP-20)
File: <arquivo>:12-30
Description: Variáveis `u`, `e`, `p`, `cc` no fluxo de pagamento escondem o significado (usuário, email, senha, cartão).
Impact: Leitura lenta e propensa a erro; dificulta revisão de código sensível.
Recommendation: Renomear internamente para nomes descritivos na convenção da linguagem, mantendo os nomes de campo do JSON (contrato da API).
Playbook: P-13
```

## Exemplos ruins (evite)

- `File: <arquivo>` — sem linha.
- `Description: Código ruim.` — sem evidência.
- Mesma injeção SQL listada 6 vezes como 6 achados separados (agrupe por arquivo/padrão).
- Achado "Falta de testes" sem relação com o catálogo e sem local.
