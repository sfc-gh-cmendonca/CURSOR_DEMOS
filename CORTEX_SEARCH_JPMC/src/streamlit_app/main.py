"""Main Streamlit application for JPMC Cortex Search Lab."""

import streamlit as st
import sys
from pathlib import Path

# Add src to path to enable imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config.settings import (
    app_settings, 
    streamlit_settings,
    validate_settings
)
from loguru import logger


def configure_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title=app_settings.app_name,
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/jpmorganchase/cortex-search-lab',
            'Report a bug': "https://github.com/jpmorganchase/cortex-search-lab/issues",
            'About': f"# {app_settings.app_name}\nVersion {app_settings.app_version}"
        }
    )


def show_error_page(error_message: str):
    """Display an error page when configuration is invalid."""
    st.error("⚠️ Configuration Error")
    st.write(f"**Error:** {error_message}")
    
    st.markdown("""
    ### Setup Instructions
    
    1. **Copy the environment template:**
       ```bash
       cp env.template .env
       ```
    
    2. **Edit the .env file with your Snowflake credentials:**
       ```bash
       SNOWFLAKE_ACCOUNT=your_account_identifier
       SNOWFLAKE_USER=your_username  
       SNOWFLAKE_PASSWORD=your_password
       SNOWFLAKE_ROLE=CORTEX_USER_ROLE
       SNOWFLAKE_WAREHOUSE=COMPUTE_WH
       SNOWFLAKE_DATABASE=JPMC_MARKETS
       SNOWFLAKE_SCHEMA=MARKET_INTELLIGENCE
       ```
    
    3. **Restart the application:**
       ```bash
       streamlit run src/streamlit_app/main.py
       ```
    """)


def show_welcome_page():
    """Display the main welcome page."""
    st.title(f"🏦 {app_settings.app_name}")
    st.subheader("Snowflake Cortex Search Lab for Financial Markets")
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        Welcome to the **JPMC Markets Team Cortex Search Lab**! This application demonstrates 
        the power of Snowflake Cortex Search for financial markets data and research.
        
        ### 🎯 What You'll Learn
        - Build sophisticated search engines for market research
        - Create AI-powered trading assistants using RAG
        - Implement advanced filtering for financial data
        - Deploy production-ready Streamlit applications
        """)
        
        # Status indicators
        st.markdown("### 📊 System Status")
        
        # Check database connection
        try:
            from src.database.connection import connection_manager
            if connection_manager.test_connection():
                st.success("✅ Snowflake connection established")
            else:
                st.error("❌ Snowflake connection failed")
        except Exception as e:
            st.error(f"❌ Database connection error: {str(e)}")
    
    with col2:
        st.info("""
        **Quick Start:**
        1. ✅ Configure .env file
        2. 🔗 Test Snowflake connection  
        3. 📊 Load sample data
        4. 🔍 Try semantic search
        5. 🤖 Chat with AI assistant
        """)
        
        # Application info
        st.markdown("---")
        st.caption(f"Version: {app_settings.app_version}")
        st.caption(f"Environment: {'Development' if app_settings.debug_mode else 'Production'}")
    
    # Feature preview cards
    st.markdown("### 🚀 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 Multi-Source Search**
        - Research reports
        - Trading insights  
        - Economic indicators
        - Real-time market data
        """)
    
    with col2:
        st.markdown("""
        **🤖 AI Trading Assistant**
        - RAG-powered responses
        - Context-aware insights
        - Source citations
        - Risk-level filtering
        """)
    
    with col3:
        st.markdown("""
        **📈 Analytics Dashboard**
        - Interactive visualizations
        - Performance metrics
        - User behavior tracking
        - Real-time updates
        """)
    
    # Getting started section
    st.markdown("### 🏁 Getting Started")
    
    with st.expander("📚 Lab Documentation", expanded=False):
        st.markdown("""
        Access the complete lab guide in the `CORTEX_SEARCH_JPMC/` directory:
        
        - **Part 1:** Environment Setup and Data Preparation
        - **Part 2:** Building Market Research Search  
        - **Part 3:** Creating Trading Insights Chatbot
        - **Part 4:** Advanced Filtering and Analytics
        - **Part 5:** Streamlit Application Deployment
        """)
    
    with st.expander("⚙️ Configuration Help", expanded=False):
        st.markdown("""
        Need help with configuration? Check these common issues:
        
        **Connection Issues:**
        - Verify your Snowflake account identifier
        - Check username and password
        - Ensure proper role permissions
        
        **Performance Issues:**  
        - Adjust warehouse size
        - Enable query result caching
        - Optimize clustering keys
        
        **Security Setup:**
        - Configure network policies
        - Enable SSO if available
        - Set up proper RBAC
        """)


def main():
    """Main application entry point."""
    try:
        # Configure page first
        configure_page()
        
        # Validate configuration
        if not validate_settings():
            show_error_page("Invalid configuration detected. Please check your .env file.")
            return
        
        # Add custom CSS for styling
        st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
        }
        .stAlert > div {
            padding: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Show main application
        show_welcome_page()
        
        # Sidebar navigation (placeholder for future features)
        with st.sidebar:
            st.markdown("### 🧭 Navigation")
            
            # Future navigation items
            nav_options = [
                "🏠 Home",
                "🔍 Document Search", 
                "🤖 AI Assistant",
                "📊 Analytics",
                "⚙️ Settings"
            ]
            
            selected = st.selectbox("Choose a section:", nav_options)
            
            if selected != "🏠 Home":
                st.info(f"**{selected}** is coming soon! This lab focuses on the foundation setup.")
            
            st.markdown("---")
            st.markdown("### 📖 Resources")
            st.markdown("""
            - [Snowflake Docs](https://docs.snowflake.com/)
            - [Cortex Search Guide](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)
            - [Streamlit Docs](https://docs.streamlit.io/)
            """)
        
        logger.info("Streamlit application loaded successfully")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"Application Error: {str(e)}")
        
        if app_settings.debug_mode:
            st.exception(e)


if __name__ == "__main__":
    main() 