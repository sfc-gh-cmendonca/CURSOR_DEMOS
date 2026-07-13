from typing import Any, Optional
from pydantic import BaseModel, Field


class TestConfigRequest(BaseModel):
    table_id: str = Field(..., description="Target table id from /api/config")
    query_mix: str = Field("single", description="Query mix id")
    exec_mode: str = Field("sync", description="sync | async")
    ticker_bias: str = Field("uniform", description="uniform | hot80 | hot50")
    num_connections: int = Field(100, ge=1, le=300)
    duration_seconds: int = Field(120, ge=5, le=900)
    result_limit: str = Field("0", description="0 | 500 | 1000 | 5000 | 10000")


class Option(BaseModel):
    id: str
    label: str


class TableOption(Option):
    table: str
    warehouse: str


class ConfigResponse(BaseModel):
    tables: list[TableOption]
    query_mixes: list[Option]
    exec_modes: list[Option]
    ticker_biases: list[Option]
    result_limits: list[Option]
    defaults: dict[str, Any]


class StartTestResponse(BaseModel):
    test_id: str
    status: str


class TestStatusResponse(BaseModel):
    test_id: str
    status: str  # queued | running | completed | error | stopped
    config: dict[str, Any]
    table: Optional[str] = None
    warehouse: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error: Optional[str] = None
    results: Optional[dict[str, Any]] = None
    server_stats: Optional[dict[str, Any]] = None
    server_details: Optional[list[dict[str, Any]]] = None
    cluster_stats: Optional[list[dict[str, Any]]] = None
    cache_stats: Optional[dict[str, Any]] = None
