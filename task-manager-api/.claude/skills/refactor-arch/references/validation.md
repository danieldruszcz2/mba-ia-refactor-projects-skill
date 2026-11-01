# Validação (Fase 3)

A refatoração só está concluída quando a aplicação **compila (se aplicável) e sobe sem erros** com os comandos originais e **os endpoints originais respondem** como antes. Esta validação compara a app refatorada com uma *baseline* capturada da app original, tratando a aplicação como **caixa-preta HTTP** — por isso funciona para qualquer stack.

## Sumário
1. Ambiente isolado e build
2. Montar o arquivo de endpoints
3. Subir a app em background e derrubar no final
4. Proteger os dados e capturar a baseline
5. Validar o resultado
6. Interpretar diferenças
7. Problemas comuns

O script `scripts/smoke_test.py` (somente stdlib Python 3) faz `wait`, `run` e `compare`. Ele é independente da stack da aplicação — só precisa de um Python 3 na máquina. Se não houver Python disponível, reproduza o mesmo fluxo com um cliente HTTP de linha de comando (ex.: `curl -s -o <arquivo> -w "%{http_code}"`): registre status e chaves de primeiro nível do JSON de cada endpoint antes e depois, e compare.

---

## 1. Ambiente isolado e build

Use os comandos da seção **"Ambiente"** do guia da stack ou, na falta dele, os declarados no manifesto/README. Ordem de preferência: wrapper/script do próprio projeto → ferramenta padrão da stack.

- Crie o ambiente/instale dependências **uma vez**, em local ignorado pelo versionamento, e reutilize-o na baseline e na validação.
- **Linguagens compiladas:** compile antes da baseline e **recompile** antes da validação — o artefato antigo não reflete a refatoração. Pule a execução dos testes no build da baseline se eles forem lentos; rode-os no passo 5.
- Se uma dependência fixada não instala na versão atual da toolchain, tente a versão compatível mais próxima **apenas no ambiente de teste** e registre como "Manual Follow-up" — não altere o manifesto sem necessidade.
- Garanta que diretórios de dependências, artefatos de build e bancos gerados estejam no `.gitignore` (adicione se faltarem).

## 2. Montar o arquivo de endpoints

Gere `reports/endpoints.json` a partir do inventário da Fase 1 (formato documentado no topo de `smoke_test.py`). Regras:

- **Um item por endpoint** do inventário, com `name` estável (ex.: `get-user-by-id`) — o `compare` casa resultados pelo nome.
- **Ordem segura:** leituras (GET) → criações (POST, capturando ids com `capture`) → leituras dos itens criados → atualizações (PUT/PATCH) → deleções **dos itens criados pelo próprio teste**.
- **Bodies válidos:** use exemplos de coleções de requisições/OpenAPI/README/testes; senão, construa a partir das validações do código e dos dados de seed. Um endpoint que responde `400` por body inválido não prova nada — ajuste o body até obter o status de sucesso.
- **Autenticação:** se rotas exigem login, inclua o endpoint de login antes e capture o token para usar em `headers`.
- **Casos de erro úteis:** inclua 1–2 casos esperados de `404`/`400` (ex.: id inexistente) — eles validam o error handler.
- **Endpoints destrutivos/externos** (reset de banco, SQL arbitrário, cobrança real, envio de mensagem real): marque com `"skip": "<motivo>"` na baseline. Depois da refatoração, eles devem responder `403` com a flag desligada — teste isso separadamente (item com `expect_status: 403`) e declare como mudança de comportamento.
- Use ids do seed para leituras apenas se o seed for determinístico.

## 3. Subir a app em background e derrubar no final

Use o **comando de start original** (após o build, se houver) e uma porta livre. Rode-o em background (`run_in_background: true` no Bash tool), redirecionando a saída para `reports/server.log`:

```bash
<comando de start> > reports/server.log 2>&1
```

Depois espere ficar de pé e só então rode o smoke test:

```bash
python .claude/skills/refactor-arch/scripts/smoke_test.py wait --url http://127.0.0.1:<porta>/ --timeout 60
```

Stacks com boot lento (ex.: compilação sob demanda, containers de DI grandes) podem precisar de `--timeout` maior. Se o `wait` falhar, leia `reports/server.log` — é ali que aparece o erro de compilação, import ou configuração.

**Derrubar o servidor:** encerre a tarefa em background (TaskStop) ou mate o processo pela porta:
- Linux/macOS: `kill $(lsof -t -i:<porta>)`
- Windows (PowerShell): `Get-NetTCPConnection -LocalPort <porta> -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`

Atenção: wrappers de build podem iniciar a app num processo filho — mate o processo que escuta na porta, não só o wrapper. Confirme que a porta foi liberada antes de subir de novo. Nunca deixe servidores rodando ao terminar a skill.

Se a porta padrão estiver ocupada, use o mecanismo de porta por ambiente/argumento (após P-01 ele existe; na baseline, apenas se o código original já o suportava).

## 4. Proteger os dados e capturar a baseline

O smoke test cria, altera e apaga dados. Antes de subir a app original, escolha a estratégia conforme o tipo de banco detectado na Fase 1:

| Banco | Estratégia |
|---|---|
| Em memória / recriado no boot | Nada a proteger; cada boot começa do zero. |
| Arquivo local | Copie os arquivos de banco para `reports/db-backup/` e restaure após cada execução. |
| Servidor (relacional, documento, cache) | Use uma instância **descartável**: serviço do `docker-compose` do projeto, container temporário ou perfil/config de teste já existente no projeto. Aponte a app para ela via variável de ambiente. Se nada disso for possível, **pergunte ao usuário** antes de executar endpoints de escrita; sem autorização, marque-os com `skip` e valide só leituras. |

Nunca execute o smoke test contra um banco compartilhado ou de produção.

Então:
1. Suba a app **original** e rode:
   ```bash
   python .claude/skills/refactor-arch/scripts/smoke_test.py run --base-url http://127.0.0.1:<porta> \
     --endpoints reports/endpoints.json --out reports/baseline.json
   ```
2. Derrube a app e **restaure** os dados (o smoke test criou/alterou registros).
3. Se algum endpoint já falha na original (5xx), anote: é um bug pré-existente. A refatoração deve corrigi-lo se estiver no escopo dos achados (ex.: validação ausente); senão, não pode piorar.

## 5. Validar o resultado

1. Restaure os dados (mesmo estado inicial da baseline). Se o banco é criado no boot, apague o que foi gerado para começar do zero exatamente como a baseline.
2. Instale dependências novas, se adicionou alguma, e **recompile** se a stack exigir.
3. Suba com o **comando de start original** → `wait` deve responder `UP`. Verifique o log: sem erros e sem avisos de depreciação das APIs corrigidas.
4. Rode:
   ```bash
   python .claude/skills/refactor-arch/scripts/smoke_test.py run --base-url http://127.0.0.1:<porta> \
     --endpoints reports/endpoints.json --out reports/after.json
   python .claude/skills/refactor-arch/scripts/smoke_test.py compare \
     --baseline reports/baseline.json --current reports/after.json --allow "<nomes de mudanças declaradas>"
   ```
5. Rode a suíte de testes existente do projeto, se houver (comando no guia da stack / manifesto).
6. Rode novamente as buscas do catálogo (genéricas + do guia da stack) para os achados corrigidos: concatenação em SQL, segredos, debug ligado, APIs deprecated etc. não podem aparecer nos arquivos novos.
7. Derrube o servidor e restaure os dados ao estado original (ou descarte a instância temporária).
8. Mantenha `reports/endpoints.json`, `baseline.json` e `after.json` como evidência; remova `reports/db-backup/` e `server.log` se não forem mais úteis.

## 6. Interpretar diferenças

| Diferença | Ação |
|---|---|
| Status 2xx → 5xx, ou app não compila/sobe | Bug da refatoração. Leia o log, corrija, valide de novo. |
| Formato mudou (chaves diferentes) | Quebra de contrato — restaure as chaves, **exceto** remoção de campos sensíveis declarada (ex.: senha). |
| 5xx → 400 | Melhoria esperada (validação). Declare como mudança de comportamento. |
| 2xx → 403 em rota admin/perigosa | Esperado se a flag está desligada (P-07). Declare. |
| Status 2xx diferente (200 ↔ 201) | Restaure o status original — clientes podem depender dele. |

Para campos sensíveis removidos, o `compare` acusará diferença de formato: inclua o endpoint em `--allow` e liste a mudança no resumo final.

## 7. Problemas comuns

- **Imports/pacotes quebrados após mover arquivos:** confira as regras de módulos/pacotes da linguagem (arquivos de pacote, namespaces, caminhos de import relativos à raiz) e evite dependências circulares (models não importam controllers).
- **Componentes não encontrados pelo framework após mover:** frameworks com descoberta automática (varredura de pacotes, autoload, convenção de nomes) só enxergam o que está nos locais configurados — confira esses locais.
- **Rotas registradas com prefixo diferente** → todos os endpoints 404. Compare os caminhos com o inventário.
- **Ordem de middlewares/filtros:** parsing do body antes das rotas; error handler conforme exigido pelo framework (geralmente o último).
- **Caminho do banco relativo ao diretório atual:** após mover o código, caminhos relativos podem apontar para outro lugar — resolva caminhos a partir da config.
- **Encoding no Windows:** ao escrever arquivos com acentos, use UTF-8.
- **Seed rodando duas vezes** (dados duplicados) após virar função de inicialização: proteja com checagem de existência/tabela vazia, como era o comportamento original.
