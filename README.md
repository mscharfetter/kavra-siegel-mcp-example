# Kavra Siegel — MCP Server for Qualified eIDAS Timestamps

**eIDAS-qualified via SIGNIUS/IDnow Trust Services AB (EU Trusted List)**

Kavra Siegel is the first MCP-enabled qualified eIDAS timestamp service. AI agents and compliance tools can create legally binding, tamper-proof timestamps for documents, hashes, and audit trails — directly from Claude, Cursor, or any MCP-compatible client.

- **RFC 3161** timestamps via SIGNIUS (IDnow Trust Services AB, Swedish QTSP on EU Trusted List)
- **Three tools**: stamp a hash, stamp content, verify a token
- **Non-custodial**: we never see your content — only SHA-256 hashes are sent to the TSA

Blog post: [Kavra Siegel Live — Qualifizierte Zeitstempel für AI Agents](https://kavra.cloud/blog/kavra-siegel-live-qualifizierte-zeitstempel/)

## Quickstart (Claude Desktop)

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

Restart Claude Desktop. You can now ask:

> "Timestamp this SHA-256 hash: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`"

## MCP Endpoint

```
POST https://siegel.kavra.cloud/mcp
```

**Auth:** `X-Kavra-Service-Token` header (contact office@kavra.cloud for access)

**Discovery:** `GET https://siegel.kavra.cloud/.well-known/mcp.json`

## Available Tools

| Tool | Description |
|------|-------------|
| `kavra_siegel_stamp_hash` | Create a qualified eIDAS timestamp for a SHA-256 hash |
| `kavra_siegel_stamp_content` | Timestamp base64-encoded content (hash computed server-side) |
| `kavra_siegel_verify_token` | Verify an existing timestamp by token UUID |

---

## Use Case 1: Stamp a Workflow Briefing

```python
import hashlib
import httpx

MCP_URL = "https://siegel.kavra.cloud/mcp"
HEADERS = {"X-Kavra-Service-Token": "your-token", "Content-Type": "application/json"}

def rpc(method, params=None, id=1):
    body = {"jsonrpc": "2.0", "id": id, "method": method}
    if params:
        body["params"] = params
    return httpx.post(MCP_URL, headers=HEADERS, json=body, timeout=15).json()

# Initialize
rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}})

# Stamp a workflow briefing hash
briefing = b"Agent Alpha: review Q2 compliance report for Acme GmbH"
sha256 = hashlib.sha256(briefing).hexdigest()

result = rpc("tools/call", {
    "name": "kavra_siegel_stamp_hash",
    "arguments": {"sha256_hex": sha256, "metadata": {"agent": "alpha", "task": "q2-review"}},
}, id=2)
print(result["result"]["content"][0]["text"])
# → Stempel erstellt: token_id=7c3a8b6e-..., is_qualified=True, verify_url=...
```

## Use Case 2: Verify Any Stamp

```python
# Verify a previously created stamp
token_id = "7c3a8b6e-..."  # from the stamp result

result = rpc("tools/call", {
    "name": "kavra_siegel_verify_token",
    "arguments": {"token_id": token_id},
}, id=3)
print(result["result"]["content"][0]["text"])
# → Verification: valid=True, tsp_provider=signius, is_qualified=True, reason=None
```

## Use Case 3: Workflow-Provenance Chain

Chain two stamps to prove a sequence of events:

```python
# Step 1: Stamp the briefing
briefing_hash = hashlib.sha256(b"Review contract #4711").hexdigest()
step1 = rpc("tools/call", {
    "name": "kavra_siegel_stamp_hash",
    "arguments": {"sha256_hex": briefing_hash, "metadata": {"step": "1-briefing"}},
}, id=10)
token1_text = step1["result"]["content"][0]["text"]
token1_id = token1_text.split("token_id=")[1].split(",")[0]

# Step 2: Stamp the output (includes reference to step 1)
output = f"Contract reviewed. Approved. Prior stamp: {token1_id}".encode()
output_hash = hashlib.sha256(output).hexdigest()
step2 = rpc("tools/call", {
    "name": "kavra_siegel_stamp_hash",
    "arguments": {"sha256_hex": output_hash, "metadata": {"step": "2-output", "prior_token": token1_id}},
}, id=11)
print("Chain complete:", step2["result"]["content"][0]["text"])

# Verify both stamps
for tid in [token1_id, step2["result"]["content"][0]["text"].split("token_id=")[1].split(",")[0]]:
    v = rpc("tools/call", {"name": "kavra_siegel_verify_token", "arguments": {"token_id": tid}}, id=20)
    print(f"  {tid[:8]}... → {v['result']['content'][0]['text']}")
```

## TypeScript Example

```typescript
const MCP_URL = "https://siegel.kavra.cloud/mcp";
const headers = {
  "X-Kavra-Service-Token": "your-token",
  "Content-Type": "application/json",
};

async function rpc(method: string, params?: any, id = 1) {
  const body: any = { jsonrpc: "2.0", id, method };
  if (params) body.params = params;
  const resp = await fetch(MCP_URL, { method: "POST", headers, body: JSON.stringify(body) });
  return resp.json();
}

// Stamp a hash
const content = new TextEncoder().encode("Audit completed 2026-06-03");
const hashBuffer = await crypto.subtle.digest("SHA-256", content);
const sha256 = Array.from(new Uint8Array(hashBuffer))
  .map((b) => b.toString(16).padStart(2, "0"))
  .join("");

const result = await rpc("tools/call", {
  name: "kavra_siegel_stamp_hash",
  arguments: { sha256_hex: sha256, tier: "basic" },
}, 2);
console.log("Stamp:", result.result.content[0].text);
```

## Full Example Script

See [`example_stamp.py`](./example_stamp.py) for a complete runnable end-to-end example.

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Kavra Siegel Documentation](https://siegel.kavra.cloud/docs)
- [Workflow Provenance Whitepaper](https://siegel.kavra.cloud/docs/whitepapers/workflow-provenance-art-50/)
- [Blog: Kavra Siegel Live](https://kavra.cloud/blog/kavra-siegel-live-qualifizierte-zeitstempel/)

## License

MIT
