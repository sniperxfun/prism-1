"""
PRISM MCP Server — Model Context Protocol compatible server.

Exposes the Evolution Experience Library as MCP tools that can be
consumed by Claude Code, Cursor, Windsurf, and other MCP-compatible clients.

Supports two transport modes:
  - stdio (default): For direct integration with AI tools
  - sse: For HTTP-based access

Usage:
  python -m prism.mcp_server                # stdio mode
  python -m prism.mcp_server --transport sse --port 3100  # SSE mode
"""

import argparse
import json
import sys
from typing import Any

from .evolution import ExperienceLibrary

# ── MCP Protocol Constants ───────────────────────────────────────────────────

JSONRPC_VERSION = "2.0"
MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "prism-evolution"
SERVER_VERSION = "0.2.0"

# ── Tool Definitions ─────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "recall_experience",
        "description": "Retrieve relevant principles from the PRISM Experience Library. "
                       "Call at the START of every task to benefit from accumulated knowledge.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {
                    "type": "string",
                    "description": "Agent slug (e.g. 'backend-architect')"
                },
                "context": {
                    "type": "string",
                    "description": "Brief description of the current task"
                },
                "top_k": {
                    "type": "integer",
                    "default": 5,
                    "description": "Max number of principles to return"
                },
                "min_confidence": {
                    "type": "number",
                    "default": 0.7,
                    "description": "Minimum confidence threshold"
                }
            },
            "required": ["agent", "context"]
        }
    },
    {
        "name": "record_decision",
        "description": "Log a significant decision for future distillation. "
                       "Call when making important architectural, technical, or strategic choices.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string", "description": "Agent slug"},
                "decision": {"type": "string", "description": "What was decided"},
                "rationale": {"type": "string", "description": "Why this decision was made"},
                "alternatives": {"type": "string", "description": "Alternatives considered"},
                "outcome": {
                    "type": "string",
                    "enum": ["pending", "success", "partial", "failure"],
                    "default": "pending"
                }
            },
            "required": ["agent", "decision", "rationale"]
        }
    },
    {
        "name": "report_telemetry",
        "description": "Report task execution metrics. Call at the END of every task "
                       "to feed the evolution loop.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string", "description": "Agent slug"},
                "task_type": {"type": "string", "description": "Type of task performed"},
                "outcome": {
                    "type": "string",
                    "enum": ["pass", "fail", "partial"],
                    "description": "Task outcome"
                },
                "retry_count": {
                    "type": "integer",
                    "default": 0,
                    "description": "Number of retries needed"
                },
                "failure_category": {"type": "string", "description": "Category of failure if any"},
                "notes": {"type": "string", "description": "Additional notes"}
            },
            "required": ["agent", "task_type", "outcome"]
        }
    },
    {
        "name": "get_agent_stats",
        "description": "View an agent's performance history and evolution status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string", "description": "Agent slug"}
            },
            "required": ["agent"]
        }
    },
    {
        "name": "add_principle",
        "description": "Add a new principle to the Experience Library. "
                       "Used by the distillation engine or manually by operators.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string", "description": "Agent slug"},
                "text": {"type": "string", "description": "Principle text"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags for retrieval"
                },
                "confidence": {
                    "type": "number",
                    "default": 0.5,
                    "description": "Confidence score (0-1)"
                }
            },
            "required": ["agent", "text", "tags"]
        }
    }
]


# ── Tool Handlers ────────────────────────────────────────────────────────────

class ToolHandler:
    """Routes MCP tool calls to ExperienceLibrary methods."""

    def __init__(self):
        self.library = ExperienceLibrary()

    def handle(self, tool_name: str, arguments: dict) -> Any:
        handlers = {
            "recall_experience": self._recall,
            "record_decision": self._record_decision,
            "report_telemetry": self._report_telemetry,
            "get_agent_stats": self._get_stats,
            "add_principle": self._add_principle,
        }
        handler = handlers.get(tool_name)
        if not handler:
            raise ValueError(f"Unknown tool: {tool_name}")
        return handler(arguments)

    def _recall(self, args: dict) -> dict:
        principles = self.library.recall(
            agent=args["agent"],
            context=args["context"],
            top_k=args.get("top_k", 5),
            min_confidence=args.get("min_confidence", 0.7),
        )
        return {
            "principles": principles,
            "agent": args["agent"],
            "count": len(principles),
        }

    def _record_decision(self, args: dict) -> dict:
        decision_id = self.library.record_decision(
            agent=args["agent"],
            decision=args["decision"],
            rationale=args["rationale"],
            alternatives=args.get("alternatives"),
            outcome=args.get("outcome", "pending"),
        )
        return {"decision_id": decision_id, "recorded": True}

    def _report_telemetry(self, args: dict) -> dict:
        telemetry_id = self.library.report_telemetry(
            agent=args["agent"],
            task_type=args["task_type"],
            outcome=args["outcome"],
            retry_count=args.get("retry_count", 0),
            failure_category=args.get("failure_category"),
            notes=args.get("notes"),
        )
        return {"telemetry_id": telemetry_id, "recorded": True}

    def _get_stats(self, args: dict) -> dict:
        return self.library.get_agent_stats(args["agent"])

    def _add_principle(self, args: dict) -> dict:
        principle_id = self.library.add_principle(
            agent=args["agent"],
            text=args["text"],
            tags=args.get("tags", []),
            confidence=args.get("confidence", 0.5),
        )
        return {"principle_id": principle_id, "recorded": True}


# ── JSON-RPC / MCP Protocol ─────────────────────────────────────────────────

class MCPServer:
    """MCP-compatible JSON-RPC server over stdio."""

    def __init__(self):
        self.handler = ToolHandler()

    def process_message(self, message: dict) -> dict:
        """Process a single JSON-RPC message."""
        method = message.get("method", "")
        msg_id = message.get("id")
        params = message.get("params", {})

        if method == "initialize":
            return self._response(msg_id, {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION,
                }
            })

        elif method == "notifications/initialized":
            return None  # No response needed for notifications

        elif method == "tools/list":
            return self._response(msg_id, {"tools": TOOLS})

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            try:
                result = self.handler.handle(tool_name, arguments)
                return self._response(msg_id, {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, indent=2, default=str)
                    }]
                })
            except Exception as e:
                return self._response(msg_id, {
                    "content": [{
                        "type": "text",
                        "text": json.dumps({"error": str(e)})
                    }],
                    "isError": True,
                })

        elif method == "ping":
            return self._response(msg_id, {})

        else:
            return self._error(msg_id, -32601, f"Method not found: {method}")

    def _response(self, msg_id, result: dict) -> dict:
        return {"jsonrpc": JSONRPC_VERSION, "id": msg_id, "result": result}

    def _error(self, msg_id, code: int, message: str) -> dict:
        return {"jsonrpc": JSONRPC_VERSION, "id": msg_id, "error": {"code": code, "message": message}}

    def run_stdio(self):
        """Run the server in stdio mode, reading JSON-RPC messages from stdin."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
                response = self.process_message(message)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError:
                error = self._error(None, -32700, "Parse error")
                sys.stdout.write(json.dumps(error) + "\n")
                sys.stdout.flush()


# ── Entry Point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PRISM MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio")
    parser.add_argument("--port", type=int, default=3100)
    args = parser.parse_args()

    server = MCPServer()

    if args.transport == "stdio":
        server.run_stdio()
    elif args.transport == "sse":
        print(f"SSE transport on port {args.port} — not yet implemented", file=sys.stderr)
        print("Use stdio transport for now.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
