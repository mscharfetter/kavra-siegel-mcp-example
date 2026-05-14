# Kavra Siegel — MCP Server Example

Example code for interacting with the [Kavra Siegel](https://siegel.kavra.cloud) qualified eIDAS timestamp service via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

## What is Kavra Siegel?

Kavra Siegel provides qualified electronic timestamps per EU Regulation 910/2014 (eIDAS). AI agents and compliance tools can timestamp documents, hashes, and audit trails with legally binding, tamper-proof proofs.

**Current status:** Mock timestamps (qualified timestamps available after SIGNIUS TSP contract, planned Q4 2026).

## MCP Endpoint

```
POST https://siegel.kavra.cloud/mcp
```

**Auth:** `X-Kavra-Service-Token` header (contact office@kavra.cloud for access).

**Discovery:** `GET https://siegel.kavra.cloud/.well-known/mcp.json`

## Available Tools

| Tool | Description |
|------|-------------|
| `kavra_siegel_stamp_hash` | Timestamp a SHA-256 hash |
| `kavra_siegel_stamp_content` | Timestamp base64-encoded content |
| `kavra_siegel_verify_token` | Verify an existing timestamp |

## Python Example

```python
import httpx
import json

MCP_URL = "https://siegel.kavra.cloud/mcp"
SERVICE_TOKEN = "your-service-token"

headers = {
    "X-Kavra-Service-Token": SERVICE_TOKEN,
    "Content-Type": "application/json",
}

# 1. Initialize
resp = httpx.post(MCP_URL, headers=headers, json={
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "my-agent", "version": "1.0"},
    },
})
print("Server:", resp.json()["result"]["serverInfo"])

# 2. List tools
resp = httpx.post(MCP_URL, headers=headers, json={
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
})
for tool in resp.json()["result"]["tools"]:
    print(f"  - {tool['name']}: {tool['description'][:60]}...")

# 3. Stamp a hash
import hashlib
content = b"This document was reviewed on 2026-05-14."
sha256 = hashlib.sha256(content).hexdigest()

resp = httpx.post(MCP_URL, headers=headers, json={
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "kavra_siegel_stamp_hash",
        "arguments": {
            "sha256_hex": sha256,
            "tier": "basic",
            "metadata": {"source": "my-agent"},
        },
    },
})
print("Stamp result:", resp.json()["result"]["content"][0]["text"])
```

## TypeScript / JavaScript Example

```typescript
const MCP_URL = "https://siegel.kavra.cloud/mcp";
const SERVICE_TOKEN = "your-service-token";

const headers = {
  "X-Kavra-Service-Token": SERVICE_TOKEN,
  "Content-Type": "application/json",
};

// List tools
const resp = await fetch(MCP_URL, {
  method: "POST",
  headers,
  body: JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/list",
  }),
});
const { result } = await resp.json();
console.log("Tools:", result.tools.map((t: any) => t.name));

// Stamp a hash
const content = new TextEncoder().encode("Audit completed 2026-05-14");
const hashBuffer = await crypto.subtle.digest("SHA-256", content);
const sha256 = Array.from(new Uint8Array(hashBuffer))
  .map((b) => b.toString(16).padStart(2, "0"))
  .join("");

const stampResp = await fetch(MCP_URL, {
  method: "POST",
  headers,
  body: JSON.stringify({
    jsonrpc: "2.0",
    id: 2,
    method: "tools/call",
    params: {
      name: "kavra_siegel_stamp_hash",
      arguments: { sha256_hex: sha256, tier: "basic" },
    },
  }),
});
console.log("Stamp:", await stampResp.json());
```

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kavra-siegel": {
      "url": "https://siegel.kavra.cloud/mcp",
      "headers": {
        "X-Kavra-Service-Token": "your-service-token"
      }
    }
  }
}
```

## Verification

Every stamp includes a `verify_url`. Open it in a browser to verify the timestamp:

```
https://siegel.kavra.cloud/api/v1/verify/v1/token/{token_id}
```

## x402 Payment (Coming Soon)

Future support for pay-per-stamp via USDC on Base chain (x402 protocol). Currently returns 503. Planned for Q4 2026 after SIGNIUS TSP contract.

## License

MIT
