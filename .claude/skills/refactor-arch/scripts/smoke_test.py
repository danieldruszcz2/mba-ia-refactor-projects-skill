#!/usr/bin/env python3
"""Smoke test HTTP genérico para a Fase 3 do refactor-arch (somente stdlib).

Subcomandos:
  wait     Espera o servidor responder (qualquer status HTTP) até o timeout.
           python smoke_test.py wait --url http://127.0.0.1:5000/ --timeout 30

  run      Executa os endpoints de um arquivo JSON e salva os resultados.
           python smoke_test.py run --base-url http://127.0.0.1:5000 \
               --endpoints reports/endpoints.json --out reports/baseline.json

  compare  Compara dois resultados (baseline x refatorado).
           python smoke_test.py compare --baseline reports/baseline.json \
               --current reports/after.json [--allow "admin-query,admin-reset"]

Formato de endpoints.json (lista, executada em ordem):
[
  {"name": "list-items", "method": "GET", "path": "/items"},
  {"name": "create-item", "method": "POST", "path": "/items",
   "body": {"name": "Smoke", "price": 10}, "capture": {"item_id": "id"}},
  {"name": "get-item", "method": "GET", "path": "/items/{{item_id}}"},
  {"name": "reset-db", "method": "POST", "path": "/admin/reset", "skip": "destrutivo"}
]
- "capture": salva valores da resposta JSON (caminho com pontos, ex.: "data.id" ou "0.id")
  em variáveis usadas depois como {{nome}} em path/body/headers.
- "skip": motivo para não executar (endpoint destrutivo/externo); aparece no relatório.
- "headers": dict opcional. "expect_status": int opcional (falha se diferente).

Saída de `compare`: código 0 se todos os endpoints batem (status + formato da resposta),
1 caso contrário. Endpoints em --allow podem divergir (mudanças de comportamento declaradas).
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request

VAR_OPEN, VAR_CLOSE = "{{", "}}"


def substitute(value, variables):
    if isinstance(value, str):
        for key, val in variables.items():
            value = value.replace(VAR_OPEN + key + VAR_CLOSE, str(val))
        return value
    if isinstance(value, dict):
        return {k: substitute(v, variables) for k, v in value.items()}
    if isinstance(value, list):
        return [substitute(v, variables) for v in value]
    return value


def extract(data, dotted):
    current = data
    for part in dotted.split("."):
        if isinstance(current, list) and part.isdigit():
            idx = int(part)
            current = current[idx] if idx < len(current) else None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        if current is None:
            return None
    return current


def shape(data):
    """Assinatura estrutural da resposta: tipo + chaves (1 nível; para listas, do 1º item)."""
    if isinstance(data, dict):
        return {"type": "object", "keys": sorted(data.keys())}
    if isinstance(data, list):
        first = data[0] if data else None
        inner = sorted(first.keys()) if isinstance(first, dict) else None
        return {"type": "array", "item_keys": inner}
    if data is None:
        return {"type": "empty"}
    return {"type": type(data).__name__}


def same_shape(a, b):
    """Compara formatos; listas vazias de um dos lados não acusam diferença de chaves."""
    if a == b:
        return True
    if a and b and a.get("type") == b.get("type") == "array":
        return a.get("item_keys") is None or b.get("item_keys") is None
    return False


def request(base_url, method, path, body=None, headers=None, timeout=15):
    url = base_url.rstrip("/") + path
    data = None
    hdrs = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method.upper(), headers=hdrs)
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status, raw = resp.status, resp.read()
    except urllib.error.HTTPError as err:
        status, raw = err.code, err.read()
    elapsed = round((time.time() - started) * 1000)
    text = raw.decode("utf-8", errors="replace")
    try:
        parsed = json.loads(text) if text.strip() else None
        is_json = True
    except ValueError:
        parsed, is_json = None, False
    return status, parsed, is_json, text[:300], elapsed


def cmd_wait(args):
    deadline = time.time() + args.timeout
    last_error = None
    while time.time() < deadline:
        try:
            urllib.request.urlopen(args.url, timeout=3)
            print(f"UP: {args.url}")
            return 0
        except urllib.error.HTTPError:
            print(f"UP: {args.url} (respondeu com status HTTP de erro, mas o servidor está de pé)")
            return 0
        except Exception as err:  # conexão recusada, timeout etc.
            last_error = err
            time.sleep(0.5)
    print(f"DOWN: {args.url} não respondeu em {args.timeout}s ({last_error})")
    return 1


def cmd_run(args):
    with open(args.endpoints, encoding="utf-8") as fh:
        endpoints = json.load(fh)
    variables, results, failures = {}, [], 0
    for ep in endpoints:
        name = ep.get("name") or f"{ep['method']} {ep['path']}"
        if ep.get("skip"):
            results.append({"name": name, "method": ep["method"], "path": ep["path"],
                            "skipped": ep["skip"]})
            print(f"SKIP  {ep['method']:6} {ep['path']}  ({ep['skip']})")
            continue
        path = substitute(ep["path"], variables)
        body = substitute(ep.get("body"), variables)
        headers = substitute(ep.get("headers"), variables)
        try:
            status, parsed, is_json, preview, ms = request(
                args.base_url, ep["method"], path, body, headers, args.timeout)
        except Exception as err:
            failures += 1
            results.append({"name": name, "method": ep["method"], "path": path,
                            "error": str(err)})
            print(f"ERROR {ep['method']:6} {path}  {err}")
            continue
        for var, dotted in (ep.get("capture") or {}).items():
            value = extract(parsed, dotted)
            if value is not None:
                variables[var] = value
        expected = ep.get("expect_status")
        ok = status < 500 and (expected is None or status == expected)
        failures += 0 if ok else 1
        results.append({"name": name, "method": ep["method"], "path": path, "status": status,
                        "json": is_json, "shape": shape(parsed) if is_json else None,
                        "ok": ok, "ms": ms, "preview": preview})
        print(f"{'OK  ' if ok else 'FAIL'}  {ep['method']:6} {path}  -> {status} ({ms}ms)")
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump({"base_url": args.base_url, "results": results}, fh, indent=2, ensure_ascii=False)
    executed = len([r for r in results if "skipped" not in r])
    print(f"\n{executed - failures}/{executed} endpoints OK (sem 5xx/erro) | resultados em {args.out}")
    return 0 if failures == 0 else 1


def cmd_compare(args):
    with open(args.baseline, encoding="utf-8") as fh:
        base = {r["name"]: r for r in json.load(fh)["results"]}
    with open(args.current, encoding="utf-8") as fh:
        curr = {r["name"]: r for r in json.load(fh)["results"]}
    allowed = {a.strip() for a in (args.allow or "").split(",") if a.strip()}
    mismatches, matched, skipped = [], 0, 0
    for name, b in base.items():
        c = curr.get(name)
        if c is None:
            mismatches.append(f"{name}: ausente no resultado atual")
            continue
        if "skipped" in b or "skipped" in c:
            skipped += 1
            continue
        problems = []
        if b.get("status") != c.get("status"):
            problems.append(f"status {b.get('status')} -> {c.get('status')}")
        if b.get("json") and c.get("json") and not same_shape(b.get("shape"), c.get("shape")):
            problems.append(f"formato {b.get('shape')} -> {c.get('shape')}")
        if "error" in c:
            problems.append(f"erro: {c['error']}")
        if problems and name in allowed:
            print(f"ALLOWED  {name}: {'; '.join(problems)} (mudança declarada)")
            matched += 1
        elif problems:
            mismatches.append(f"{name}: {'; '.join(problems)}")
        else:
            matched += 1
    for line in mismatches:
        print(f"DIFF     {line}")
    total = len(base) - skipped
    print(f"\n{matched}/{total} endpoints equivalentes à baseline | {skipped} pulados")
    return 0 if not mismatches else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("wait")
    w.add_argument("--url", required=True)
    w.add_argument("--timeout", type=int, default=30)
    r = sub.add_parser("run")
    r.add_argument("--base-url", required=True)
    r.add_argument("--endpoints", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--timeout", type=int, default=15)
    c = sub.add_parser("compare")
    c.add_argument("--baseline", required=True)
    c.add_argument("--current", required=True)
    c.add_argument("--allow", default="")
    args = parser.parse_args()
    return {"wait": cmd_wait, "run": cmd_run, "compare": cmd_compare}[args.cmd](args)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
