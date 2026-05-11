"""
FastAPI application for Inf Expert Agent - Infrastructure & Operations.
Implements A2A protocol endpoints for agent discovery and communication.
"""

import os
import json
import logging

from fastapi import FastAPI, HTTPException, Depends, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage


# =====================================================================
# A2A Authentication
# =====================================================================
A2A_SHARED_SECRET = os.getenv("A2A_SHARED_SECRET", "")
_a2a_header = APIKeyHeader(name="X-A2A-Secret", auto_error=False)


async def require_a2a_secret(api_key: str = Security(_a2a_header)):
    """Mandatory shared secret for A2A inter-agent calls."""
    if not A2A_SHARED_SECRET:
        raise HTTPException(status_code=503, detail="A2A_SHARED_SECRET not configured")
    if api_key != A2A_SHARED_SECRET:
        raise HTTPException(status_code=401, detail="Invalid X-A2A-Secret header")
    return api_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inf-expert-agent")

app = FastAPI(
    title="Inf Expert Agent API",
    description="Infrastructure & Operations Agent - VPS Management, Deployments, Monitoring",
    version="1.0.0",
)

# =====================================================================
# Request ID Middleware (ISO 27001 A.8.15 - Trazabilidad)
# =====================================================================
import uuid

@app.middleware("http")
async def add_request_id(request, call_next):
    """
    Inject X-Request-ID and propagate X-Trace-ID end-to-end.
    See docs/A2A_PROTOCOL_SPEC.md.
    """
    request_id = str(uuid.uuid4())
    incoming_trace = request.headers.get("X-Trace-ID") or request.headers.get("x-trace-id")
    trace_id = incoming_trace or request_id
    request.state.request_id = request_id
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Trace-ID"] = trace_id
    logger.info(
        f"[req={request_id} trace={trace_id}] {request.method} {request.url.path} -> {response.status_code}"
    )
    return response

_infrastructure_graph = None


def _get_infrastructure_graph():
    """Lazily builds the infrastructure graph once per process."""
    global _infrastructure_graph
    if _infrastructure_graph is None:
        from graph.agent_graph import build_infrastructure_graph
        _infrastructure_graph = build_infrastructure_graph()
    return _infrastructure_graph


def _extract_graph_response(result: dict) -> str:
    """Returns the most relevant assistant text from a graph result."""
    messages = result.get("messages", []) if isinstance(result, dict) else []
    for message in reversed(messages):
        if isinstance(message, AIMessage) and getattr(message, "content", None):
            return message.content
    return "Infrastructure workflow completed without a textual summary."


# =====================================================================
# Models
# =====================================================================

class AgentCard(BaseModel):
    """Agent Card for A2A protocol discovery."""
    agent_id: str
    name: str
    description: str
    version: str
    capabilities: list[str]
    endpoint: str
    model: dict
    tools: list[str]
    mcp_servers: list[str]
    durability_modes: list[str] = ["sync"]
    streaming: bool = False


class HealthResponse(BaseModel):
    status: str
    agent: str
    version: str
    vps_connected: bool


# =====================================================================
# Health Check
# =====================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        agent="inf-expert-agent",
        version="1.0.0",
        vps_connected=True
    )


# =====================================================================
# A2A Protocol Endpoints (Gap C9)
# =====================================================================

@app.get("/a2a/{assistant_id}", tags=["A2A"])
async def get_agent_card(assistant_id: str):
    """
    A2A Protocol: Agent Card discovery endpoint.
    Returns agent capabilities for dynamic discovery.
    """
    agents = {
        "inf-expert-agent": AgentCard(
            agent_id="inf-expert-agent",
            name="Cerebro Técnico Infrastructure Agent",
            description="Gestión de infraestructura VPS, autocuración, monitoreo y operaciones SSH",
            version="1.0.0",
            capabilities=[
                "infrastructure_monitoring",
                "auto_healing",
                "log_analysis",
                "service_management",
                "vps_operations",
                "deployment_management"
            ],
            endpoint=f"http://localhost:{os.getenv('PORT', '8003')}/a2a/inf-expert-agent",
            model={
                "provider": "google",
                "name": "gemini-2.5-flash-preview-04-17",
                "temperature": 0.2,
                "max_tokens": 8192
            },
            tools=[
                "check_cpu",
                "check_ram",
                "check_disk",
                "fetch_logs_backend",
                "fetch_logs_nginx",
                "restart_service",
                "trigger_backup",
                "verify_schema",
                "resolver_bloqueo_puerto",
                "deploy_to_vps",
                "configure_nginx"
            ],
            mcp_servers=["brainstem_mcp"],
            durability_modes=["sync"],
            streaming=False
        )
    }
    
    if assistant_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {assistant_id} not found")
    
    return agents[assistant_id]


# =====================================================================
# A2A Task Persistence (per docs/A2A_PROTOCOL_SPEC.md v1.0)
# =====================================================================

import sqlite3
import threading
import time
from pathlib import Path

_TASK_DB_PATH = Path(os.getenv("A2A_TASK_DB", "data/a2a_tasks.db"))
_TASK_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
_task_lock = threading.Lock()


def _task_db():
    conn = sqlite3.connect(str(_TASK_DB_PATH), check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS a2a_tasks (
            task_id TEXT PRIMARY KEY,
            assistant_id TEXT NOT NULL,
            status TEXT NOT NULL,
            request_payload TEXT,
            response_payload TEXT,
            error_detail TEXT,
            idempotency_key TEXT UNIQUE,
            tenant_id TEXT,
            trace_id TEXT,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
        """
    )
    return conn


def _upsert_task(
    task_id: str,
    assistant_id: str,
    status: str,
    request_payload: dict | None = None,
    response_payload: dict | None = None,
    error_detail: str | None = None,
    idempotency_key: str | None = None,
    tenant_id: str | None = None,
    trace_id: str | None = None,
) -> None:
    now = time.time()
    with _task_lock:
        conn = _task_db()
        try:
            row = conn.execute(
                "SELECT created_at FROM a2a_tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
            req_json = json.dumps(request_payload) if request_payload is not None else None
            res_json = json.dumps(response_payload) if response_payload is not None else None
            if row is None:
                conn.execute(
                    """INSERT INTO a2a_tasks
                       (task_id, assistant_id, status, request_payload, response_payload,
                        error_detail, idempotency_key, tenant_id, trace_id, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (task_id, assistant_id, status, req_json, res_json,
                     error_detail, idempotency_key, tenant_id, trace_id, now, now),
                )
            else:
                conn.execute(
                    """UPDATE a2a_tasks
                       SET status = ?, request_payload = COALESCE(?, request_payload),
                           response_payload = COALESCE(?, response_payload),
                           error_detail = ?, updated_at = ?
                       WHERE task_id = ?""",
                    (status, req_json, res_json, error_detail, now, task_id),
                )
            conn.commit()
        finally:
            conn.close()


def _get_task(task_id: str) -> dict | None:
    with _task_lock:
        conn = _task_db()
        try:
            row = conn.execute(
                """SELECT task_id, assistant_id, status, request_payload, response_payload,
                          error_detail, created_at, updated_at
                   FROM a2a_tasks WHERE task_id = ?""",
                (task_id,),
            ).fetchone()
        finally:
            conn.close()
    if row is None:
        return None
    return {
        "taskId": row[0],
        "assistant_id": row[1],
        "status": row[2],
        "request": json.loads(row[3]) if row[3] else None,
        "response": json.loads(row[4]) if row[4] else None,
        "error": row[5],
        "created_at": row[6],
        "updated_at": row[7],
    }


@app.post("/a2a/{assistant_id}/message/send", tags=["A2A"], dependencies=[Depends(require_a2a_secret)])
async def a2a_send_message(assistant_id: str, request: dict, req: Request):
    """
    A2A Protocol: Synchronous message sending (RPC).
    Sends a message to the infrastructure agent and waits for response.
    Persists task state per A2A_PROTOCOL_SPEC.md.
    Supports Idempotency-Key header for deduplication.
    """
    import uuid

    if assistant_id != "inf-expert-agent":
        raise HTTPException(status_code=404, detail=f"Agent {assistant_id} not implemented")

    idempotency_key = req.headers.get("Idempotency-Key")
    if idempotency_key:
        with _task_lock:
            conn = _task_db()
            try:
                row = conn.execute(
                    "SELECT task_id, status, response_payload FROM a2a_tasks WHERE idempotency_key = ?",
                    (idempotency_key,),
                ).fetchone()
            finally:
                conn.close()
        if row:
            resp = json.loads(row[2]) if row[2] else {}
            return {
                "taskId": row[0],
                "status": row[1],
                "response": resp.get("response"),
                "result": resp.get("result"),
            }

    task_id = request.get("contextId") or str(uuid.uuid4())
    message = (request.get("message") or {}).get("content", "")
    metadata = request.get("metadata") or {}
    tenant_id = metadata.get("tenant_id")
    trace_id = metadata.get("trace_id")

    if not message:
        raise HTTPException(status_code=400, detail="Message content required")

    _upsert_task(
        task_id=task_id,
        assistant_id=assistant_id,
        status="running",
        request_payload=request,
        idempotency_key=idempotency_key,
        tenant_id=tenant_id,
        trace_id=trace_id,
    )

    graph = _get_infrastructure_graph()
    initial_state = {
        "messages": [HumanMessage(content=message)],
        "vps_metrics": metadata.get("vps_metrics", message),
        "issues_found": [],
        "actions_taken": [],
        "requires_human": False,
        "current_agent": None,
    }
    config = {"configurable": {"thread_id": task_id}}

    try:
        from core.observability import get_langfuse_callback_handler
        langfuse_handler = get_langfuse_callback_handler()
        if langfuse_handler:
            config["callbacks"] = [langfuse_handler]
    except ImportError:
        pass

    try:
        result = graph.invoke(initial_state, config=config)
        response_text = _extract_graph_response(result)
        response_payload = {
            "taskId": task_id,
            "status": "completed",
            "response": response_text,
            "result": {
                "issues_found": result.get("issues_found", []),
                "actions_taken": result.get("actions_taken", []),
                "requires_human": result.get("requires_human", False),
            },
        }
        _upsert_task(
            task_id=task_id,
            assistant_id=assistant_id,
            status="completed",
            response_payload=response_payload,
        )
        return response_payload
    except Exception as e:
        logger.error(f"Infrastructure graph execution failed: {e}", exc_info=True)
        _upsert_task(
            task_id=task_id,
            assistant_id=assistant_id,
            status="failed",
            error_detail=str(e),
        )
        raise HTTPException(status_code=500, detail="Infrastructure agent execution failed")


@app.get("/a2a/{assistant_id}/tasks/{task_id}", tags=["A2A"], dependencies=[Depends(require_a2a_secret)])
async def a2a_get_task(assistant_id: str, task_id: str):
    """A2A Protocol: Get task status. Returns 404 if task not found."""
    task = _get_task(task_id)
    if task is None or task["assistant_id"] != assistant_id:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


# =====================================================================
# Agent Card Endpoint for Agent Discovery
# =====================================================================

@app.get("/agent-card", tags=["Discovery"])
def get_agent_card_from_manifest():
    """
    Agent Card for automatic discovery in the multi-agent ecosystem.
    Returns agent metadata from langgraph.json for service registry.
    """
    langgraph_config_path = os.path.join(
        os.path.dirname(__file__), "..", "langgraph.json"
    )
    langgraph_config_path = os.path.normpath(langgraph_config_path)
    
    try:
        if os.path.exists(langgraph_config_path):
            with open(langgraph_config_path, "r") as f:
                config = json.load(f)
            
            agent_card = {
                "name": config.get("agent_name", "inf-expert-agent"),
                "description": config.get("description", ""),
                "version": config.get("version", "1.0.0"),
                "model": config.get("model", {}),
                "api": {
                    "base_url": f"http://localhost:{os.getenv('PORT', '8003')}/api/v1",
                    "version": "v1",
                    "endpoints": {
                        "a2a": "/a2a/inf-expert-agent",
                        "health": "/health"
                    }
                },
                "capabilities": {
                    "vps_management": True,
                    "monitoring": True,
                    "auto_healing": True,
                    "deployment": True,
                    "ssh_operations": True
                },
                "compliance": {
                    "ssh_key_management": True,
                    "audit_logging": True
                }
            }
            return JSONResponse(content=agent_card)
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "Agent card not found", "path": langgraph_config_path}
            )
    except Exception as e:
        logger.error(f"Error reading agent card: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
