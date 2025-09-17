---
description: Project structure and file organization standards
---

# File Organization Standards

## Project Structure
```
/
├── config.py                    # Master configuration
├── setup.py                     # Main setup script with mode options
├── requirements.txt              # Python dependencies
├── README.md                     # Setup and demo instructions
├── docs/
│   ├── agent_setup_instructions.md  # Detailed agent configuration guide
│   └── demo_script.md           # Complete demo delivery scripts
├── src/
│   ├── data_generation/
│   │   ├── structured_data.py    # Companies, prices, clients
│   │   ├── unstructured_data.py  # Documents via cortex.complete()
│   │   └── event_log.py          # Master event generation
│   ├── ai_components/
│   │   ├── semantic_views.py     # CREATE SEMANTIC VIEW statements (see semantic-views.mdc)
│   │   ├── search_services.py    # CREATE CORTEX SEARCH statements (see cortex-search.mdc)
│   │   └── agents.py             # Agent configuration templates
│   └── utils/
│       ├── snowpark_session.py   # Session management
│       ├── validation.py         # Data quality checks
│       └── date_utils.py          # Dynamic date generation utilities
└── sql/
    ├── schemas.sql               # Database and schema creation
    └── cleanup.sql               # Reset/cleanup scripts
```

## File Naming Conventions
- Python files: snake_case.py
- SQL files: snake_case.sql
- Configuration: config.py (single file)
- No spaces or special characters in filenames

## Import Standards
- Use relative imports within src/
- Import snowflake.snowpark functions explicitly
- Import snowflake.cortex.complete for text generation
- Always import from config import DemoConfig
- **CRITICAL**: Import dynamic date utilities for all time-based data:
  ```python
  from utils.date_utils import get_historical_quarters, get_dynamic_date_range
  ```

## Documentation Requirements
- Docstrings for all functions
- README with setup instructions
- Inline comments for complex business logic
- Agent configuration examples in agents.py