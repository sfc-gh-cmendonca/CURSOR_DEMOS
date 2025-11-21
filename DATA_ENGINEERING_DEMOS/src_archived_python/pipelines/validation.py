"""
Data Quality Validation Pipeline
Implements comprehensive data quality checks
"""
from snowflake.snowpark import Session
from config import DataEngDemoConfig
from utils.logging_utils import setup_logger, log_step, log_metrics

logger = setup_logger("validation")


def run_data_quality_checks(session: Session, table_name: str, schema_name: str = None) -> dict:
    """
    Run comprehensive data quality checks on a table
    
    Args:
        session: Active Snowpark session
        table_name: Name of table to validate
        schema_name: Schema name (uses CURATED if not specified)
    
    Returns:
        Dictionary with quality metrics and pass/fail status
    
    Quality checks performed:
        - NULL value checks
        - Duplicate record detection
        - Referential integrity
        - Value range validation
        - Format validation
    """
    if schema_name is None:
        schema_name = DataEngDemoConfig.SCHEMA_CURATED
    
    full_table_name = f"{DataEngDemoConfig.DATABASE}.{schema_name}.{table_name}"
    
    log_step(logger, f"Data Quality Checks: {table_name}", "START")
    
    results = {
        "table_name": full_table_name,
        "checks_passed": 0,
        "checks_failed": 0,
        "total_rows": 0,
        "quality_score": 0.0,
        "issues": []
    }
    
    # Get total row count
    results["total_rows"] = session.table(full_table_name).count()
    logger.info(f"Total rows in table: {results['total_rows']:,}")
    
    # Run table-specific checks
    if table_name == "CUSTOMERS":
        _check_customers(session, full_table_name, results)
    elif table_name == "PRODUCTS":
        _check_products(session, full_table_name, results)
    elif table_name == "TRANSACTIONS":
        _check_transactions(session, full_table_name, results)
    
    # Calculate quality score
    total_checks = results["checks_passed"] + results["checks_failed"]
    if total_checks > 0:
        results["quality_score"] = (results["checks_passed"] / total_checks) * 100
    
    # Log results
    log_metrics(logger, {
        "Total Checks": total_checks,
        "Passed": results["checks_passed"],
        "Failed": results["checks_failed"],
        "Quality Score": f"{results['quality_score']:.1f}%"
    })
    
    # Show issues
    if results["issues"]:
        logger.warning(f"⚠️  Found {len(results['issues'])} data quality issues:")
        for issue in results["issues"]:
            logger.warning(f"   - {issue}")
    
    # Determine overall status
    threshold = DataEngDemoConfig.QUALITY_THRESHOLD_PASS
    if results["quality_score"] >= threshold * 100:
        log_step(logger, f"Data Quality Checks: {table_name}", "COMPLETE")
    else:
        logger.warning(f"⚠️  Quality score below threshold ({threshold * 100}%)")
        log_step(logger, f"Data Quality Checks: {table_name}", "WARNING")
    
    return results


def _check_customers(session: Session, table_name: str, results: dict) -> None:
    """Run customer-specific data quality checks"""
    logger.info("Running CUSTOMERS quality checks...")
    
    # Check 1: Primary key nulls
    null_ids = session.sql(f"""
        SELECT COUNT(*) as cnt FROM {table_name} WHERE CUSTOMER_ID IS NULL
    """).collect()[0]['CNT']
    
    if null_ids == 0:
        results["checks_passed"] += 1
        logger.info("✅ No NULL customer IDs")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{null_ids} NULL customer IDs found")
    
    # Check 2: Duplicate customer IDs
    duplicates = session.sql(f"""
        SELECT COUNT(*) as cnt FROM (
            SELECT CUSTOMER_ID, COUNT(*) as dup_count
            FROM {table_name}
            GROUP BY CUSTOMER_ID
            HAVING COUNT(*) > 1
        )
    """).collect()[0]['CNT']
    
    if duplicates == 0:
        results["checks_passed"] += 1
        logger.info("✅ No duplicate customer IDs")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{duplicates} duplicate customer IDs found")
    
    # Check 3: Email format validation
    invalid_emails = session.sql(f"""
        SELECT COUNT(*) as cnt 
        FROM {table_name} 
        WHERE EMAIL IS NOT NULL 
        AND NOT REGEXP_LIKE(EMAIL, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$')
    """).collect()[0]['CNT']
    
    if invalid_emails == 0:
        results["checks_passed"] += 1
        logger.info("✅ All emails properly formatted")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{invalid_emails} invalid email formats found")
    
    # Check 4: Lifetime value range
    invalid_ltv = session.sql(f"""
        SELECT COUNT(*) as cnt 
        FROM {table_name} 
        WHERE LIFETIME_VALUE IS NULL OR LIFETIME_VALUE < 0
    """).collect()[0]['CNT']
    
    if invalid_ltv == 0:
        results["checks_passed"] += 1
        logger.info("✅ All lifetime values valid")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{invalid_ltv} invalid lifetime values found")


def _check_products(session: Session, table_name: str, results: dict) -> None:
    """Run product-specific data quality checks"""
    logger.info("Running PRODUCTS quality checks...")
    
    # Check 1: Primary key nulls
    null_ids = session.sql(f"""
        SELECT COUNT(*) as cnt FROM {table_name} WHERE PRODUCT_ID IS NULL
    """).collect()[0]['CNT']
    
    if null_ids == 0:
        results["checks_passed"] += 1
        logger.info("✅ No NULL product IDs")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{null_ids} NULL product IDs found")
    
    # Check 2: Price validation
    invalid_prices = session.sql(f"""
        SELECT COUNT(*) as cnt 
        FROM {table_name} 
        WHERE UNIT_PRICE IS NULL OR UNIT_PRICE <= 0
    """).collect()[0]['CNT']
    
    if invalid_prices == 0:
        results["checks_passed"] += 1
        logger.info("✅ All prices valid")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{invalid_prices} invalid prices found")
    
    # Check 3: Cost vs Price validation
    cost_errors = session.sql(f"""
        SELECT COUNT(*) as cnt 
        FROM {table_name} 
        WHERE COST > UNIT_PRICE
    """).collect()[0]['CNT']
    
    if cost_errors == 0:
        results["checks_passed"] += 1
        logger.info("✅ All cost/price relationships valid")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{cost_errors} products with cost > price found")


def _check_transactions(session: Session, table_name: str, results: dict) -> None:
    """Run transaction-specific data quality checks"""
    logger.info("Running TRANSACTIONS quality checks...")
    
    # Check 1: Primary key nulls
    null_ids = session.sql(f"""
        SELECT COUNT(*) as cnt FROM {table_name} WHERE TRANSACTION_ID IS NULL
    """).collect()[0]['CNT']
    
    if null_ids == 0:
        results["checks_passed"] += 1
        logger.info("✅ No NULL transaction IDs")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{null_ids} NULL transaction IDs found")
    
    # Check 2: Foreign key integrity (customers)
    orphan_customers = session.sql(f"""
        SELECT COUNT(*) as cnt 
        FROM {table_name} t
        LEFT JOIN {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.CUSTOMERS c
            ON t.CUSTOMER_ID = c.CUSTOMER_ID
        WHERE t.CUSTOMER_ID IS NOT NULL AND c.CUSTOMER_ID IS NULL
    """).collect()[0]['CNT']
    
    if orphan_customers == 0:
        results["checks_passed"] += 1
        logger.info("✅ All customer references valid")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{orphan_customers} transactions with invalid customer IDs")
    
    # Check 3: Foreign key integrity (products)
    orphan_products = session.sql(f"""
        SELECT COUNT(*) as cnt 
        FROM {table_name} t
        LEFT JOIN {DataEngDemoConfig.DATABASE}.{DataEngDemoConfig.SCHEMA_CURATED}.PRODUCTS p
            ON t.PRODUCT_ID = p.PRODUCT_ID
        WHERE t.PRODUCT_ID IS NOT NULL AND p.PRODUCT_ID IS NULL
    """).collect()[0]['CNT']
    
    if orphan_products == 0:
        results["checks_passed"] += 1
        logger.info("✅ All product references valid")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{orphan_products} transactions with invalid product IDs")
    
    # Check 4: Amount validation
    invalid_amounts = session.sql(f"""
        SELECT COUNT(*) as cnt 
        FROM {table_name} 
        WHERE TOTAL_AMOUNT IS NULL OR TOTAL_AMOUNT <= 0
    """).collect()[0]['CNT']
    
    if invalid_amounts == 0:
        results["checks_passed"] += 1
        logger.info("✅ All transaction amounts valid")
    else:
        results["checks_failed"] += 1
        results["issues"].append(f"{invalid_amounts} invalid transaction amounts found")


if __name__ == "__main__":
    from utils.snowpark_session import get_snowpark_session, set_context
    
    session = get_snowpark_session()
    set_context(session, database=DataEngDemoConfig.DATABASE)
    
    # Run checks on all curated tables
    for table in ["CUSTOMERS", "PRODUCTS", "TRANSACTIONS"]:
        results = run_data_quality_checks(session, table)
        print(f"\n{table} Quality Score: {results['quality_score']:.1f}%\n")
    
    session.close()

