#!/usr/bin/env python3
"""
Diagnóstico do fluxo de criação de conta (register + login).

Uso:
  python scripts/check_signup.py                          # testa localhost
  python scripts/check_signup.py http://204.216.144.197:8000/api/v1

O script tenta:
  1. POST /auth/register  — criar conta
  2. POST /auth/login     — logar com a conta criada
  3. GET  /auth/me        — validar o token retornado

Imprime status code, resposta JSON e erro completo quando houver falha.
"""

import json
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE_URL = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1").rstrip("/")

TEST_EMAIL = f"diag_{uuid.uuid4().hex[:8]}@check.local"
TEST_PASS = "senha123"
TEST_NICK = "DiagUser"


def _request(method: str, path: str, body: dict | None = None, token: str | None = None) -> tuple[int, object]:
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw
    except urllib.error.URLError as e:
        return 0, str(e.reason)
    except Exception as e:
        return -1, str(e)


def _print(label: str, status: int, payload: object) -> None:
    ok = "OK" if 200 <= status < 300 else "FAIL"
    print(f"\n[{ok}] {label}")
    print(f"  Status : {status}")
    print(f"  Body   : {json.dumps(payload, ensure_ascii=False, indent=4) if isinstance(payload, (dict, list)) else payload}")


def main() -> None:
    print(f"Base URL : {BASE_URL}")
    print(f"Email    : {TEST_EMAIL}")
    print("-" * 60)

    # 1. Health check
    status, body = _request("GET", "/health".replace("/api/v1", "")
                             if "/api/v1" in BASE_URL else "/health")
    # Try health at root (strip the /api/v1 prefix)
    root_url = BASE_URL.replace("/api/v1", "")
    req = urllib.request.Request(f"{root_url}/health", headers={"Accept": "application/json"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            health_status = resp.status
            health_body = json.loads(resp.read().decode())
    except Exception as e:
        health_status = 0
        health_body = str(e)
    _print("GET /health", health_status, health_body)

    # 2. Register
    status, body = _request("POST", "/auth/register", {
        "email": TEST_EMAIL,
        "password": TEST_PASS,
        "nickname": TEST_NICK,
    })
    _print("POST /auth/register", status, body)

    if status != 201:
        print("\n[STOP] Registro falhou — abortando teste de login.")
        _diagnose_register(status, body)
        sys.exit(1)

    # 3. Login
    status, body = _request("POST", "/auth/login", {
        "email": TEST_EMAIL,
        "password": TEST_PASS,
    })
    _print("POST /auth/login", status, body)

    if status != 200:
        print("\n[STOP] Login falhou após registro bem-sucedido.")
        sys.exit(1)

    token = body.get("accessToken") or body.get("access_token") if isinstance(body, dict) else None
    print(f"\n  Token (primeiros 30 chars): {str(token)[:30]}..." if token else "\n  [WARN] Token não encontrado na resposta")

    # 4. /auth/me
    if token:
        status, body = _request("GET", "/auth/me", token=token)
        _print("GET /auth/me", status, body)

    print("\n" + "=" * 60)
    print("Diagnóstico concluído — sem erros críticos encontrados.")


def _diagnose_register(status: int, body: object) -> None:
    print("\n--- Diagnóstico ---")
    if status == 0:
        print("  Causa provável : servidor inacessível ou CORS bloqueando a requisição.")
        print("  Verifique      : BACKEND_CORS_ORIGINS e se o serviço está rodando.")
    elif status == 404:
        print("  Causa provável : URL errada — a rota /auth/register não existe nesse caminho.")
        print("  Dica           : o backend usa prefixo /api/v1. NEXT_PUBLIC_API_URL deve terminar em /api/v1")
        print(f"  URL testada    : {BASE_URL}/auth/register")
        print(f"  Tente          : {BASE_URL.rstrip('/api/v1')}/api/v1/auth/register")
    elif status == 422:
        print("  Causa provável : payload inválido (campo faltando ou tipo errado).")
        print("  Resposta       :", json.dumps(body, indent=4) if isinstance(body, dict) else body)
    elif status == 500:
        print("  Causa provável : erro interno — banco de dados inacessível ou DATABASE_URL errada.")
        print("  Verifique      : DATABASE_URL, se Postgres está rodando e se as migrations foram aplicadas.")
    elif status == 409:
        print("  INFO: Email já cadastrado — o usuário de teste já existe. Isso é OK.")


if __name__ == "__main__":
    main()
