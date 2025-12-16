# Snowflake Connection Setup

## What is `your_connection`?

In all demo commands, you'll see:
```bash
snowsql -c your_connection -f sql/00_setup_infrastructure.sql
```

**`your_connection` is a placeholder** - replace it with your actual Snowflake connection name.

## Setting Up connections.toml

### Step 1: Create the configuration file

```bash
# Create directory if it doesn't exist
mkdir -p ~/.snowflake

# Create or edit connections.toml
nano ~/.snowflake/connections.toml
```

### Step 2: Add your connection

Add this to `~/.snowflake/connections.toml`:

```toml
[factset_demo]
account = "your-account-identifier"    # e.g., "xy12345.us-east-1"
user = "your-username"                 # Your Snowflake username
password = "your-password"             # Your Snowflake password
role = "ACCOUNTADMIN"                  # Role to use
warehouse = "DATA_ENG_XFORM_WH"        # Warehouse (will be created)
database = "DATA_ENG_DEMO"             # Database (will be created)
schema = "FACTSET"                     # Schema (will be created)
```

### Step 3: Test your connection

```bash
snowsql -c factset_demo -q "SELECT CURRENT_VERSION()"
```

If this works, you're all set!

## Using Your Connection

Now in all demo commands, replace `your_connection` with `factset_demo`:

```bash
# Infrastructure setup
snowsql -c factset_demo -f sql/00_setup_infrastructure.sql

# Demo setup
cd demos/factset_etf_iceberg
snowsql -c factset_demo -f config_factset.sql
snowsql -c factset_demo -f sql/00_initialization.sql

# Deploy pipelines
snowsql -c factset_demo -f sql/01_pipeline_stream_task_iceberg.sql
snowsql -c factset_demo -f sql/02_pipeline_stream_task_iceberg_parquet.sql
```

## Finding Your Account Identifier

If you don't know your Snowflake account identifier:

1. **Log into Snowflake Web UI**
2. **Look at the URL**: `https://APP.REGION.CLOUD.snowflakecomputing.com/`
3. **Your account is**: `APP.REGION.CLOUD` or just `APP`

Example:
- URL: `https://xy12345.us-east-1.aws.snowflakecomputing.com/`
- Account: `xy12345.us-east-1` or `xy12345`

## Alternative: Use Default Connection

You can also set up a default connection:

```toml
[connections.default]
account = "your-account"
user = "your-username"
password = "your-password"
role = "ACCOUNTADMIN"
```

Then run commands without specifying `-c`:

```bash
snowsql -f sql/00_setup_infrastructure.sql
```

## Security Note

**Never commit connections.toml to Git!** It contains your password.

The `.gitignore` file already excludes it:
```
connections.toml
.snowflake/
```

## Troubleshooting

### "Connection not found"
**Problem:** SnowSQL can't find your connection name

**Solution:** Check that the name in brackets `[factset_demo]` matches what you use in `-c factset_demo`

### "Authentication failed"
**Problem:** Invalid credentials

**Solution:** 
- Verify account identifier format
- Check username/password
- Try logging into Snowflake Web UI with same credentials

### "File not found: ~/.snowflake/connections.toml"
**Problem:** File doesn't exist

**Solution:** Create it using the steps above

## Quick Reference

**File Location:** `~/.snowflake/connections.toml`  
**Format:** TOML configuration  
**Sections:** `[connection_name]`  
**Usage:** `snowsql -c connection_name`

---

**For more details:** https://docs.snowflake.com/en/user-guide/snowsql-config

