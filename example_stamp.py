#!/usr/bin/env python3
"""Example: Stamp a document hash via Kavra Siegel MCP.

Usage:
    SERVICE_TOKEN=your_token python example_stamp.py
"""

import hashlib
import json
import os
import sys

import httpx

MCP_URL = os.environ.get("SIEGEL_MCP_URL", "https://siegel.kavra.cloud/mcp")
SERVICE_TOKEN = os.environ.get("SERVICE_TOKEN", "")

if not SERVICE_TOKEN:
    print("Set SERVICE_TOKEN environment variable", file=sys.stderr)
    sys.exit(1)

headers = {
    "X-Kavra-Service-Token": SERVICE_TOKEN,
    "Content-Type": "application/json",
}


def rpc(method: str, params: dict | None = None, id: int = 1) -> dict:
    body = {"jsonrpc": "2.0", "id": id, "method": method}
    if params:
        body["params"] = params
    resp = httpx.post(MCP_URL, headers=headers, json=body, timeout=10)
    data = resp.json()
    if "error" in data:
        print(f"Error: {data['error']}", file=sys.stderr)
        sys.exit(1)
    return data["result"]


# 1. Initialize
result = rpc("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "kavra-siegel-example", "version": "1.0"},
})
print(f"Connected to: {result['serverInfo']['name']} v{result['serverInfo']['version']}")

# 2. List tools
result = rpc("tools/list", id=2)
print(f"\nAvailable tools ({len(result['tools'])}):")
for tool in result["tools"]:
    print(f"  - {tool['name']}")

# 3. Stamp a hash
content = b"This compliance audit was completed on 2026-06-03 by AI Agent."
sha256 = hashlib.sha256(content).hexdigest()
print(f"\nStamping hash: {sha256[:16]}...")

result = rpc("tools/call", {
    "name": "kavra_siegel_stamp_hash",
    "arguments": {
        "sha256_hex": sha256,
        "tier": "basic",
        "metadata": {"source": "example-script", "purpose": "demo"},
    },
}, id=3)
print(f"Result: {result['content'][0]['text']}")

# 4. Verify (extract token_id from result text)
text = result["content"][0]["text"]
if "token_id=" in text:
    token_id = text.split("token_id=")[1].split(",")[0]
    print(f"\nVerifying token: {token_id}")
    result = rpc("tools/call", {
        "name": "kavra_siegel_verify_token",
        "arguments": {"token_id": token_id},
    }, id=4)
    print(f"Verification: {result['content'][0]['text']}")
