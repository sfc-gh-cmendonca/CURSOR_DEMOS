---
description: Demo scenario requirements and user interaction patterns
---

# Demo Scenario Standards

## Phase 1 Scenarios (Build First)
1. **Equity Research Analyst - Earnings Analysis**
   - Focus: Accelerating earnings season analysis
   - Tools: Earnings semantic view + transcripts search
   - Duration: 15 minutes standalone

2. **Equity Research Analyst - Thematic Research**
   - Focus: Discovering investment themes from unstructured data
   - Tools: Research reports search + stock data analysis
   - Duration: 15 minutes standalone

## Scenario Independence Requirements
- Each scenario must work without prior context
- No data dependencies between scenarios
- Complete setup/teardown for each scenario
- Self-contained datasets and configurations

## User Interaction Flow Pattern
Each scenario follows a 3-4 question conversation:
1. **Initial Question**: Broad request that demonstrates core capability
2. **Follow-up Question**: Drill down or cross-reference data sources
3. **Visualization Request**: Chart or table generation
4. **Action Item**: Generate summary, report, or recommendation

## Data Requirements Per Scenario
- All agent questions must have supporting synthetic data
- Responses should showcase multiple Snowflake AI features
- Cross-reference capabilities between structured and unstructured data
- Realistic but impressive results that highlight AI value
- **CRITICAL**: All data must use dynamic dates for demo relevance:
  - Earnings questions reference current/recent quarters
  - Market events span realistic timeframes relative to demo date
  - Research reports cite current market conditions
  - Client data reflects recent engagement patterns

## Success Criteria
- Agents respond within 30 seconds
- All visualizations render properly in Snowflake Intelligence
- Responses demonstrate clear business value
- Scenarios can run independently in any order