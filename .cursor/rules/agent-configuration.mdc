---
description: Agent setup patterns and instruction templates for Snowflake Intelligence
---

# Agent Configuration Standards

## Agent Architecture
- **4 separate agents**: One per demo scenario for maximum modularity
- **Multiple tools per agent**: Combine Cortex Analyst + Cortex Search as needed
- **Deterministic behavior**: Use specific tool descriptions and when-to-use rules

## Agent Naming Pattern
- Scenario-based names: "Earnings_Analysis_Agent", "Thematic_Research_Agent", etc.
- Display names: User-friendly versions for the UI
- Descriptions: Clear business context and capabilities

## Standard Agent Template
```
Agent Name: {scenario_name}_agent
Display Name: {User Friendly Name}
Description: {Business context and capabilities}
Orchestration Model: Claude 4

Tools:
  - {semantic_view_name} (Cortex Analyst)
  - search_{document_type} (Cortex Search)

Planning Instructions: {Specific tool selection logic with when-to-use rules}
Response Instructions: {Tone, format, and output guidelines}
```

## Tool Description Requirements
- **Cortex Analyst tools**: Specify exactly what data/metrics are available
- **Cortex Search tools**: Specify document types and search capabilities
- **When-to-use rules**: Clear conditions for tool selection
- **Examples**: Include sample queries each tool can handle

## Instruction Guidelines
- **Planning Instructions**: Focus on tool selection logic
- **Response Instructions**: Define tone, format, citation requirements
- **Deterministic logic**: Avoid ambiguous guidance, use explicit decision trees
- **Demo-ready**: Instructions should ensure consistent, impressive responses