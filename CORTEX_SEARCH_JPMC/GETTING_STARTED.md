# 🚀 Getting Started with JPMC Cortex Search Lab

Welcome to your **Cortex Search Lab**! This directory is now the root of your demo project, optimized for Snowflake Cortex Search development with Cursor AI.

## 📂 What's in This Directory

```
CORTEX_SEARCH_JPMC/                 # 🏠 You are here (PROJECT ROOT)
├── 📋 JPMC_Cortex_Search_Lab.md    # Complete lab documentation
├── 📖 README.md                    # Project overview and instructions
├── 📋 GETTING_STARTED.md           # This file - your quick start guide
├── ⚙️ setup.py                     # Automated environment setup
├── 📦 requirements.txt             # Python dependencies
├── 🔧 Makefile                     # Development commands
├── 🏗️ pyproject.toml               # Modern Python project config
├── 🔐 env.template                 # Environment configuration template
├── 🛠️ .cursor/                     # Cursor AI configuration
├── 💻 src/                         # Source code
│   ├── config/                     # Configuration management
│   ├── database/                   # Snowflake connections
│   ├── search/                     # Cortex Search implementation
│   ├── streamlit_app/              # Web application
│   └── utils/                      # Helper functions
├── 🧪 tests/                       # Test suite
├── 🗄️ sql/                         # Database setup scripts
├── 📊 data/                        # Sample data
└── 📚 docs/                        # Documentation
```

## ⚡ Quick Start (5 minutes)

### Step 1: Run the Setup Script
```bash
python setup.py
```
This automatically:
- ✅ Creates virtual environment
- ✅ Installs all dependencies  
- ✅ Sets up code quality tools
- ✅ Creates `.env` from template

### Step 2: Configure Snowflake Connection
```bash
# Edit .env file with your Snowflake credentials
nano .env  # or use your preferred editor
```

Required settings:
```env
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=CORTEX_USER_ROLE
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=JPMC_MARKETS
SNOWFLAKE_SCHEMA=MARKET_INTELLIGENCE
```

### Step 3: Test Your Setup
```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Test database connection
make db-test

# Start the Streamlit application
make run-app
```

## 🏗️ Database Setup (Required for Cortex Search)

Execute these SQL scripts in order in your Snowflake environment:

### 1. Database and Schema Setup
```bash
# Execute: sql/01_setup_database.sql
# Creates: JPMC_MARKETS database, MARKET_INTELLIGENCE schema, CORTEX_WH warehouse
```

### 2. Create Tables
```bash
# Execute: sql/02_create_tables.sql  
# Creates: market_research_reports, trading_insights, economic_indicators tables
```

### 3. Create Cortex Search Services
```bash
# Execute: sql/03_create_search_services.sql
# Creates: 4 search services for different document types
```

## 🔍 Cortex Search Services Created

Based on the [official Snowflake Cortex Search documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/query-cortex-search-service), your lab includes:

1. **`market_research_search`** - Search equity research, bond analysis, commodity insights
2. **`trading_insights_search`** - Search daily market commentary and trade ideas  
3. **`economic_indicators_search`** - Search Fed minutes, ECB statements, economic data
4. **`market_intelligence_unified_search`** - Search across all document types

## 🧑‍💻 Development Commands

Your Makefile provides these convenient commands:

```bash
make help           # Show all available commands
make setup          # Run full development setup
make test           # Run all tests
make lint           # Run code linting
make format         # Format code with Black
make type-check     # Run MyPy type checking
make security       # Run security checks
make quality        # Run all quality checks
make run-app        # Start Streamlit application
make run-dev        # Start app in development mode
make clean          # Clean up build artifacts
make db-test        # Test Snowflake connection
```

## 📝 Example: Your First Search

Once you've set up the database and loaded sample data, try this Python example:

```python
from src.search.cortex_search import MarketResearchSearchService

# Create search service
search_service = MarketResearchSearchService()

# Search for AI-related research
results = search_service.search_by_asset_class(
    query="artificial intelligence technology trends",
    asset_class="equity",
    limit=5
)

print(f"Found {results.total_count} results:")
for result in results.results:
    print(f"- {result.content[:100]}... (Score: {result.score})")
```

## 🔧 What's Already Configured

Your workspace includes enterprise-grade configurations:

### ✅ Cursor AI Optimization
- **Smart coding rules** in `.cursor/rules.md`
- **Documentation links** in `.cursor/docs.md` 
- **Optimized for Snowflake development**

### ✅ Code Quality
- **Black** formatting (88 char line length)
- **Flake8** linting with custom rules
- **MyPy** type checking
- **Bandit** security scanning
- **Pre-commit hooks** for automated checks

### ✅ Snowflake Best Practices
- **Environment-based configuration** (no hardcoded credentials)
- **Connection pooling** and keep-alive
- **Query result caching** enabled
- **Proper timeout settings**
- **RBAC support** configured

### ✅ Testing Framework
- **pytest** with coverage reporting
- **Mock fixtures** for Snowflake connections
- **Separate unit and integration tests**

## 🎯 Next Steps

1. **📖 Read the Lab Guide**: Start with `JPMC_Cortex_Search_Lab.md`
2. **🗄️ Set Up Database**: Execute the SQL scripts in order
3. **📊 Load Sample Data**: Follow the lab guide for sample data
4. **🔍 Try Search Examples**: Use the Cortex Search APIs
5. **🤖 Build AI Features**: Extend the Streamlit app
6. **🚀 Deploy**: Follow production deployment guide

## 🆘 Need Help?

- 📘 **Cortex Search Docs**: [Query Cortex Search Service](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/query-cortex-search-service)
- 🔍 **API Examples**: Check `src/search/cortex_search.py` for Python/REST/SQL examples
- 📋 **Lab Guide**: Complete walkthrough in `JPMC_Cortex_Search_Lab.md`
- ⚙️ **Troubleshooting**: See `WORKSPACE_SETUP.md`

## 🎉 You're All Set!

Your Cortex Search lab is ready for development. The workspace follows Snowflake best practices and is optimized for Cursor AI assistance.

**Happy searching! 🔍✨** 