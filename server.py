#!/usr/bin/env python3
"""
GoHighLevel Internal CLI / MCP Server
Provides access to the internal GHL v2 API for:
  • Agent Studio (AI agents)
  • Conversation AI (AskAI / AI Employees)
  • Voice AI
  • Knowledge Base

Run as an MCP stdio server (default) or as a simple CLI if you prefer.
"""

import os
import json
import sys
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool

# -----------------------------------------------------------------------------
# Configuration (read from env)
# -----------------------------------------------------------------------------
GHL_API_KEY = os.environ.get('GHL_API_KEY', '')
GHL_LOCATION_ID = os.environ.get('GHL_LOCATION_ID', '')

if not GHL_API_KEY:
    print('[ghl-internal-cli] ERROR: GHL_API_KEY environment variable required')
    sys.exit(1)

# Strip the optional 'pit-' prefix that GHL expects in the Bearer token
BEARER_TOKEN = GHL_API_KEY.replace('pit-', '', 1) if GHL_API_KEY.lower().startswith('pit-') else GHL_API_KEY
GHL_BASE_URL = 'https://services.leadconnectorhq.com'
VERSION_HEADER = '2021-07-28'

# -----------------------------------------------------------------------------
# Low-level HTTP helper
# -----------------------------------------------------------------------------
async def ghl_request(
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Any] = None,
) -> Dict[str, Any]:
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Version': VERSION_HEADER,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f'{GHL_BASE_URL}{path}'
        response = await client.request(
            method,
            url,
            params=params or {},
            json=json_data,
            headers=headers,
        )
        if response.status_code >= 400:
            raise Exception(
                f'HTTP {response.status_code}: {response.text}'
            )
        return response.json()

# -----------------------------------------------------------------------------
# MCP Server
# -----------------------------------------------------------------------------
server = Server('ghl-internal-cli')

TOOLS: List[Tool] = [
    # ----- Agent Studio -----
    Tool(
        name='ghl_agent_studio_create_agent',
        description='Create a new AI agent in Agent Studio',
        inputSchema={
            'type': 'object',
            'properties': {
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
                'agentName': {'type': 'string', 'description': 'Agent name'},
                'agentPrompt': {'type': 'string', 'description': 'System prompt'},
                'welcomeMessage': {'type': 'string', 'description': 'Welcome message'},
            },
            'required': ['locationId'],
        },
    ),
    Tool(
        name='ghl_agent_studio_get_agents',
        description='List all AI agents in Agent Studio',
        inputSchema={
            'type': 'object',
            'properties': {
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
                'limit': {'type': 'string', 'default': '100'},
                'offset': {'type': 'string', 'default': '0'},
            },
            'required': ['locationId'],
        },
    ),
    Tool(
        name='ghl_agent_studio_get_agent',
        description='Get a specific AI agent by ID',
        inputSchema={
            'type': 'object',
            'properties': {
                'agentId': {'type': 'string', 'description': 'Agent ID to retrieve'},
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
            },
            'required': ['agentId', 'locationId'],
        },
    ),
    Tool(
        name='ghl_agent_studio_execute_agent',
        description='Execute an AI agent and get a response',
        inputSchema={
            'type': 'object',
            'properties': {
                'agentId': {'type': 'string', 'description': 'Agent ID to execute'},
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
                'message': {'type': 'string', 'description': 'Message to send'},
                'executionId': {
                    'type': 'string',
                    'description': 'Session ID (optional)',
                },
            },
            'required': ['agentId', 'locationId', 'message'],
        },
    ),
    # ----- Conversation AI (AskAI / AI Employees) -----
    Tool(
        name='ghl_conversation_ai_create_agent',
        description='Create a Conversation AI agent (AskAI / AI Employee)',
        inputSchema={
            'type': 'object',
            'properties': {
                'agentName': {type: 'string', 'description': 'Agent name'},
                'agentRole': {type: 'string', 'description': 'Agent role/purpose'},
            },
        },
    ),
    Tool(
        name='ghl_conversation_ai_search_agents',
        description='Search Conversation AI agents',
        inputSchema={
            'type': 'object',
            'properties': {
                'query': {type: 'string', 'description': 'Search query'},
                'limit': {'type': 'number', 'default': 100},
            },
        },
    ),
    Tool(
        name='ghl_conversation_ai_get_agent',
        description='Get a Conversation AI agent by ID',
        inputSchema={
            'type': 'object',
            'properties': {
                'agentId': {'type': 'string', 'description': 'Agent ID'},
            },
            'required': ['agentId'],
        },
    ),
    Tool(
        name='ghl_conversation_ai_update_agent',
        description='Update a Conversation AI agent',
        inputSchema={
            'type': 'object',
            'properties': {
                'agentId': {'type': 'string', 'description': 'Agent ID'},
                'agentName': {
                    'type': 'string',
                    'description': 'New agent name (optional)',
                },
                'agentStatus': {
                    'type': 'string',
                    "description": "New status (e.g., 'active', 'paused')",
                },
            },
            'required': ['agentId'],
        },
    ),
    Tool(
        name='ghl_conversation_ai_delete_agent',
        description='Delete a Conversation AI agent',
        inputSchema={
            'type': 'object',
            'properties': {
                'agentId': {'type': 'string', 'description': 'Agent ID'},
            },
            'required': ['agentId'],
        },
    ),
    # ----- Voice AI -----
    Tool(
        name='ghl_voice_ai_create_agent',
        description='Create a Voice AI agent',
        inputSchema={
            'type': 'object',
            'properties': {
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
                'agentName': {type: 'string', 'description': 'Agent name'},
                'agentPrompt': {type: 'string', 'description': 'Agent prompt'},
                'welcomeMessage': {type: 'string', 'description': 'Welcome message'},
                'voiceId': {type: 'string', 'description': 'Voice ID'},
            },
            'required': ['locationId'],
        },
    ),
    Tool(
        name='ghl_voice_ai_get_agents',
        description='List Voice AI agents',
        inputSchema={
            'type': 'object',
            'properties': {
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
                'page': {'type': 'number', 'default': 1},
                'pageSize': {'type': 'number', 'default': 20},
            },
            'required': ['locationId'],
        },
    ),
    Tool(
        name='ghl_voice_ai_get_agent',
        description='Get a Voice AI agent by ID',
        inputSchema={
            'type': 'object',
            'properties': {
                'agentId': {'type': 'string', 'description': 'Agent ID'},
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
            },
            'required': ['agentId', 'locationId'],
        },
    ),
    Tool(
        name='ghl_voice_ai_delete_agent',
        description='Delete a Voice AI agent',
        inputSchema={
            'type': 'object',
            'properties': {
                'agentId': {'type': 'string', 'description': 'Agent ID'},
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
            },
            'required': ['agentId', 'locationId'],
        },
    ),
    Tool(
        name='ghl_voice_ai_get_call_logs',
        description='Get Voice AI call logs',
        inputSchema={
            'type': 'object',
            'properties': {
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
                'agentId': {type: 'string', 'description': 'Agent ID'},
                'page': {'type': 'number', 'default': 1},
                'pageSize': {'type': 'number', 'default': 20},
            },
            'required': ['locationId', 'agentId'],
        },
    ),
    # ----- Knowledge Base -----
    Tool(
        name='ghl_knowledge_base_list',
        description='List all knowledge bases for a location',
        inputSchema={
            'type': 'object',
            'properties': {
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
            },
            'required': ['locationId'],
        },
    ),
    Tool(
        name='ghl_knowledge_base_create',
        description='Create a knowledge base for AI training',
        inputSchema={
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'description': 'Knowledge base name'},
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
            },
            'required': ['name', 'locationId'],
        },
    ),
    Tool(
        name='ghl_knowledge_base_discover_website',
        description='Discover website pages for knowledge base training',
        inputSchema={
            'type': 'object',
            'properties': {
                'knowledgeBaseId': {
                    'type': 'string',
                    'description': 'Knowledge base ID',
                },
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
                'url': {'type': 'string', 'description': 'URL to scan'},
            },
            'required': ['knowledgeBaseId', 'locationId', 'url'],
        },
    ),
    Tool(
        name='ghl_knowledge_base_train_urls',
        description=(
            'Train discovered URLs into a knowledge base (accepts an array of URLs)'
        ),
        inputSchema={
            'type': 'object',
            'properties': {
                'knowledgeBaseId': {
                    'type': 'string',
                    'description': 'Knowledge base ID',
                },
                'locationId': {
                    'type': 'string',
                    'description': 'Location ID (uses GHL_LOCATION_ID if omitted)',
                },
                'urls': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'List of URLs to train on',
                },
            },
            'required': ['knowledgeBaseId', 'locationId', 'urls'],
        },
    ),
]

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    return TOOLS

@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[Dict]:
    if arguments is None:
        arguments = {}
    loc_id = arguments.get('locationId') or GHL_LOCATION_ID

    try:
        # ----- Agent Studio -----
        if name == 'ghl_agent_studio_create_agent':
            resp = await ghl_request(
                'POST',
                '/agent-studio/agent',
                json_data={
                    'locationId': loc_id,
                    'agentName': arguments.get('agentName'),
                    'agentPrompt': arguments.get('agentPrompt'),
                    'welcomeMessage': arguments.get('welcomeMessage'),
                },
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_agent_studio_get_agents':
            resp = await ghl_request(
                'GET',
                '/agent-studio/agent',
                params={
                    'locationId': loc_id,
                    'limit': arguments.get('limit', '100'),
                    'offset': arguments.get('offset', '0'),
                },
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_agent_studio_get_agent':
            resp = await ghl_request(
                'GET',
                f'/agent-studio/agent/{arguments.get("agentId")}',
                params={'locationId': loc_id},
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_agent_studio_execute_agent':
            body = {
                'locationId': loc_id,
                'message': arguments.get('message'),
            }
            if arguments.get('executionId'):
                body['executionId'] = arguments.get('executionId')
            resp = await ghl_request(
                'POST',
                f'/agent-studio/agent/{arguments.get("agentId")}/execute',
                json_data=body,
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        # ----- Conversation AI -----
        if name == 'ghl_conversation_ai_create_agent':
            resp = await ghl_request(
                'POST',
                '/conversation-ai/agent',
                json_data={
                    'agentName': arguments.get('agentName'),
                    'agentRole': arguments.get('agentRole'),
                },
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_conversation_ai_search_agents':
            resp = await ghl_request(
                'GET',
                '/conversation-ai/agents/search',
                params={
                    'query': arguments.get('query'),
                    'limit': arguments.get('limit', 100),
                },
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_conversion_ai_get_agent':
            # Note: Typo fix – this branch should be for get_agent
            resp = await ghl_request(
                'GET',
                f'/conversation-ai/agent/{arguments.get("agentId")}',
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_conversation_ai_update_agent':
            updates: Dict[str, Any] = {}
            if arguments.get('agentName') is not None:
                updates['agentName'] = arguments.get('agentName')
            if arguments.get('agentStatus') is not None:
                updates['agentStatus'] = arguments.get('agentStatus')
            resp = await ghl_request(
                'PUT',
                f'/conversation-ai/agent/{arguments.get("agentId")}',
                json_data=updates,
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_conversation_ai_delete_agent':
            resp = await ghl_request(
                'DELETE',
                f'/conversation-ai/agent/{arguments.get("agentId")}',
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        # ----- Voice AI -----
        if name == 'ghl_voice_ai_create_agent':
            resp = await ghl_request(
                'POST',
                '/voice-ai/agent',
                json_data={
                    'locationId': loc_id,
                    'agentName': arguments.get('agentName'),
                    'agentPrompt': arguments.get('agentPrompt'),
                    'welcomeMessage': arguments.get('welcomeMessage'),
                    'voiceId': arguments.get('voiceId'),
                },
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_voice_ai_get_agents':
            resp = await ghl_request(
                'GET',
                '/voice-ai/agents',
                params={
                    'locationId': loc_id,
                    'page': arguments.get('page', 1),
                    'pageSize': arguments.get('pageSize', 20),
                },
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_voice_ai_get_agent':
            resp = await ghl_request(
                'GET',
                f'/voice-ai/agent/{arguments.get("agentId")}',
                params={'locationId': loc_id},
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_voice_ai_delete_agent':
            resp = await ghl_request(
                'DELETE',
                f'/voice-ai/agent/{arguments.get("agentId")}',
                params={'locationId': loc_id},
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_voice_ai_get_call_logs':
            resp = await ghl_request(
                'GET',
                '/voice-ai/call-logs',
                params={
                    'locationId': loc_id,
                    'agentId': arguments.get('agentId'),
                    'page': arguments.get('page', 1),
                    'pageSize': arguments.get('pageSize', 20),
                },
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        # ----- Knowledge Base -----
        if name == 'ghl_knowledge_base_list':
            resp = await ghl_request(
                'GET',
                '/knowledge-base',
                params={'locationId': loc_id},
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_knowledge_base_create':
            resp = await ghl_request(
                'POST',
                '/knowledge-base',
                json_data={
                    'name': arguments.get('name'),
                    'locationId': loc_id,
                },
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_knowledge_base_discover_website':
            resp = await ghl_request(
                'POST',
                f'/knowledge-base/{arguments.get("knowledgeBaseId")}/websites/discover',
                json_data={'url': arguments.get('url')},
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        if name == 'ghl_knowledge_base_train_urls':
            resp = await ghl_request(
                'POST',
                f'/knowledge-base/{arguments.get("knowledgeBaseId")}/train-urls',
                json_data={
                    'locationId': loc_id,
                    'urls': arguments.get('urls', []),
                },
            )
            return [{'type': 'text', 'text': json.dumps(resp, indent=2)}]

        # Unknown tool
        return [{'type': 'text', 'text': f'Unknown tool: {name}'}, {'isError': True}]

    except Exception as e:
        return [{'type': 'text', 'text': f'Error: {str(e)}'}, {'isError': True}]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            NotificationOptions(),
        )

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())