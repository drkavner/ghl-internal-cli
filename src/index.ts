#!/usr/bin/env node
/**
 * GHL Internal CLI / MCP Server
 * Provides access to the internal GHL v2 API for:
 *   • Agent Studio (AI agents)
 *   • Conversation AI (AskAI / AI Employees)
 *   • Voice AI
 *   • Knowledge Base
 *   • Vibe AI
 *   • Funnels
 *   • Feature Flags
 *   • Facebook Integration
 *
 * Runs as an MCP stdio server when invoked without arguments,
 * or as a simple CLI when a sub‑command is supplied.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import HighLevel from '@gohighlevel/api-client';

// -----------------------------------------------------------------------------
// Configuration (read from env)
// -----------------------------------------------------------------------------
const API_KEY = process.env.GHL_API_KEY ?? '';
const LOCATION_ID = process.env.GHL_LOCATION_ID ?? '';

if (!API_KEY) {
  console.error('[ghl-internal-cli] ERROR: GHL_API_KEY environment variable required');
  process.exit(1);
}

const ghl = new HighLevel({
  privateIntegrationToken: API_KEY,
});

// -----------------------------------------------------------------------------
// Helper: wrapper that adds the required Version header
// -----------------------------------------------------------------------------
async function ghRequest<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  path: string,
  params?: Record<string, any>,
  data?: any
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    Version: '2021-07-28',
    Authorization: `Bearer ${API_KEY.replace(/^pur\-/i, '')}`,
  };

  const url = `https://services.leadconnectorhq.com${path}`;

  // The @gohighlevel/api-client wrapper expects a `request` method.
  // We'll use its internal axios instance via `ghl.request`.
  const response = await ghl.request({
    method,
    url,
    params,
    data,
    headers,
  });

  return response.data;
}

// -----------------------------------------------------------------------------
// Tool definitions (mirror the capabilities in server.py)
// -----------------------------------------------------------------------------
const tools = [
  // ----- Agent Studio -----
  {
    name: 'ghl_agent_studio_create_agent',
    description: 'Create a new AI agent in Agent Studio',
    inputSchema: {
      type: 'object',
      properties: {
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
        agentName: { type: 'string', description: 'Agent name' },
        agentPrompt: { type: 'string', description: 'System prompt' },
        welcomeMessage: { type: 'string', description: 'Welcome message' },
      },
      required: ['locationId'],
    },
  },
  {
    name: 'ghl_agent_studio_get_agents',
    description: 'List all AI agents in Agent Studio',
    inputSchema: {
      type: 'object',
      properties: {
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
        limit: { type: 'string', default: '100' },
        offset: { type: 'string', default: '0' },
      },
      required: ['locationId'],
    },
  },
  {
    name: 'ghl_agent_studio_get_agent',
    description: 'Get a specific AI agent by ID',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string', description: 'Agent ID to retrieve' },
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
      },
      required: ['agentId', 'locationId'],
    },
  },
  {
    name: 'ghl_agent_studio_execute_agent',
    description: 'Execute an AI agent and get a response',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string', description: 'Agent ID to execute' },
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
        message: { type: 'string', description: 'Message to send' },
        executionId: {
          type: 'string',
          description: 'Session ID (optional)',
        },
      },
      required: ['agentId', 'locationId', 'message'],
    },
  },

  // ----- Conversation AI (AskAI / AI Employees) -----
  {
    name: 'ghl_conversation_ai_create_agent',
    description: 'Create a Conversation AI agent (AskAI / AI Employee)',
    inputSchema: {
      type: 'object',
      properties: {
        agentName: { type: 'string', description: 'Agent name' },
        agentRole: { type: 'string', description: 'Agent role/purpose' },
      },
    },
  },
  {
    name: 'ghl_conversion_ai_get_agent',
    description: 'Get a Conversation AI agent by ID (typo fix)',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string', description: 'Agent ID' },
      },
      required: ['agentId'],
    },
  },
  {
    name: 'ghl_conversation_ai_search_agents',
    description: 'Search Conversation AI agents',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query' },
        limit: { type: 'number', default: 100 },
      },
    },
  },
  {
    name: 'ghl_conversation_ai_get_agent',
    description: 'Get a Conversation AI agent by ID',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string', description: 'Agent ID' },
      },
      required: ['agentId'],
    },
  },
  {
    name: 'ghl_conversation_ai_update_agent',
    description: 'Update a Conversation AI agent',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string', description: 'Agent ID' },
        agentName: {
          type: 'string',
          description: 'New agent name (optional)',
        },
        agentStatus: {
          type: 'string',
          description: "New status (e.g., 'active', 'paused')",
        },
      },
      required: ['agentId'],
    },
  },
  {
    name: 'ghl_conversation_ai_delete_agent',
    description: 'Delete a Conversation AI agent',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string', description: 'Agent ID' },
      },
      required: ['agentId'],
    },
  },

  // ----- Voice AI -----
  {
    name: 'ghl_voice_ai_create_agent',
    description: 'Create a Voice AI agent',
    inputSchema: {
      type: 'object',
      properties: {
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
        agentName: { type: 'string', description: 'Agent name' },
        agentPrompt: { type: 'string', description: 'Agent prompt' },
        welcomeMessage: { type: 'string', description: 'Welcome message' },
        voiceId: { type: 'string', description: 'Voice ID' },
      },
      required: ['locationId'],
    },
  },
  {
    name: 'ghl_voice_ai_get_agents',
    description: 'List Voice AI agents',
    inputSchema: {
      type: 'object',
      properties: {
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
        page: { type: 'number', default: 1 },
        pageSize: { type: 'number', default: 20 },
      },
      required: ['locationId'],
    },
  },
  {
    name: 'ghl_voice_ai_get_agent',
    description: 'Get a Voice AI agent by ID',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string', description: 'Agent ID' },
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
      },
      required: ['agentId', 'locationId'],
    },
  },
  {
    name: 'ghl_voice_ai_delete_agent',
    description: 'Delete a Voice AI agent',
    inputSchema: {
      type: 'object',
      properties: {
        agentId: { type: 'string', description: 'Agent ID' },
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
      },
      required: ['agentId', 'locationId'],
    },
  },
  {
    name: 'ghl_voice_ai_get_call_logs',
    description: 'Get Voice AI call logs',
    inputSchema: {
      type: 'object',
      properties: {
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
        agentId: { type: 'string', description: 'Agent ID' },
        page: { type: 'number', default: 1 },
        pageSize: { type: 'number', default: 20 },
      },
      required: ['locationId', 'agentId'],
    },
  },

  // ----- Knowledge Base -----
  {
    name: 'ghl_knowledge_base_list',
    description: 'List all knowledge bases for a location',
    inputSchema: {
      type: 'object',
      properties: {
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
      },
      required: ['locationId'],
    },
  },
  {
    name: 'ghl_knowledge_base_create',
    description: 'Create a knowledge base for AI training',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Knowledge base name' },
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
      },
      required: ['name', 'locationId'],
    },
  },
  {
    name: 'ghl_knowledge_base_discover_website',
    description: 'Discover website pages for knowledge base training',
    inputSchema: {
      type: 'object',
      properties: {
        knowledgeBaseId: {
          type: 'string',
          description: 'Knowledge base ID',
        },
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
        url: { type: 'string', description: 'URL to scan' },
      },
      required: ['knowledgeBaseId', 'locationId', 'url'],
    },
  },
  {
    name: 'ghl_knowledge_base_train_urls',
    description:
      'Train discovered URLs into a knowledge base (accepts an array of URLs)',
    inputSchema: {
      type: 'object',
      properties: {
        knowledgeBaseId: {
          type: 'string',
          description: 'Knowledge base ID',
        },
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
        urls: {
          type: 'array',
          items: { type: 'string' },
          description: 'List of URLs to train on',
        },
      },
      required: ['knowledgeBaseId', 'locationId', 'urls'],
    },
  },

  // ----- Vibe AI -----
  {
    name: 'ghl_vibe_ai_chat_get',
    description: 'Get chat messages from a Vibe AI project',
    inputSchema: {
      type: 'object',
      properties: {
        projectId: { type: 'string', description: 'Vibe AI project ID' },
        limit: { type: 'string', default: '100' },
        offset: { type: 'string', default: '0' },
      },
      required: ['projectId'],
    },
  },
  {
    name: 'ghl_vibe_ai_sandbox_keepalive',
    description: 'Keep Vibe AI sandbox alive',
    inputSchema: {
      type: 'object',
      properties: {
        projectId: { type: 'string', description: 'Vibe AI project ID' },
      },
      required: ['projectId'],
    },
  },

  // ----- Funnels -----
  {
    name: 'ghl_funnel_create',
    description: 'Create a funnel',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Funnel name' },
        description: { type: 'string', description: 'Funnel description' },
      },
      required: ['name'],
    },
  },
  {
    name: 'ghl_funnel_create_step',
    description: 'Create a funnel step',
    inputSchema: {
      type: 'object',
      properties: {
        funnelId: { type: 'string', description: 'Funnel ID' },
        stepName: { type: 'string', description: 'Step name' },
        stepType: { type: 'string', description: 'Step type' },
        stepConfig: {
          type: 'object',
          description: 'Step configuration (JSON object)',
        },
      },
      required: ['funnelId', 'stepName', 'stepType'],
    },
  },
  {
    name: 'ghl_funnel_geo_location',
    description: 'Get or set geo‑location settings for a funnel',
    inputSchema: {
      type: 'object',
      properties: {
        funnelId: { type: 'string', description: 'Funnel ID' },
        latitude: { type: 'number', description: 'Latitude' },
        longitude: { type: 'number', description: 'Longitude' },
        radius: { type: 'number', description: 'Radius in meters' },
      },
      required: ['funnelId'],
    },
  },

  // ----- Feature Flags -----
  {
    name: 'ghl_feature_flags_get',
    description: 'Get feature flags for a location',
    inputSchema: {
      type: 'object',
      properties: {
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
      },
      required: ['locationId'],
    },
  },

  // ----- Facebook Integration -----
  {
    name: 'ghl_facebook_connection_get',
    description: 'Get Facebook connection for a location',
    inputSchema: {
      type: 'object',
      properties: {
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
      },
      required: ['locationId'],
    },
  },
  {
    name: 'ghl_facebook_linked_pages_get',
    description: 'Get linked Facebook pages for a location',
    inputSchema: {
      type: 'object',
      properties: {
        locationId: {
          type: 'string',
          description: 'Location ID (uses GHL_LOCATION_ID if omitted)',
        },
      },
      required: ['locationId'],
    },
  },
];

// -----------------------------------------------------------------------------
// MCP Server setup
// -----------------------------------------------------------------------------
const server = new Server(
  {
    name: 'ghl-internal-cli',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools,
}));

// Call a tool
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const locId = (args?.locationId as string) ?? LOCATION_ID;

  try {
    // ----- Agent Studio -----
    if (name === 'ghl_agent_studio_create_agent') {
      const resp = await ghRequest('POST', '/agent-studio/agent', undefined, {
        locationId: locId,
        agentName: args?.agentName,
        agentPrompt: args?.agentPrompt,
        welcomeMessage: args?.welcomeMessage,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_agent_studio_get_agents') {
      const resp = await ghRequest('GET', '/agent-studio/agent', {
        locationId: locId,
        limit: args?.limit ?? '100',
        offset: args?.offset ?? '0',
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_agent_studio_get_agent') {
      const resp = await ghRequest(
        'GET',
        `/agent-studio/agent/${args?.agentId}`,
        { locationId: locId }
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_agent_studio_execute_agent') {
      const body: any = {
        locationId: locId,
        message: args?.message,
      };
      if (args?.executionId) body.executionId = args.executionId;
      const resp = await ghRequest(
        'POST',
        `/agent-studio/agent/${args?.agentId}/execute`,
        undefined,
        body
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    // ----- Conversation AI -----
    if (name === 'ghl_conversation_ai_create_agent') {
      const resp = await ghRequest('POST', '/conversation-ai/agent', undefined, {
        agentName: args?.agentName,
        agentRole: args?.agentRole,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_conversion_ai_get_agent') {
      // Note: Typo fix – this branch should be for get_agent
      const resp = await ghRequest(
        'GET',
        `/conversation-ai/agent/${args?.agentId}`
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_conversation_ai_search_agents') {
      const resp = await ghRequest('GET', '/conversation-ai/agents/search', {
        query: args?.query,
        limit: args?.limit ?? 100,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_conversation_ai_get_agent') {
      const resp = await ghRequest(
        'GET',
        `/conversation-ai/agent/${args?.agentId}`
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_conversation_ai_update_agent') {
      const updates: any = {};
      if (args?.agentName !== undefined) updates.agentName = args.agentName;
      if (args?.agentStatus !== undefined) updates.agentStatus = args.agentStatus;
      const resp = await ghRequest(
        'PUT',
        `/conversation-ai/agent/${args?.agentId}`,
        undefined,
        updates
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_conversation_ai_delete_agent') {
      const resp = await ghRequest(
        'DELETE',
        `/conversation-ai/agent/${args?.agentId}`
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    // ----- Voice AI -----
    if (name === 'ghl_voice_ai_create_agent') {
      const resp = await ghRequest('POST', '/voice-ai/agent', undefined, {
        locationId: locId,
        agentName: args?.agentName,
        agentPrompt: args?.agentPrompt,
        welcomeMessage: args?.welcomeMessage,
        voiceId: args?.voiceId,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_voice_ai_get_agents') {
      const resp = await ghRequest('GET', '/voice-ai/agents', {
        locationId: locId,
        page: args?.page ?? 1,
        pageSize: args?.pageSize ?? 20,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_voice_ai_get_agent') {
      const resp = await ghRequest(
        'GET',
        `/voice-ai/agent/${args?.agentId}`,
        { locationId: locId }
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_voice_ai_delete_agent') {
      const resp = await ghRequest(
        'DELETE',
        `/voice-ai/agent/${args?.agentId}`,
        { locationId: locId }
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_voice_ai_get_call_logs') {
      const resp = await ghRequest('GET', '/voice-ai/call-logs', {
        locationId: locId,
        agentId: args?.agentId,
        page: args?.page ?? 1,
        pageSize: args?.pageSize ?? 20,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    // ----- Knowledge Base -----
    if (name === 'ghl_knowledge_base_list') {
      const resp = await ghRequest('GET', '/knowledge-base', {
        locationId: locId,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_knowledge_base_create') {
      const resp = await ghRequest('POST', '/knowledge-base', undefined, {
        name: args?.name,
        locationId: locId,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_knowledge_base_discover_website') {
      const resp = await ghRequest(
        'POST',
        `/knowledge-base/${args?.knowledgeBaseId}/websites/discover`,
        undefined,
        { url: args?.url }
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_knowledge_base_train_urls') {
      const resp = await ghRequest(
        'POST',
        `/knowledge-base/${args?.knowledgeBaseId}/train-urls`,
        undefined,
        {
          locationId: locId,
          urls: args?.urls,
        }
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    // ----- Vibe AI -----
    if (name === 'ghl_vibe_ai_chat_get') {
      const resp = await ghRequest(
        'GET',
        `/vibe-ai/projects/${args?.projectId}/chat`,
        {
          limit: args?.limit ?? '100',
          offset: args?.offset ?? '0',
        }
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_vibe_ai_sandbox_keepalive') {
      const resp = await ghRequest(
        'GET',
        `/vibe-ai/projects/${args?.projectId}/sandbox/keep-alive`,
        {}
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    // ----- Funnels -----
    if (name === 'ghl_funnel_create') {
      const resp = await ghRequest('POST', '/funnels/funnel/create', undefined, {
        name: args?.name,
        description: args?.description,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_funnel_create_step') {
      const resp = await ghRequest('POST', '/funnels/funnel/create-step', undefined, {
        funnelId: args?.funnelId,
        stepName: args?.stepName,
        stepType: args?.stepType,
        stepConfig: args?.stepConfig,
      });
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_funnel_geo_location') {
      const resp = await ghRequest(
        'POST',
        '/funnels/funnel/geo-location/',
        undefined,
        {
          funnelId: args?.funnelId,
          latitude: args?.latitude,
          longitude: args?.longitude,
          radius: args?.radius,
        }
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    // ----- Feature Flags -----
    if (name === 'ghl_feature_flags_get') {
      const resp = await ghRequest(
        'GET',
        `/locations/${locId}/labs/featureFlags`,
        {}
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    // ----- Facebook Integration -----
    if (name === 'ghl_facebook_connection_get') {
      const resp = await ghRequest(
        'GET',
        `/integrations/facebook/${locId}/connection`,
        {}
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    if (name === 'ghl_facebook_linked_pages_get') {
      const resp = await ghRequest(
        'GET',
        `/integrations/facebook/${locId}/linked-pages`,
        {}
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(resp, null, 2) }],
      };
    }

    // Unknown tool
    return {
      content: [{ type: 'text', text: `Unknown tool: ${name}` }],
      isError: true,
    };
  } catch (err: any) {
    return {
      content: [{ type: 'text', text: `Error: ${err.message ?? String(err)}` }],
      isError: true,
    };
  }
});

// -----------------------------------------------------------------------------
// Start server (stdio) – this is what Hermes/MCP clients will connect to
// -----------------------------------------------------------------------------
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('[ghl-internal-cli] MCP server connected via stdio');
}

main().catch((err) => {
  console.error('[ghl-internal-cli] Fatal error:', err);
  process.exit(1);
});