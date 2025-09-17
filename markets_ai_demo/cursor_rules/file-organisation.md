# Project Structure and File Organization Standards

## Repository Structure Standards

### Top-Level Organization
```
PROJECT_ROOT/
├── README.md                          # Project overview and quick start
├── cursor_rules/                      # AI development rules (this directory)
├── {demo_name}/                       # Main demo directory
│   ├── README.md                     # Comprehensive demo documentation
│   ├── requirements.txt              # Python dependencies
│   ├── scripts/                      # Deployment and automation
│   ├── docs/                         # Complete documentation suite
│   ├── agents/                       # Agent configuration templates
│   ├── tests/                        # Validation and testing
│   └── cursor_rules/                 # Demo-specific rules (copy)
└── .gitignore                        # Git ignore patterns
```

### Demo Directory Structure (Mandatory Pattern)
Based on FSI demos repository structure for professional consistency:

```
{demo_name}/
├── README.md                         # Comprehensive demo description
├── requirements.txt                  # Python dependencies with versions
├── scripts/                         # Deployment and automation tools
│   ├── deploy_{demo_name}.py        # Main deployment script
│   ├── cleanup_{demo_name}.py       # Multi-level cleanup automation
│   ├── validate_{demo_name}.py      # Deployment validation
│   └── utils/                       # Common utilities
│       ├── __init__.py
│       ├── connection.py            # Database connection handling
│       ├── date_utils.py            # Dynamic date generation
│       └── data_generation.py       # Synthetic data creation
├── docs/                            # Complete documentation suite
│   ├── setup_guide.md               # Detailed setup instructions
│   ├── agent_setup_instructions.md  # Agent configuration guide
│   ├── demo_scripts.md              # Professional demo scenarios
│   ├── architecture.md              # Technical architecture overview
│   └── troubleshooting.md           # Common issues and solutions
├── agents/                          # Agent configuration templates
│   ├── README.md                    # Agent configuration overview
│   ├── {agent_name}_config.yaml    # Agent configuration files
│   └── templates/                   # Reusable agent templates
├── tests/                           # Validation and testing
│   ├── __init__.py
│   ├── test_deployment.py           # Deployment validation tests
│   ├── test_agents.py               # Agent functionality tests
│   ├── test_data_quality.py         # Data quality validation
│   └── fixtures/                    # Test data and fixtures
├── sql/                             # SQL scripts and schemas
│   ├── 01_database_setup.sql        # Database and schema creation
│   ├── 02_tables.sql                # Table definitions
│   ├── 03_semantic_views.sql        # Semantic view creation
│   ├── 04_search_services.sql       # Cortex Search services
│   └── 99_cleanup.sql               # Cleanup scripts
└── data/                           # Sample data files (if needed)
    ├── README.md                    # Data description and sources
    ├── companies.csv                # Reference data
    └── sample_data/                 # Sample datasets
```

## File Naming Conventions

### Python Files
- **Scripts**: `{action}_{component}.py` (e.g., `deploy_dual_tool_demo.py`)
- **Utilities**: `{component}_utils.py` (e.g., `date_utils.py`)
- **Tests**: `test_{component}.py` (e.g., `test_deployment.py`)
- **Classes**: `{ComponentName}.py` using PascalCase

### Documentation Files
- **Guides**: `{purpose}_guide.md` (e.g., `setup_guide.md`)
- **Instructions**: `{component}_instructions.md` (e.g., `agent_setup_instructions.md`)
- **References**: `{component}_reference.md` (e.g., `api_reference.md`)

### SQL Files
- **Numbered sequence**: `{order}_{purpose}.sql` (e.g., `01_database_setup.sql`)
- **Component-based**: `{component}_{action}.sql` (e.g., `semantic_views_create.sql`)

### Configuration Files
- **YAML configs**: `{component}_config.yaml` (e.g., `agent_config.yaml`)
- **Environment**: `.env.{environment}` (e.g., `.env.development`)

## Content Organization Standards

### README.md Structure (Repository Root)
```markdown
# Project Title
Brief description and purpose

## 📁 Demos
List of available demos with links

## 🚀 Quick Start
Basic usage instructions

## 🔧 Development
Development setup and patterns

## 📚 Documentation
Links to detailed documentation

## 🤝 Contributing
Contribution guidelines
```

### README.md Structure (Demo Directory)
```markdown
# Demo Title - Platform Name
Subtitle with key technology

## 🎯 Demo Overview
Business context and scenarios

## 🏗️ Architecture Overview
Technical architecture with diagrams

## 📊 Data Architecture
Database structure and data model

## 🤖 AI Agent Capabilities
Agent descriptions and use cases

## 🚀 Quick Start Guide
Step-by-step deployment

## 🎪 Demo Highlights
Key demo scenarios and value prop

## 🧹 Management & Cleanup
Cleanup options and maintenance

## 📚 Documentation
Links to detailed guides
```

### Script File Structure
```python
#!/usr/bin/env python3
"""
Script Title - Brief Description
================================

Detailed description of script purpose and functionality.
"""

import statements (grouped: stdlib, third-party, local)

# Configuration constants
CONFIG_SECTION = {
    'key': 'value'
}

class ComponentName:
    """Class docstring with purpose and usage."""
    
    def __init__(self):
        """Initialize with configuration."""
        pass
    
    def public_method(self):
        """Public method with clear docstring."""
        pass
    
    def _private_method(self):
        """Private method for internal use."""
        pass

def main():
    """Main execution function."""
    pass

if __name__ == "__main__":
    main()
```

### Documentation File Structure
```markdown
# Title
Brief description

## Prerequisites
Required setup and dependencies

## Step-by-Step Instructions
Numbered steps with code blocks

## Configuration Options
Available settings and customization

## Troubleshooting
Common issues and solutions

## Examples
Working examples with expected output

## Reference
Links to additional resources
```

## Version Control Standards

### .gitignore Patterns
```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment
.env
.env.local
.env.development
.env.production

# Snowflake
connections.toml
*.key
*.pem

# Data files (if large)
data/*.csv
data/*.json
data/*.parquet

# Temporary files
tmp/
temp/
*.tmp
```

### Commit Message Standards
```
type: Brief description (50 chars max)

Detailed explanation if needed (wrap at 72 chars):
- What changes were made
- Why changes were necessary
- Any breaking changes or considerations

Types: feat, fix, docs, style, refactor, test, chore
```

### Branch Naming
- **Feature branches**: `feature/descriptive-name`
- **Bug fixes**: `fix/issue-description`
- **Documentation**: `docs/section-name`
- **Releases**: `release/version-number`

## Quality Standards

### Code Quality Requirements
- **Documentation**: Every public function/class has docstrings
- **Error Handling**: Comprehensive try/catch with specific error messages
- **Logging**: Structured logging with appropriate levels
- **Configuration**: No hardcoded values, use configuration files
- **Testing**: Unit tests for core functionality

### Documentation Quality Requirements
- **Completeness**: All steps documented with expected outcomes
- **Clarity**: Written for target audience skill level
- **Currency**: Updated with code changes
- **Examples**: Working examples with sample output
- **Troubleshooting**: Common issues and solutions included

### File Organization Checklist
- [ ] Directory structure follows FSI demos pattern
- [ ] File naming conventions are consistent
- [ ] README files are comprehensive and current
- [ ] Scripts include proper docstrings and error handling
- [ ] Configuration is externalized and documented
- [ ] Tests cover core functionality
- [ ] Documentation includes troubleshooting guides
- [ ] .gitignore excludes sensitive and generated files

## Maintenance Standards

### Regular Maintenance Tasks
- **Monthly**: Review and update documentation
- **Quarterly**: Update dependencies and test compatibility
- **Per Release**: Update version numbers and changelogs
- **As Needed**: Fix broken links and outdated examples

### Deprecation Process
1. **Mark as deprecated** in documentation
2. **Add deprecation warnings** in code
3. **Provide migration path** in documentation
4. **Remove after grace period** (minimum 2 releases)

### Archival Process
- **Archive unused demos** to separate branch
- **Update main README** to remove archived demos
- **Maintain archive documentation** for reference
- **Provide migration guidance** for archived content
