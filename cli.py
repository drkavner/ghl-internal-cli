#!/usr/bin/env python3
"""
Simple CLI wrapper for GoHighLevel internal API.
Provides command-line access to the same endpoints as the MCP server.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

import httpx

# -----------------------------------------------------------------------------
# Configuration (read from env)
# -----------------------------------------------------------------------------
GHL_API_KEY = os.environ.get('GHL_API_KEY', '')
GHL_LOCATION_ID = os.environ.get('GHL_LOCATION_ID', '')

if not GHL_API_KEY:
    print('ERROR: GHL_API_KEY environment variable required', file=sys.stderr)
    sys.exit(1)

# Strip the optional 'pit-' prefix that GHL expects in the Bearer token
BEARER_TOKEN = GHL_API_KEY.replace('pit-', '', 1) if GHL_API_KEY.lower().startswith('pit-') else GHL_API_KEY
GHL_BASE_URL = 'https://services.leadconnectorhq.com'
VERSION_HEADER = '2021-07-28'


def ghl_request(method: str, path: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Any] = None) -> Dict[str, Any]:
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Version': VERSION_HEADER,
    }
    # For simplicity, use synchronous client; for production you might want async.
    with httpx.Client(timeout=30.0) as client:
        url = f'{GHL_BASE_URL}{path}'
        response = client.request(method, url, params=params or {}, json=json_data, headers=headers)
        if response.status_code >= 400:
            raise Exception(f'HTTP {response.status_code}: {response.text}')
        return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description='GHL Internal API CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # ----- Agent Studio -----
    parser_agent_create = subparsers.add_parser('agent-create', help='Create a new AI agent in Agent Studio')
    parser_agent_create.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_agent_create.add_argument('--agentName', required=True, help='Agent name')
    parser_agent_create.add_argument('--agentPrompt', required=True, help='System prompt')
    parser_agent_create.add_argument('--welcomeMessage', required=True, help='Welcome message')

    parser_agent_list = subparsers.add_parser('agent-list', help='List all AI agents in Agent Studio')
    parser_agent_list.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_agent_list.add_argument('--limit', default='100', help='Limit (default 100)')
    parser_agent_list.add_argument('--offset', default='0', help='Offset (default 0)')

    parser_agent_get = subparsers.add_parser('agent-get', help='Get a specific AI agent by ID')
    parser_agent_get.add_argument('--agentId', required=True, help='Agent ID')
    parser_agent_get.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_agent_execute = subparsers.add_parser('agent-execute', help='Execute an AI agent and get a response')
    parser_agent_execute.add_argument('--agentId', required=True, help='Agent ID to execute')
    parser_agent_execute.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_agent_execute.add_argument('--message', required=True, help='Message to send')
    parser_agent_execute.add_argument('--executionId', required=False, help='Session ID (optional)')

    # ----- Conversation AI (AskAI / AI Employees) -----
    parser_conv_create = subparsers.add_parser('conv-create', help='Create a Conversation AI agent (AskAI / AI Employee)')
    parser_conv_create.add_argument('--agentName', required=True, help='Agent name')
    parser_conv_create.add_argument('--agentRole', required=True, help='Agent role/purpose')

    parser_conv_search = subparsers.add_parser('conv-search', help='Search Conversation AI agents')
    parser_conv_search.add_argument('--query', required=True, help='Search query')
    parser_conv_search.add_argument('--limit', default='100', help='Limit (default 100)')

    parser_conv_get = subparsers.add_parser('conv-get', help='Get a Conversation AI agent by ID')
    parser_conv_get.add_argument('--agentId', required=True, help='Agent ID')

    parser_conv_update = subparsers.add_parser('conv-update', help='Update a Conversation AI agent')
    parser_conv_update.add_argument('--agentId', required=True, help='Agent ID')
    parser_conv_update.add_argument('--agentName', required=False, help='New agent name (optional)')
    parser_conv_update.add_argument('--agentStatus', required=False, help='New status (e.g., active, paused)')

    parser_conv_delete = subparsers.add_parser('conv-delete', help='Delete a Conversation AI agent')
    parser_conv_delete.add_argument('--agentId', required=True, help='Agent ID')

    # ----- Voice AI -----
    parser_voice_create = subparsers.add_parser('voice-create', help='Create a Voice AI agent')
    parser_voice_create.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_voice_create.add_argument('--agentName', required=True, help='Agent name')
    parser_voice_create.add_argument('--agentPrompt', required=True, help='Agent prompt')
    parser_voice_create.add_argument('--welcomeMessage', required=True, help='Welcome message')
    parser_voice_create.add_argument('--voiceId', required=True, help='Voice ID')

    parser_voice_list = subparsers.add_parser('voice-list', help='List Voice AI agents')
    parser_voice_list.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_voice_list.add_argument('--page', default='1', help='Page (default 1)')
    parser_voice_list.add_argument('--pageSize', default='20', help='Page size (default 20)')

    parser_voice_get = subparsers.add_parser('voice-get', help='Get a Voice AI agent by ID')
    parser_voice_get.add_argument('--agentId', required=True, help='Agent ID')
    parser_voice_get.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_voice_delete = subparsers.add_parser('voice-delete', help='Delete a Voice AI agent')
    parser_voice_delete.add_argument('--agentId', required=True, help='Agent ID')
    parser_voice_delete.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_voice_logs = subparsers.add_parser('voice-logs', help='Get Voice AI call logs')
    parser_voice_logs.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_voice_logs.add_argument('--agentId', required=True, help='Agent ID')
    parser_voice_logs.add_argument('--page', default='1', help='Page (default 1)')
    parser_voice_logs.add_argument('--pageSize', default='20', help='Page size (default 20)')

    # ----- Knowledge Base -----
    parser_kb_list = subparsers.add_parser('kb-list', help='List all knowledge bases for a location')
    parser_kb_list.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_kb_create = subparsers.add_parser('kb-create', help='Create a knowledge base for AI training')
    parser_kb_create.add_argument('--name', required=True, help='Knowledge base name')
    parser_kb_create.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_kb_discover = subparsers.add_parser('kb-discover', help='Discover website pages for knowledge base training')
    parser_kb_discover.add_argument('--knowledgeBaseId', required=True, help='Knowledge base ID')
    parser_kb_discover.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_kb_discover.add_argument('--url', required=True, help='URL to scan')

    parser_kb_train = subparsers.add_parser('kb-train', help='Train discovered URLs into a knowledge base')
    parser_kb_train.add_argument('--knowledgeBaseId', required=True, help='Knowledge base ID')
    parser_kb_train.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_kb_train.add_argument('--urls', required=True, nargs='+', help='List of URLs to train on (space-separated)')

    # ----- Vibe AI -----
    parser_vibe_chat = subparsers.add_parser('vibe-chat', help='Get chat messages from a Vibe AI project')
    parser_vibe_chat.add_argument('--projectId', required=True, help='Vibe AI project ID')
    parser_vibe_chat.add_argument('--limit', default='100', help='Limit (default 100)')
    parser_vibe_chat.add_argument('--offset', default='0', help='Offset (default 0)')

    parser_vibe_sandbox = subparsers.add_parser('vibe-sandbox', help='Keep Vibe AI sandbox alive')
    parser_vibe_sandbox.add_argument('--projectId', required=True, help='Vibe AI project ID')

    # ----- Funnels -----
    parser_funnel_create = subparsers.add_parser('funnel-create', help='Create a funnel')
    parser_funnel_create.add_argument('--name', required=True, help='Funnel name')
    parser_funnel_create.add_argument('--description', required=False, help='Funnel description (optional)')

    parser_funnel_step = subparsers.add_parser('funnel-step', help='Create a funnel step')
    parser_funnel_step.add_argument('--funnelId', required=True, help='Funnel ID')
    parser_funnel_step.add_argument('--stepName', required=True, help='Step name')
    parser_funnel_step.add_argument('--stepType', required=True, help='Step type')
    parser_funnel_step.add_argument('--stepConfig', required=False, help='Step configuration (JSON string)')

    parser_funnel_geo = subparsers.add_parser('funnel-geo', help='Set geo-location targeting for a funnel')
    parser_funnel_geo.add_argument('--funnelId', required=True, help='Funnel ID')
    parser_funnel_geo.add_argument('--latitude', required=True, type=float, help='Latitude')
    parser_funnel_geo.add_argument('--longitude', required=True, type=float, help='Longitude')
    parser_funnel_geo.add_argument('--radius', required=True, type=float, help='Radius in meters')

    # ----- Feature Flags -----
    parser_feature_flags = subparsers.add_parser('feature-flags', help='Get feature flags for a location')
    parser_feature_flags.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    # ----- Facebook Integration -----
    parser_fb_conn = subparsers.add_parser('fb-connection', help='Get Facebook connection for a location')
    parser_fb_conn.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_fb_pages = subparsers.add_parser('fb-pages', help='Get linked Facebook pages for a location')
    parser_fb_pages.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    # ----- Chat Widget -----
    parser_chat_widget = subparsers.add_parser('chat-widget', help='Get chat widget settings')
    parser_chat_widget.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    # ----- WhatsApp Phone Numbers -----
    parser_whatsapp = subparsers.add_parser('whatsapp', help='Get WhatsApp phone numbers for a location')
    parser_whatsapp.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    # ----- Forms -----
    parser_forms = subparsers.add_parser('forms', help='Get forms')

    # ----- Custom Values -----
    parser_custom = subparsers.add_parser('custom-values', help='Get custom values for a location')
    parser_custom.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    # ----- Payments Currency -----
    parser_payments = subparsers.add_parser('payments-currency', help='Get payment currencies')

    # ----- Social Media Accounts -----
    parser_social = subparsers.add_parser('social-media', help='Get social media accounts for a location')
    parser_social.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    # ----- Templates -----
    parser_templates = subparsers.add_parser('templates', help='Get list of templates')

    # ----- Pipelines -----
    parser_pipelines = subparsers.add_parser('pipelines', help='Get all pipelines for a location')
    parser_pipelines.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_pipeline_create = subparsers.add_parser('pipeline-create', help='Create a pipeline')
    parser_pipeline_create.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_pipeline_create.add_argument('--name', required=True, help='Pipeline name')
    parser_pipeline_create.add_argument('--description', required=False, help='Pipeline description (optional)')

    parser_pipeline_get = subparsers.add_parser('pipeline-get', help='Get a specific pipeline by ID')
    parser_pipeline_get.add_argument('--pipelineId', required=True, help='Pipeline ID')
    parser_pipeline_get.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_pipeline_update = subparsers.add_parser('pipeline-update', help='Update a pipeline')
    parser_pipeline_update.add_argument('--pipelineId', required=True, help='Pipeline ID')
    parser_pipeline_update.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_pipeline_update.add_argument('--name', required=False, help='Pipeline name (optional)')
    parser_pipeline_update.add_argument('--description', required=False, help='Pipeline description (optional)')

    parser_pipeline_delete = subparsers.add_parser('pipeline-delete', help='Delete a pipeline')
    parser_pipeline_delete.add_argument('--pipelineId', required=True, help='Pipeline ID')
    parser_pipeline_delete.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_pipeline_stages = subparsers.add_parser('pipeline-stages', help='Get all stages for a pipeline')
    parser_pipeline_stages.add_argument('--pipelineId', required=True, help='Pipeline ID')
    parser_pipeline_stages.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_pipeline_stage_create = subparsers.add_parser('pipeline-stage-create', help='Create a stage in a pipeline')
    parser_pipeline_stage_create.add_argument('--pipelineId', required=True, help='Pipeline ID')
    parser_pipeline_stage_create.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_pipeline_stage_create.add_argument('--stageName', required=True, help='Stage name')
    parser_pipeline_stage_create.add_argument('--stageType', required=True, help='Stage type (e.g., open, won, lost)')
    parser_pipeline_stage_create.add_argument('--sort', required=False, type=int, help='Sort order (optional)')

    parser_pipeline_stage_update = subparsers.add_parser('pipeline-stage-update', help='Update a pipeline stage')
    parser_pipeline_stage_update.add_argument('--pipelineId', required=True, help='Pipeline ID')
    parser_pipeline_stage_update.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_pipeline_stage_update.add_argument('--stageId', required=True, help='Stage ID')
    parser_pipeline_stage_update.add_argument('--stageName', required=False, help='Stage name (optional)')
    parser_pipeline_stage_update.add_argument('--stageType', required=False, help='Stage type (optional)')
    parser_pipeline_stage_update.add_argument('--sort', required=False, type=int, help='Sort order (optional)')

    parser_pipeline_stage_delete = subparsers.add_parser('pipeline-stage-delete', help='Delete a pipeline stage')
    parser_pipeline_stage_delete.add_argument('--pipelineId', required=True, help='Pipeline ID')
    parser_pipeline_stage_delete.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_pipeline_stage_delete.add_argument('--stageId', required=True, help='Stage ID')

    # ----- Opportunities -----
    parser_opportunities = subparsers.add_parser('opportunities', help='Get all opportunities for a location')
    parser_opportunities.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_opportunities.add_argument('--pipelineId', required=False, help='Filter by pipeline ID (optional)')
    parser_opportunities.add_argument('--stageId', required=False, help='Filter by stage ID (optional)')
    parser_opportunities.add_argument('--limit', default='100', help='Limit (default 100)')
    parser_opportunities.add_argument('--offset', default='0', help='Offset (default 0)')

    parser_opportunity_create = subparsers.add_parser('opportunity-create', help='Create an opportunity')
    parser_opportunity_create.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_opportunity_create.add_argument('--pipelineId', required=True, help='Pipeline ID')
    parser_opportunity_create.add_argument('--stageId', required=True, help='Stage ID')
    parser_opportunity_create.add_argument('--contactId', required=False, help='Contact ID (optional)')
    parser_opportunity_create.add_argument('--title', required=True, help='Opportunity title')
    parser_opportunity_create.add_argument('--value', required=False, type=float, help='Opportunity value (optional)')
    parser_opportunity_create.add_argument('--probability', required=False, type=float, help='Probability percentage (optional)')
    parser_opportunity_create.add_argument('--expectedCloseDate', required=False, help='Expected close date (ISO string, optional)')
    parser_opportunity_create.add_argument('--source', required=False, help='Source (optional)')
    parser_opportunity_create.add_argument('--sourceUrl', required=False, help='Source URL (optional)')
    parser_opportunity_create.add_argument('--assignedTo', required=False, help='Assigned to user ID (optional)')
    parser_opportunity_create.add_argument('--tags', required=False, nargs='*', help='Tags (optional)')

    parser_opportunity_get = subparsers.add_parser('opportunity-get', help='Get a specific opportunity by ID')
    parser_opportunity_get.add_argument('--opportunityId', required=True, help='Opportunity ID')
    parser_opportunity_get.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    parser_opportunity_update = subparsers.add_parser('opportunity-update', help='Update an opportunity')
    parser_opportunity_update.add_argument('--opportunityId', required=True, help='Opportunity ID')
    parser_opportunity_update.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')
    parser_opportunity_update.add_argument('--pipelineId', required=False, help='Pipeline ID (optional)')
    parser_opportunity_update.add_argument('--stageId', required=False, help='Stage ID (optional)')
    parser_opportunity_update.add_argument('--contactId', required=False, help='Contact ID (optional)')
    parser_opportunity_update.add_argument('--title', required=False, help='Opportunity title (optional)')
    parser_opportunity_update.add_argument('--value', required=False, type=float, help='Opportunity value (optional)')
    parser_opportunity_update.add_argument('--probability', required=False, type=float, help='Probability percentage (optional)')
    parser_opportunity_update.add_argument('--expectedCloseDate', required=False, help='Expected close date (ISO string, optional)')
    parser_opportunity_update.add_argument('--source', required=False, help='Source (optional)')
    parser_opportunity_update.add_argument('--sourceUrl', required=False, help='Source URL (optional)')
    parser_opportunity_update.add_argument('--assignedTo', required=False, help='Assigned to user ID (optional)')
    parser_opportunity_update.add_argument('--tags', required=False, nargs='*', help='Tags (optional)')

    parser_opportunity_delete = subparsers.add_parser('opportunity-delete', help='Delete an opportunity')
    parser_opportunity_delete.add_argument('--opportunityId', required=True, help='Opportunity ID')
    parser_opportunity_delete.add_argument('--locationId', required=False, help='Location ID (uses GHL_LOCATION_ID if omitted)')

    args = parser.parse_args()

    # Helper to get locationId from args or env
    def get_location_id() -> str:
        loc = getattr(args, 'locationId', None)
        if loc:
            return loc
        return GHL_LOCATION_ID

    try:
        # ----- Agent Studio -----
        if args.command == 'agent-create':
            locationId = get_location_id()
            resp = ghl_request('POST', '/agent-studio/agent', json_data={
                'locationId': locationId,
                'agentName': args.agentName,
                'agentPrompt': args.agentPrompt,
                'welcomeMessage': args.welcomeMessage,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'agent-list':
            locationId = get_location_id()
            resp = ghl_request('GET', '/agent-studio/agent', params={
                'locationId': locationId,
                'limit': args.limit,
                'offset': args.offset,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'agent-get':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/agent-studio/agent/{args.agentId}', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        elif args.command == 'agent-execute':
            locationId = get_location_id()
            body = {
                'locationId': locationId,
                'message': args.message,
            }
            if args.executionId:
                body['executionId'] = args.executionId
            resp = ghl_request('POST', f'/agent-studio/agent/{args.agentId}/execute', json_data=body)
            print(json.dumps(resp, indent=2))

        # ----- Conversation AI -----
        elif args.command == 'conv-create':
            resp = ghl_request('POST', '/conversation-ai/agent', json_data={
                'agentName': args.agentName,
                'agentRole': args.agentRole,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'conv-search':
            resp = ghl_request('GET', '/conversation-ai/agents/search', params={
                'query': args.query,
                'limit': args.limit,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'conv-get':
            resp = ghl_request('GET', f'/conversation-ai/agent/{args.agentId}')
            print(json.dumps(resp, indent=2))

        elif args.command == 'conv-update':
            updates: Dict[str, Any] = {}
            if args.agentName is not None:
                updates['agentName'] = args.agentName
            if args.agentStatus is not None:
                updates['agentStatus'] = args.agentStatus
            resp = ghl_request('PUT', f'/conversation-ai/agent/{args.agentId}', json_data=updates)
            print(json.dumps(resp, indent=2))

        elif args.command == 'conv-delete':
            resp = ghl_request('DELETE', f'/conversation-ai/agent/{args.agentId}')
            print(json.dumps(resp, indent=2))

        # ----- Voice AI -----
        elif args.command == 'voice-create':
            locationId = get_location_id()
            resp = ghl_request('POST', '/voice-ai/agent', json_data={
                'locationId': locationId,
                'agentName': args.agentName,
                'agentPrompt': args.agentPrompt,
                'welcomeMessage': args.welcomeMessage,
                'voiceId': args.voiceId,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'voice-list':
            locationId = get_location_id()
            resp = ghl_request('GET', '/voice-ai/agents', params={
                'locationId': locationId,
                'page': args.page,
                'pageSize': args.pageSize,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'voice-get':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/voice-ai/agent/{args.agentId}', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        elif args.command == 'voice-delete':
            locationId = get_location_id()
            resp = ghl_request('DELETE', f'/voice-ai/agent/{args.agentId}', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        elif args.command == 'voice-logs':
            locationId = get_location_id()
            resp = ghl_request('GET', '/voice-ai/call-logs', params={
                'locationId': locationId,
                'agentId': args.agentId,
                'page': args.page,
                'pageSize': args.pageSize,
            })
            print(json.dumps(resp, indent=2))

        # ----- Knowledge Base -----
        elif args.command == 'kb-list':
            locationId = get_location_id()
            resp = ghl_request('GET', '/knowledge-base', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        elif args.command == 'kb-create':
            locationId = get_location_id()
            resp = ghl_request('POST', '/knowledge-base', json_data={
                'name': args.name,
                'locationId': locationId,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'kb-discover':
            locationId = get_location_id()
            resp = ghl_request('POST', f'/knowledge-base/{args.knowledgeBaseId}/websites/discover', json_data={'url': args.url})
            print(json.dumps(resp, indent=2))

        elif args.command == 'kb-train':
            locationId = get_location_id()
            resp = ghl_request('POST', f'/knowledge-base/{args.knowledgeBaseId}/train-urls', json_data={
                'locationId': locationId,
                'urls': args.urls,
            })
            print(json.dumps(resp, indent=2))

        # ----- Vibe AI -----
        elif args.command == 'vibe-chat':
            resp = ghl_request('GET', f'/vibe-ai/projects/{args.projectId}/chat', params={
                'limit': args.limit,
                'offset': args.offset,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'vibe-sandbox':
            resp = ghl_request('GET', f'/vibe-ai/projects/{args.projectId}/sandbox/keep-alive', params={})
            print(json.dumps(resp, indent=2))

        # ----- Funnels -----
        elif args.command == 'funnel-create':
            resp = ghl_request('POST', '/funnels/funnel/create', json_data={
                'name': args.name,
                'description': args.description,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'funnel-step':
            stepConfig = None
            if args.stepConfig:
                try:
                    stepConfig = json.loads(args.stepConfig)
                except json.JSONDecodeError:
                    print('Error: stepConfig must be valid JSON', file=sys.stderr)
                    sys.exit(1)
            resp = ghl_request('POST', '/funnels/funnel/create-step', json_data={
                'funnelId': args.funnelId,
                'stepName': args.stepName,
                'stepType': args.stepType,
                'stepConfig': stepConfig,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'funnel-geo':
            resp = ghl_request('POST', '/funnels/funnel/geo-location/', json_data={
                'funnelId': args.funnelId,
                'latitude': args.latitude,
                'longitude': args.longitude,
                'radius': args.radius,
            })
            print(json.dumps(resp, indent=2))

        # ----- Feature Flags -----
        elif args.command == 'feature-flags':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/locations/{locationId}/labs/featureFlags', params={})
            print(json.dumps(resp, indent=2))

        # ----- Facebook Integration -----
        elif args.command == 'fb-connection':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/integrations/facebook/{locationId}/connection', params={})
            print(json.dumps(resp, indent=2))

        elif args.command == 'fb-pages':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/integrations/facebook/{locationId}/linked-pages', params={})
            print(json.dumps(resp, indent=2))

        # ----- Chat Widget -----
        elif args.command == 'chat-widget':
            locationId = get_location_id()
            resp = ghl_request('GET', '/chat-widget/', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        # ----- WhatsApp Phone Numbers -----
        elif args.command == 'whatsapp':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/phone-system/whatsapp/location/{locationId}/phone-numbers', params={})
            print(json.dumps(resp, indent=2))

        # ----- Forms -----
        elif args.command == 'forms':
            resp = ghl_request('GET', '/forms/', params={})
            print(json.dumps(resp, indent=2))

        # ----- Custom Values -----
        elif args.command == 'custom-values':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/locations/{locationId}/customValues', params={})
            print(json.dumps(resp, indent=2))

        # ----- Payments Currency -----
        elif args.command == 'payments-currency':
            resp = ghl_request('GET', '/payments/currency', params={})
            print(json.dumps(resp, indent=2))

        # ----- Social Media Accounts -----
        elif args.command == 'social-media':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/social-media-posting/{locationId}/accounts', params={'fetchAll': 'true'})
            print(json.dumps(resp, indent=2))

        # ----- Templates -----
        elif args.command == 'templates':
            resp = ghl_request('GET', '/templates/list', params={})
            print(json.dumps(resp, indent=2))

        # ----- Pipelines -----
        elif args.command == 'pipelines':
            locationId = get_location_id()
            resp = ghl_request('GET', '/pipelines/', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        elif args.command == 'pipeline-create':
            locationId = get_location_id()
            resp = ghl_request('POST', '/pipelines/', json_data={
                'locationId': locationId,
                'name': args.name,
                'description': args.description,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'pipeline-get':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/pipelines/{args.pipelineId}', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        elif args.command == 'pipeline-update':
            locationId = get_location_id()
            resp = ghl_request('PUT', f'/pipelines/{args.pipelineId}', json_data={
                'locationId': locationId,
                'name': args.name,
                'description': args.description,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'pipeline-delete':
            locationId = get_location_id()
            resp = ghl_request('DELETE', f'/pipelines/{args.pipelineId}', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        elif args.command == 'pipeline-stages':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/pipelines/{args.pipelineId}/stages', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        elif args.command == 'pipeline-stage-create':
            locationId = get_location_id()
            resp = ghl_request('POST', f'/pipelines/{args.pipelineId}/stages', json_data={
                'locationId': locationId,
                'stageName': args.stageName,
                'stageType': args.stageType,
                'sort': args.sort,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'pipeline-stage-update':
            locationId = get_location_id()
            resp = ghl_request('PUT', f'/pipelines/{args.pipelineId}/stages/{args.stageId}', json_data={
                'locationId': locationId,
                'stageName': args.stageName,
                'stageType': args.stageType,
                'sort': args.sort,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'pipeline-stage-delete':
            locationId = get_location_id()
            resp = ghl_request('DELETE', f'/pipelines/{args.pipelineId}/stages/{args.stageId}', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        # ----- Opportunities -----
        elif args.command == 'opportunities':
            locationId = get_location_id()
            resp = ghl_request('GET', '/opportunities/', params={
                'locationId': locationId,
                'pipelineId': args.pipelineId,
                'stageId': args.stageId,
                'limit': args.limit,
                'offset': args.offset,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'opportunity-create':
            locationId = get_location_id()
            resp = ghl_request('POST', '/opportunities/', json_data={
                'locationId': locationId,
                'pipelineId': args.pipelineId,
                'stageId': args.stageId,
                'contactId': args.contactId,
                'title': args.title,
                'value': args.value,
                'probability': args.probability,
                'expectedCloseDate': args.expectedCloseDate,
                'source': args.source,
                'sourceUrl': args.sourceUrl,
                'assignedTo': args.assignedTo,
                'tags': args.tags,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'opportunity-get':
            locationId = get_location_id()
            resp = ghl_request('GET', f'/opportunities/{args.opportunityId}', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        elif args.command == 'opportunity-update':
            locationId = get_location_id()
            resp = ghl_request('PUT', f'/opportunities/{args.opportunityId}', json_data={
                'locationId': locationId,
                'pipelineId': args.pipelineId,
                'stageId': args.stageId,
                'contactId': args.contactId,
                'title': args.title,
                'value': args.value,
                'probability': args.probability,
                'expectedCloseDate': args.expectedCloseDate,
                'source': args.source,
                'sourceUrl': args.sourceUrl,
                'assignedTo': args.assignedTo,
                'tags': args.tags,
            })
            print(json.dumps(resp, indent=2))

        elif args.command == 'opportunity-delete':
            locationId = get_location_id()
            resp = ghl_request('DELETE', f'/opportunities/{args.opportunityId}', params={'locationId': locationId})
            print(json.dumps(resp, indent=2))

        else:
            print(f'Unknown command: {args.command}', file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()