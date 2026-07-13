import os
from pathlib import Path

# Root of the Performance_Test_Harness directory (two levels up from this file:
# backend/app/config.py -> backend/app -> backend -> Performance_Test_Harness)
HARNESS_ROOT = Path(__file__).resolve().parents[2]


class Settings:
    """Runtime configuration, overridable via environment variables.

    Defaults mirror the values baked into the original Streamlit app.py so the
    backend behaves identically when deployed on the same EC2 host.
    """

    def __init__(self) -> None:
        self.snowflake_account = os.environ.get("SNOWFLAKE_ACCOUNT", "SFSEEUROPE-EU_DEMO59")
        self.snowflake_user = os.environ.get("SNOWFLAKE_USER", "JACK")
        self.snowflake_database = os.environ.get("SNOWFLAKE_DATABASE", "THEMES_RESEARCH_DEMO")
        self.snowflake_schema = os.environ.get("SNOWFLAKE_SCHEMA", "RAW_DATA")

        self.private_key_path = os.environ.get(
            "PRIVATE_KEY_PATH", str(HARNESS_ROOT / "keys" / "rsa_key.p8")
        )

        self.java_home = os.environ.get(
            "JAVA_HOME", "/usr/lib/jvm/java-17-amazon-corretto.x86_64"
        )
        self.java_harness_dir = os.environ.get(
            "JAVA_HARNESS_DIR", str(HARNESS_ROOT / "java-harness")
        )
        self.jdbc_jar_path = os.environ.get(
            "JDBC_JAR_PATH", str(HARNESS_ROOT / "lib" / "snowflake-jdbc.jar")
        )
        self.slf4j_api_jar = os.environ.get(
            "SLF4J_API_JAR", str(HARNESS_ROOT / "lib" / "slf4j-api.jar")
        )
        self.slf4j_simple_jar = os.environ.get(
            "SLF4J_SIMPLE_JAR", str(HARNESS_ROOT / "lib" / "slf4j-simple.jar")
        )

        # Comma-separated list of allowed CORS origins for the local frontend.
        self.cors_origins = [
            o.strip()
            for o in os.environ.get(
                "CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if o.strip()
        ]

        # Warehouse used for querying INFORMATION_SCHEMA / ACCOUNT_USAGE metrics.
        self.metrics_warehouse = os.environ.get("METRICS_WAREHOUSE", "COMPUTE_WH")


settings = Settings()


# --- Option catalogs (ported from app.py) -------------------------------------

TABLE_OPTIONS = [
    {
        "id": "std_36b",
        "label": "RDP_TIMESERIES_OBSERVATION (36B rows)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION",
        "warehouse": "RDP_STANDARD_WH",
    },
    {
        "id": "it_36b",
        "label": "RDP_TIMESERIES_OBSERVATION_IT (36B rows - Interactive)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_IT",
        "warehouse": "RDP_INTERACTIVE_WH",
    },
    {
        "id": "it_date_so",
        "label": "RDP_TIMESERIES_OBSERVATION_IT_DATE_SO (36B rows - Interactive, DATE cluster + SO on TS_CD)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_IT_DATE_SO",
        "warehouse": "RDP_INTERACTIVE_WH",
    },
    {
        "id": "it_tscd",
        "label": "RDP_TIMESERIES_OBSERVATION_IT_TSCD (36B rows - Interactive, Ordered by TS_CD + SO)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_IT_TSCD",
        "warehouse": "RDP_INTERACTIVE_WH",
    },
    {
        "id": "v2_36b",
        "label": "RDP_TIMESERIES_OBSERVATION_36B_V2 (36B rows - 8-level TS_CD)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_36B_V2",
        "warehouse": "RDP_STANDARD_WH",
    },
    {
        "id": "v2_ordered",
        "label": "RDP_TIMESERIES_OBSERVATION_36B_V2_ORDERED (36B rows - Ordered + SO)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_36B_V2_ORDERED",
        "warehouse": "RDP_STANDARD_WH",
    },
    {
        "id": "v2_ordered_nocluster",
        "label": "RDP_TIMESERIES_OBSERVATION_36B_V2_ORDERED_NOCLUSTER (36B rows - Ordered + SO, No AC)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_36B_V2_ORDERED_NOCLUSTER",
        "warehouse": "RDP_STANDARD_WH",
    },
    {
        "id": "split_36b",
        "label": "RDP_TIMESERIES_OBSERVATION_36B_SPLIT (36B rows - Clustered on TS_CD)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_36B_SPLIT",
        "warehouse": "RDP_STANDARD_WH",
    },
    {
        "id": "split_5b",
        "label": "RDP_TIMESERIES_OBSERVATION_5B_SPLIT (5B rows - Clustered on TS_CD)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_5B_SPLIT",
        "warehouse": "RDP_STANDARD_WH",
    },
    {
        "id": "std_1b",
        "label": "RDP_TIMESERIES_OBSERVATION_1B (1B rows)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_1B",
        "warehouse": "RDP_STANDARD_WH",
    },
    {
        "id": "split_1b",
        "label": "RDP_TIMESERIES_OBSERVATION_1B_SPLIT (1B rows - Clustered on TS_CD)",
        "table": "THEMES_RESEARCH_DEMO.RAW_DATA.RDP_TIMESERIES_OBSERVATION_1B_SPLIT",
        "warehouse": "RDP_STANDARD_WH",
    },
]

QUERY_MIX_OPTIONS = [
    {"id": "single", "label": "Single-ticker deduplicated only"},
    {"id": "single_date_100", "label": "Single-ticker with date range only (100%)"},
    {"id": "single_date_mix", "label": "Single-ticker mix (80% single, 20% single+date range)"},
    {"id": "single_date_50", "label": "Single-ticker mix (50% single, 50% single+date range)"},
    {"id": "multi", "label": "Multi-ticker lookup only"},
    {"id": "multi_date", "label": "Multi-ticker with date range"},
    {"id": "mixed", "label": "Mixed (60% multi-ticker, 40% single-ticker)"},
    {"id": "full_mix", "label": "Full mix (40% multi, 30% multi+date, 30% single)"},
    {"id": "tscd_single", "label": "TS_CD single lookup"},
    {"id": "tscd_date", "label": "TS_CD with date range"},
    {"id": "tscd_multi", "label": "TS_CD multi-ticker lookup"},
    {"id": "tscd_mixed", "label": "TS_CD mixed (50% single, 30% date, 20% multi)"},
]

EXEC_MODE_OPTIONS = [
    {"id": "sync", "label": "Sync (Default)"},
    {"id": "async", "label": "Async (8 in-flight per connection)"},
]

TICKER_BIAS_OPTIONS = [
    {"id": "uniform", "label": "Uniform (random from 1M pool)"},
    {"id": "hot80", "label": "Hot Ticker Bias 80% (from top 1,000)"},
    {"id": "hot50", "label": "Hot Ticker Bias 50% (from top 1,000)"},
]

RESULT_LIMIT_OPTIONS = [
    {"id": "0", "label": "No limit (full result set)"},
    {"id": "500", "label": "500 rows"},
    {"id": "1000", "label": "1000 rows"},
    {"id": "5000", "label": "5000 rows"},
    {"id": "10000", "label": "10000 rows"},
]


def resolve_table(table_id: str):
    for opt in TABLE_OPTIONS:
        if opt["id"] == table_id:
            return opt
    return None


def valid_ids(options):
    return {opt["id"] for opt in options}
