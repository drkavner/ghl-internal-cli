# GHL Internal API CLI / Skill

This repository provides access to GoHighLevel's **internal** v2 API endpoints that are not exposed in the public REST API. It can be used in two ways:

1. **As a Hermes MCP skill** – integrate with Hermes Agent (or any MCP-compatible host) to let Claude Code or another AI agent call GHL functions naturally.
2. **As a standalone CLI** – invoke commands directly from a terminal to perform GHL operations (useful for scripting or quick ad‑hoc tasks).

## Features

- **Agent Studio** – create, list, get, execute, update, and promote AI agents.
- **Conversation AI (AskAI / AI Employees)** – create, search, get, update, delete agents.
- **Voice AI** – create, list, get, delete agents and retrieve call logs.
- **Knowledge Base** – list, create, discover website content, train on discovered URLs.

All endpoints are the same internal ones used by the GHL dashboard (`https://services.leadconnectorhq.com`).

## Prerequisites

- A GoHighLevel **Private Integration Token (PIT)** with sufficient permissions.
- Your GoHighLevel **Location ID**.
- Node.js ≥ 16 (for the TypeScript/Node version) **or** Python ≥ 3.8 (for the Python version).
- (Optional) Git – to push this repo to your own GitHub account.

## Installation

Choose either the Node/TypeScript version or the Python version; both provide identical functionality.

### Option A: Node/TypeScript (recommended for TypeScript fans)

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/ghl-internal-cli.git
cd ghl-internal-cli

# 2. Install dependencies
npm ci

# 3. Build the TypeScript source
npm run build   # compiles src/ → dist/
```

### Option B: Python

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/ghl-internal-cli.git
cd ghl-internal-cli

# 2. Install dependencies
pip install -r requirements.txt   # mcp, httpx
```

## Configuration

Create a `.env` file in the repo root (or export the variables in your shell) with:

```dotenv
GHL_API_KEY=pit-<your-private-integration-token>
GHL_LOCATION_ID=<your-location-id>
```

The CLI and MCP server will automatically strip the `pit-` prefix if present.

## Usage as Hermes MCP Skill

1. Copy the desired implementation into your Hermes profile's `skill-mcp` directory:

   - **Node version**: copy the entire `ghl-internal-cli` folder to `~/.hermes/profiles/iris/skill-mcp/ghl-internal`.
   - **Python version**: copy `server.py` and `requirements.txt` to `~/.hermes/profiles/iris/skill-mcp/ghl-internal-py` (or any name).

2. Add an entry to `~/.hermes/config.yaml` under `mcp_servers`:

   ```yaml
   mcp_servers:
     ghl-internal:
       # ----- Node version -----
       command: "node"
       args: ["~/.hermes/profiles/iris/skill-mcp/ghl-internal/dist/index.js"]
       env:
         GHL_API_KEY: "pit-<your-private-integration-token>"
         GHL_LOCATION_ID: "<your-location-id>"
       # ----- Python version (uncomment to use) -----
       # command: "python3"
       # args: ["~/.hermes/profiles/iris/skill-mcp/ghl-internal-py/server.py"]
       # env:
       #   GHL_API_KEY: "pit-<your-private-integration-token>"
       #   GHL_LOCATION_ID: "<your-location-id>"
   ```

3. Restart Hermes (or reload the MCP servers). You can now ask Claude Code / Hermes to:

   - “Create a new AI agent called ‘Support Helper’ in Agent Studio.”
   - “List all my Voice AI agents.”
   - “Create a knowledge base for my website content.”
   - “Execute my AI agent with the message ‘Hello, how can I help you today?’”

## Usage as Standalone CLI

The repo includes a simple command‑line interface (`cli.py`) that wraps the same internal API calls.

```bash
# Make sure .env is sourced or variables are exported
export GHL_API_KEY=pit-...
export GHL_LOCATION_ID=...

# Examples
python cli.py agent create --name "Support Helper" --prompt "You are a helpful support bot." --welcomeMessage "Hi! How can I assist?"
python cli.py agent list
python cli.py voice create --name "Inbound Voice Bot" --prompt "Answer calls politely." --welcomeMessage "Thanks for calling!"
python cli.py voice list
python cli.py kb create --name "Website FAQ"
python cli.py kb discover --knowledgeBaseId <kb-id> --url https://example.com/faq
python cli.py kb train --knowledgeBaseId <kb-id> --urls '["https://example.com/faq","https://example.com/about"]'
```

Run `python cli.py --help` for the full list of subcommands and options.

## Architecture

- **`server.py`** – Python implementation of an MCP server (stdio transport). Hermes (or any MCP host) connects to it via standard input/output.
- **`src/index.ts`** – TypeScript implementation of an MCP server (uses `@modelcontextprotocol/sdk`). Compiled to `dist/index.js`.
- **`cli.py`** – Simple Python CLI that directly calls the same internal API functions (does not require MCP). Useful for quick scripting or CI pipelines.
- **Shared logic** – Both the MCP server and the CLI use the same low‑level `call_ghl_api` helper (Python) or `ghl.request` helper (Node) to talk to `https://services.leadconnectorhq.com`.

## Extending / Adding New Endpoints

If you discover additional internal GHL endpoints (e.g., for a future “Vibe Coder” AIStudio feature), you can add them by:

1. Adding a new **Tool** definition to the appropriate list (`TOOLS` in Python or `tools` array in TypeScript).
2. Implementing the handler in the `handle_call_tool` / request handler, calling the existing low‑level request helper with the observed path, method, and payload.
3. Re‑building (Node) or restarting (Python) the server.

Because the MCP server exposes a standard `tools/list` endpoint, any MCP‑compatible host (including Hermes Agent, Claude Code with MCP support, or other agents) will automatically discover the new tools without further configuration.

## License

MIT – feel free to fork, modify, and distribute.

## Acknowledgements

Built upon the GHL API exploration performed with Hermes Agent. Inspired by the official `@gohighlevel/api-client` package and the Model Context Protocol specification.