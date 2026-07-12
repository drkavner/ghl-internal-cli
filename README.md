# GHL Internal CLI

A command-line interface for accessing GoHighLevel's internal APIs, built on top of the ghl-internal-cli MCP server.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/drkavner/ghl-internal-cli.git
   cd ghl-internal-cli
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   export GHL_API_KEY=pit-your-private-integration-token
   export GHL_LOCATION_ID=your-location-id
   ```

## Usage

Run the CLI directly:
```bash
python3 cli.py <command> [options]
```

Or make it executable:
```bash
chmod +x cli.py
./cli.py <command> [options]
```

### Available Commands

#### Agent Studio
- `agent-create` - Create a new AI agent
  - `--agentName` (required) - Agent name
  - `--agentPrompt` (required) - System prompt
  - `--welcomeMessage` (required) - Welcome message
  - `--locationId` (optional) - Location ID (uses GHL_LOCATION_ID if omitted)

- `agent-list` - List all AI agents
  - `--locationId` (optional) - Location ID
  - `--limit` (default: 100) - Number of results
  - `--offset` (default: 0) - Offset for pagination

- `agent-get` - Get a specific agent by ID
  - `--agentId` (required) - Agent ID
  - `--locationId` (optional) - Location ID

- `agent-execute` - Execute an AI agent
  - `--agentId` (required) - Agent ID
  - `--message` (required) - Message to send
  - `--locationId` (optional) - Location ID
  - `--executionId` (optional) - Session ID

#### Conversation AI (AskAI / AI Employees)
- `conv-create` - Create a Conversation AI agent
  - `--agentName` (required) - Agent name
  - `--agentRole` (required) - Agent role/purpose

- `conv-search` - Search Conversation AI agents
  - `--query` (required) - Search query
  - `--limit` (default: 100) - Maximum results

- `conv-get` - Get a Conversation AI agent by ID
  - `--agentId` (required) - Agent ID

- `conv-update` - Update a Conversation AI agent
  - `--agentId` (required) - Agent ID
  - `--agentName` (optional) - New agent name
  - `--agentStatus` (optional) - New status (e.g., active, paused)

- `conv-delete` - Delete a Conversation AI agent
  - `--agentId` (required) - Agent ID

#### Voice AI
- `voice-create` - Create a Voice AI agent
  - `--agentName` (required) - Agent name
  - `--agentPrompt` (required) - Agent prompt
  - `--welcomeMessage` (required) - Welcome message
  - `--voiceId` (required) - Voice ID
  - `--locationId` (optional) - Location ID

- `voice-list` - List Voice AI agents
  - `--locationId` (optional) - Location ID
  - `--page` (default: 1) - Page number
  - `--pageSize` (default: 20) - Page size

- `voice-get` - Get a Voice AI agent by ID
  - `--agentId` (required) - Agent ID
  - `--locationId` (optional) - Location ID

- `voice-delete` - Delete a Voice AI agent
  - `--agentId` (required) - Agent ID
  - `--locationId` (optional) - Location ID

- `voice-logs` - Get Voice AI call logs
  - `--agentId` (required) - Agent ID
  - `--locationId` (optional) - Location ID
  - `--page` (default: 1) - Page number
  - `--pageSize` (default: 20) - Page size

#### Knowledge Base
- `kb-list` - List knowledge bases
  - `--locationId` (optional) - Location ID

- `kb-create` - Create a knowledge base
  - `--name` (required) - Knowledge base name
  - `--locationId` (optional) - Location ID

- `kb-discover` - Discover website pages for training
  - `--knowledgeBaseId` (required) - Knowledge base ID
  - `--locationId` (optional) - Location ID
  - `--url` (required) - URL to scan

- `kb-train` - Train on discovered URLs
  - `--knowledgeBaseId` (required) - Knowledge base ID
  - `--locationId` (optional) - Location ID
  - `--urls` (required, space-separated) - URLs to train on

#### Vibe AI
- `vibe-chat` - Get chat messages from a Vibe AI project
  - `--projectId` (required) - Project ID
  - `--limit` (default: 100) - Maximum messages
  - `--offset` (default: 0) - Offset for pagination

- `vibe-sandbox` - Keep Vibe AI sandbox alive
  - `--projectId` (required) - Project ID

#### Funnels
- `funnel-create` - Create a funnel
  - `--name` (required) - Funnel name
  - `--description` (optional) - Funnel description

- `funnel-step` - Create a funnel step
  - `--funnelId` (required) - Funnel ID
  - `--stepName` (required) - Step name
  - `--stepType` (required) - Step type
  - `--stepConfig` (optional) - Step configuration (JSON string)

- `funnel-geo` - Set geo-location targeting for a funnel
  - `--funnelId` (required) - Funnel ID
  - `--latitude` (required) - Latitude
  - `--longitude` (required) - Longitude
  - `--radius` (required) - Radius in meters

#### Feature Flags
- `feature-flags` - Get feature flags for a location
  - `--locationId` (optional) - Location ID

#### Facebook Integration
- `fb-connection` - Get Facebook connection for a location
  - `--locationId` (optional) - Location ID

- `fb-pages` - Get linked Facebook pages for a location
  - `--locationId` (optional) - Location ID

#### Chat Widget
- `chat-widget` - Get chat widget settings
  - `--locationId` (optional) - Location ID

#### WhatsApp Phone Numbers
- `whatsapp` - Get WhatsApp phone numbers for a location
  - `--locationId` (optional) - Location ID

#### Forms
- `forms` - Get forms
  - No arguments required

#### Custom Values
- `custom-values` - Get custom values for a location
  - `--locationId` (optional) - Location ID

#### Payments Currency
- `payments-currency` - Get payment currencies
  - No arguments required

#### Social Media Accounts
- `social-media` - Get social media accounts for a location
  - `--locationId` (optional) - Location ID

#### Templates
- `templates` - Get list of templates
  - No arguments required

## Examples

```bash
# Create an AI agent
python3 cli.py agent-create --agentName "Support Bot" --agentPrompt "You are a helpful support agent." --welcomeMessage "Hello! How can I help you today?"

# List Voice AI agents
python3 cli.py voice-list

# Get chat messages from a Vibe AI project
python3 cli.py vibe-chat --projectId "your-project-id-here"

# Create a funnel
python3 cli.py funnel-create --name "Sales Funnel" --description "Funnel for converting leads to customers"

# Create a funnel step
python3 cli.py funnel-step --funnelId "your-funnel-id" --stepName "Email Sequence" --stepType "email" --stepConfig '{"emailTemplateId": "abc123"}'

# Set geo-location for a funnel
python3 cli.py funnel-geo --funnelId "your-funnel-id" --latitude 40.7128 --longitude -74.0060 --radius 10000

# Get feature flags
python3 cli.py feature-flags

# Get Facebook connection
python3 cli.py fb-connection

# Get WhatsApp phone numbers
python3 cli.py whatsapp

# Get forms
python3 cli.py forms

# Get custom values
python3 cli.py custom-values

# Get payment currencies
python3 cli.py payments-currency

# Get social media accounts
python3 cli.py social-media

# Get templates
python3 cli.py templates
```

## Notes

- All commands that require a location ID will use the `GHL_LOCATION_ID` environment variable if not explicitly provided.
- For commands that accept JSON (like `--stepConfig`), pass a valid JSON string.
- The CLI outputs JSON responses directly to stdout for easy processing with tools like `jq`.

## Error Handling

The CLI will exit with code 1 and print an error message to stderr if:
- Required arguments are missing
- The API returns an error (non-2xx status code)
- An unexpected exception occurs

## Integration with Hermes Agent

This CLI shares the same underlying API logic as the MCP server (`server.py`). For use with Hermes Agent, prefer the MCP server integration as it provides native tool discovery and invocation capabilities.

## License

MIT