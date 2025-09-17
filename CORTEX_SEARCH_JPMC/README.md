# JPMC Markets Team - Cortex Search Lab

A sophisticated search and RAG (Retrieval Augmented Generation) application using Snowflake Cortex Search, specifically designed for markets data and financial research use cases.

## 🎯 Objectives

By completing this lab, you will:
- Understand Cortex Search capabilities for financial data
- Build a market research document search engine
- Create a trading insights chatbot using RAG
- Implement advanced filtering for market segments and asset classes
- Deploy a Streamlit application for the Markets team

## 🏗️ Architecture

```
├── CORTEX_SEARCH_JPMC/          # Lab documentation
├── src/                         # Source code
│   ├── config/                  # Configuration modules
│   ├── database/                # Database connection and utilities
│   ├── search/                  # Cortex Search implementation
│   ├── streamlit_app/           # Streamlit application
│   └── utils/                   # Utility functions
├── tests/                       # Test files
├── sql/                         # SQL scripts
├── data/                        # Sample data files
└── docs/                        # Additional documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ 
- Snowflake account with Cortex features enabled
- Access to the `SNOWFLAKE.CORTEX_USER` database role
- Basic SQL knowledge
- Familiarity with financial markets terminology

### Installation

1. **Clone and navigate to the repository:**
   ```bash
   git clone <repository-url>
   cd jpmc-cortex-search-lab
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp env.template .env
   # Edit .env with your Snowflake credentials
   ```

5. **Install development tools (optional):**
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

### Environment Configuration

Edit the `.env` file with your Snowflake connection details:

```bash
# Required Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=CORTEX_USER_ROLE
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=JPMC_MARKETS
SNOWFLAKE_SCHEMA=MARKET_INTELLIGENCE
```

## 📊 Dataset Overview

The lab works with three main datasets:

1. **Market Research Reports** - Equity research, bond analysis, commodity insights
2. **Trading Insights** - Daily market commentary, trade ideas, risk assessments  
3. **Economic Indicators** - Fed minutes, ECB statements, economic data releases

## 🔧 Development Setup

### Code Quality Tools

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing

Run quality checks:
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run tests
pytest tests/
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run quality checks:
```bash
pre-commit install
```

## 🏃‍♂️ Running the Application

### 1. Database Setup

Run the SQL scripts to set up your Snowflake environment:
```sql
-- Execute the scripts in order:
sql/01_setup_database.sql
sql/02_create_tables.sql
sql/03_load_sample_data.sql
sql/04_create_search_services.sql
```

### 2. Launch Streamlit Application

```bash
streamlit run src/streamlit_app/main.py
```

The application will be available at `http://localhost:8501`

### 3. API Usage (Optional)

If you've set up the API components:
```bash
python -m src.api.main
```

## 🔍 Key Features

### Multi-source Search
- Search across research reports, trading insights, and economic indicators
- Semantic search using Snowflake's embedding models
- Advanced filtering by asset class, risk level, and time horizon

### AI-Powered Trading Assistant
- RAG-based chatbot for market queries
- Context-aware responses with source citations
- Real-time market data integration

### Analytics Dashboard
- Interactive visualizations using Plotly
- Performance metrics and search analytics
- User behavior tracking

### Security & Compliance
- Role-based access control (RBAC)
- Secure credential management
- Audit logging for all queries

## 🔒 Security Best Practices

Following the best practices from [Snowflake and Power BI integration](https://medium.com/snowflake/snowflake-and-power-bi-best-practices-and-recent-improvements-183e2d970c0c):

1. **Never hardcode credentials** - Use environment variables
2. **Implement RBAC** - Use appropriate Snowflake roles
3. **Enable SSO** where possible for production deployments
4. **Network policies** - Restrict IP access to Snowflake
5. **Query optimization** - Monitor performance and costs
6. **Data governance** - Implement proper security controls

## 📈 Performance Optimization

Based on Snowflake best practices:

1. **Warehouse Management:**
   - Use dedicated warehouses for different workloads
   - Set appropriate auto-suspension (10+ minutes for BI workloads)
   - Monitor for spilling and adjust sizing accordingly

2. **Query Optimization:**
   - Use clustering keys for large tables
   - Implement materialized views for aggregated data
   - Leverage query result caching

3. **Application Performance:**
   - Use Streamlit caching decorators
   - Implement proper error handling
   - Monitor query execution times

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m "unit"          # Unit tests only
pytest -m "integration"   # Integration tests only
```

## 📚 Additional Resources

- [Snowflake Cortex Search Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [JPMC Python Training Repository](https://github.com/jpmorganchase/python-training)
- [Snowflake Performance Best Practices](https://docs.snowflake.com/en/user-guide/ui-snowsight-query-performance)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## 📄 License

Apache 2.0 - See LICENSE file for details

## 📞 Support

Contact your JPMC Technology Team for support and questions.

---

**Happy Learning! 🚀** 