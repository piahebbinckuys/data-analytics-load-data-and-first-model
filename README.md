## Context

In the previous challenge, you installed dbt Core, configured a DuckDB connection, and defined your three Jaffle Shop sources in `schema.yml`. Now you'll put that setup to use: download the raw data, load it into DuckDB, and write your first transformation.

## Objective

Download the Jaffle Shop dataset, load it into DuckDB, and write your first dbt staging model. By the end of this challenge, raw CSV data will be transformed into a clean, documented view using dbt's `source()` macro and the staging layer pattern.

## Prerequisites

- Completed the previous challenge with a working `jaffle_shop_dbt/` directory containing:
  - `dbt_project.yml` configured with materialization and schema settings
  - `models/schema.yml` with source definitions for the three Jaffle Shop tables
  - `~/.dbt/profiles.yml` with a working DuckDB connection (`dbt debug` passes)
  - `../../dbt-shared/dev.duckdb` shared database created

## 0. Copy Your Work from Previous Challenge

Each challenge has its own directory. Copy your dbt project files from the previous challenge.

**📍 In your terminal:**

```bash
cp -rP ../../../{{ local_path_to("03-Data-Transformation/09-Data-Layers-And-Intro-DBT/01-Setup-DBT") }}/jaffle_shop_dbt .

# Verify the symlink copied correctly
ls -l jaffle_shop_dbt/dev.duckdb
# Should show: dev.duckdb -> ../../../dbt-shared/dev.duckdb
```

Then commit so you have a clean starting point for this challenge:

```bash
git add jaffle_shop_dbt
git commit -m "Copied setup from previous challenge"
git push origin master
```

<details>
<summary markdown="span">**💡 Why does the database carry over automatically?**</summary>

The `dev.duckdb` file in your project is a symlink pointing to `../../../dbt-shared/dev.duckdb` (three levels up, into the shared `dbt-shared/` folder in `03-Data-Transformation/`). The `-P` flag in `cp -rP` tells both macOS and Linux/WSL to copy the symlink itself rather than dereference it. Because all challenge directories sit at the same depth under their unit folder, the relative path still resolves to the same shared database — no recreation needed.

</details>

## 1. Load Raw Data into DuckDB

Now we'll download the Jaffle Shop dataset from dbt Labs' GitHub and load it into DuckDB.

### Step 1: Download Data from GitHub

**📍 In your terminal**, download the CSV files:

```bash
# Create data directory
mkdir -p jaffle_shop_dbt/data

# Download Jaffle Shop CSV files from dbt Labs
curl -o jaffle_shop_dbt/data/raw_customers.csv \
  https://raw.githubusercontent.com/dbt-labs/jaffle_shop/main/seeds/raw_customers.csv

curl -o jaffle_shop_dbt/data/raw_orders.csv \
  https://raw.githubusercontent.com/dbt-labs/jaffle_shop/main/seeds/raw_orders.csv

curl -o jaffle_shop_dbt/data/raw_payments.csv \
  https://raw.githubusercontent.com/dbt-labs/jaffle_shop/main/seeds/raw_payments.csv

# Verify downloads succeeded
ls -lh jaffle_shop_dbt/data/
# Should show: raw_customers.csv, raw_orders.csv, raw_payments.csv (~6KB total)
```

Raw data files should not be committed — they can always be re-downloaded from source. Add the `data/` directory to `.gitignore` and commit:

```bash
echo "data/" >> jaffle_shop_dbt/.gitignore
git add jaffle_shop_dbt/.gitignore
git commit -m "Ignore raw data files"
git push origin master
```

### Step 2: Connect DBeaver to Your Shared Database

Connect DBeaver to the shared database location. This connection will work for **all future challenges** - you'll never need to update the path!

**Connect to your database:**

1. **Install DBeaver Community** if you haven't already — download it from [dbeaver.io/download](https://dbeaver.io/download/) and run the installer for your operating system.

1. **Launch DBeaver**

1. **Click "New Database Connection"** (plug icon in toolbar)
  <img src="https://wagon-public-datasets.s3.amazonaws.com/data-analytics/03-Data-Transformation/09-Intro-to-DBT/dbeaver-new-db-connection.png" alt="DBeaver new database connection button" width="40%">

1. **Search for and select "DuckDB"**
  <img src="https://wagon-public-datasets.s3.amazonaws.com/data-analytics/03-Data-Transformation/09-Intro-to-DBT/dbeaver-select-duckdb.png" alt="DBeaver database selection showing DuckDB" width="40%">

1. **Click "Next"**

1. **Enter the path to your shared database.** Run the appropriate command for your system to get the absolute path:

   **macOS / Linux:**

   ```bash
   readlink -f ../../dbt-shared/dev.duckdb
   ```

   **Windows (WSL):**

   ```bash
   wslpath -w $(readlink -f ../../dbt-shared/dev.duckdb)
   ```

   Copy the output and paste it into the **Path** field in DBeaver. It should end up looking like this:
   <img src="https://wagon-public-datasets.s3.amazonaws.com/data-analytics/03-Data-Transformation/09-Intro-to-DBT/dbeaver-select-devduckdb.png" alt="DBeaver connection settings with dev.duckdb database name" width="40%">

1. **Set "Connection name" to "jaffle_shop_shared"** (select `Connection Details` tab to edit)

1. **Click "Test Connection"** → Should say "Connected"
  <img src="https://wagon-public-datasets.s3.amazonaws.com/data-analytics/03-Data-Transformation/09-Intro-to-DBT/dbeaver-test-connection.png" alt="DBeaver test connection dialog showing Connected status" width="40%">

1. **Click "Finish"
  <img src="https://wagon-public-datasets.s3.amazonaws.com/data-analytics/03-Data-Transformation/09-Intro-to-DBT/dbeaver-duckdb-connected.png" alt="DBeaver database navigator showing connected DuckDB database" height="300px">

**Success!** Your DBeaver connection is now established. This connection will work for all dbt challenges - no more path updates needed!

<details>
<summary markdown="span">**🔧 Troubleshooting: Can't connect DBeaver**</summary>

### "DuckDB Driver not found"

**🗄️ In DBeaver:**

1. When prompted "Download DuckDB driver?", click "Download"
2. Wait for download to complete (may take 30-60 seconds)
3. Try "Test Connection" again

### "Connection failed" or "Database not found"

**Check file path is correct:**

**📍 In your terminal:**

**macOS / Linux:**

```bash
readlink -f ../../dbt-shared/dev.duckdb
```

**Windows (WSL):**

```bash
wslpath -w $(readlink -f ../../dbt-shared/dev.duckdb)
```

**🗄️ In DBeaver:**

1. Copy the output path
2. Paste into "Path" field
3. Try "Test Connection" again

### Still can't connect?

**📍 Verify the database file exists:**

```bash
# Check the symlink exists
ls -l jaffle_shop_dbt/dev.duckdb
# Should show: dev.duckdb -> ../../../dbt-shared/dev.duckdb

# Check the actual database exists
ls -lh ../../dbt-shared/dev.duckdb
# Should show the file with size (not empty)
```

</details>

### Step 3: Load Data into DuckDB

**Before you run the SQL below, let's understand what it does:**

1. `CREATE SCHEMA IF NOT EXISTS raw;`
   - Creates a "folder" for organizing tables
   - `IF NOT EXISTS` prevents errors if schema already exists

2. `read_csv_auto('path/to/file.csv')`
   - DuckDB function that reads CSV files
   - "auto" means it detects column types automatically
   - Super useful for quick CSV imports!

3. `CREATE TABLE ... AS SELECT * FROM read_csv_auto(...)`
   - Creates a permanent table from the CSV data
   - `AS SELECT` pattern: create table from query results

**This pattern is useful whenever you need to load CSV files into any database!**

**🗄️ In DBeaver**, open the Database Navigator (left sidebar):

1. **Right-click your `jaffle_shop_shared` connection** > `SQL Editor` > `New SQL Script`

1. **Copy and paste** the SQL below into the file, replacing `YOUR_FULL_PATH_HERE` with the absolute path to your `jaffle_shop_dbt/data` directory (the one containing the CSV files):

  **First, get your absolute path:**

  **📍 In your terminal**, get the absolute path to your data directory (make sure you are still in the correct challenge directory):

  **macOS / Linux:**

  ```bash
  readlink -f jaffle_shop_dbt/data
  ```

  **Windows (WSL):**

  ```bash
  wslpath -w $(readlink -f jaffle_shop_dbt/data)
  ```

  Now copy the SQL below, paste it into the DBeaver SQL editor, and replace `YOUR_FULL_PATH_HERE` with the path you just copied from the terminal

  ```sql
  -- Create schema for raw data
  CREATE SCHEMA IF NOT EXISTS raw;

  -- Load customers (replace YOUR_FULL_PATH_HERE with your actual path)
  CREATE TABLE raw.raw_customers AS
  SELECT * FROM read_csv_auto('YOUR_FULL_PATH_HERE/raw_customers.csv');

  -- Load orders
  CREATE TABLE raw.raw_orders AS
  SELECT * FROM read_csv_auto('YOUR_FULL_PATH_HERE/raw_orders.csv');

  -- Load payments
  CREATE TABLE raw.raw_payments AS
  SELECT * FROM read_csv_auto('YOUR_FULL_PATH_HERE/raw_payments.csv');

  -- Verify data loaded
  SELECT 'customers' as table_name, COUNT(*) as row_count FROM raw.raw_customers
  UNION ALL
  SELECT 'orders', COUNT(*) FROM raw.raw_orders
  UNION ALL
  SELECT 'payments', COUNT(*) FROM raw.raw_payments;
  ```

1. **Run the entire script** by clicking the **Execute SQL Script** button (third button in the SQL editor toolbar)

1. Check the results panel below the editor for the row counts of each table. Results will appear in the DBeaver results panel below your query.

  You should see:

  ```bash
  table_name | row_count
  -----------|----------
  customers  | 100
  orders     | 99
  payments   | 113
  ```

  <img src="https://wagon-public-datasets.s3.amazonaws.com/data-analytics/03-Data-Transformation/09-Intro-to-DBT/dbeaver-new-sql-script.png" alt="DBeaver new SQL script editor" width="40%">

<details>
<summary markdown="span">**🔧 Troubleshooting: Data Loading Issues**</summary>

### Row counts don't match (not 100/99/113)

**Problem:** CSV files may be incomplete or corrupted

**📍 In your terminal**, move to the data folder:

```bash
cd jaffle_shop_dbt/data
```

Then remove the existing CSVs and re-download the files from GitHub:

```bash
rm *.csv

# Re-download from GitHub
curl -o raw_customers.csv https://raw.githubusercontent.com/dbt-labs/jaffle_shop/main/seeds/raw_customers.csv
curl -o raw_orders.csv https://raw.githubusercontent.com/dbt-labs/jaffle_shop/main/seeds/raw_orders.csv
curl -o raw_payments.csv https://raw.githubusercontent.com/dbt-labs/jaffle_shop/main/seeds/raw_payments.csv
```

**🗄️ In DuckDB**, drop and reload tables:

```sql
DROP TABLE IF EXISTS raw.raw_customers;
DROP TABLE IF EXISTS raw.raw_orders;
DROP TABLE IF EXISTS raw.raw_payments;

-- Re-run CREATE TABLE commands from Step 2 above
```

### Tables not found

**📍 Check files exist:**

```bash
ls jaffle_shop_dbt/data/
# Should show: raw_customers.csv, raw_orders.csv, raw_payments.csv
```

**🗄️ Check tables in DBeaver:**

1. Click database icon in sidebar
2. Expand your connection
3. Look for "raw" schema and tables
4. Or run: `SHOW TABLES;` in new SQL file

If tables missing, re-run Step 2 (Load Data into DuckDB)

</details>

## 2. Create Your First Model

### 2.1. Create Staging Model

<details>
<summary markdown="span">**💡 Understanding `source()` and Jinja**</summary>

**What is `{{ source() }}`?**

The `{{ source() }}` macro is part of Jinja templating in dbt. Jinja lets you write dynamic SQL.

**Why use `{{ source() }}` instead of writing table names directly?**

```sql
-- ❌ Without source macro (brittle)
SELECT * FROM raw.raw_customers

-- With source macro (flexible)
SELECT * FROM {{ source('jaffle_shop', 'raw_customers') }}
```

**Benefits:**

- If raw table moves/renames, change it once in `schema.yml`
- dbt tracks lineage (raw data → models)
- Can add freshness tests to sources
- Shows in dbt documentation automatically

**Double curly braces** tell dbt to replace expressions with actual SQL before running.

</details>

**📍 In your terminal**, create the staging directory:

```bash
# Navigate to your dbt project
cd jaffle_shop_dbt

# Create staging directory
mkdir -p models/staging
```

**📝 In VS Code**, create a new file `models/staging/stg_customers.sql` with this SQL:

```sql
{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('jaffle_shop', 'raw_customers') }}
)

SELECT
    id AS customer_id,
    first_name,
    last_name
FROM source
```

**💡 Why include `config()` when it's already set in `dbt_project.yml`?** The `dbt_project.yml` already sets `+materialized: view` as the default for the staging layer — so technically this block is redundant. We include it here explicitly so the intent is clear inline: anyone reading this file immediately knows it materialises as a view, without having to cross-reference the project config. This is a style choice; once you're comfortable with the project structure you can omit inline `config()` blocks if the project default already matches.

**💾 Save the file** (Cmd+S or Ctrl+S).

### 2.2. Run Your First Model

**🗄️ In DBeaver**, disconnect from your database:

1. **Right-click your `jaffle_shop_shared` connection** in the Database Navigator

2. **Select "Disconnect"**

**💡 Why?** DuckDB only allows one process to write to the database at a time. DBeaver holds a lock on the database file, which prevents dbt from running. You can reconnect DBeaver any time after dbt finishes if you want to query the results directly.

**📍 In your terminal**, navigate to your dbt project if you are not already there:

```bash
cd jaffle_shop_dbt
```

Then run the staging model:

```bash
dbt run --select stg_customers
```

<details>
<summary markdown="span">**Expected output**</summary>

```bash
Completed successfully
Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
```

</details>

<details>
<summary markdown="span">**🔧 Troubleshooting: Model Run Issues**</summary>

### "Conflicting lock" or "Could not set lock on file" error

**Problem:** DBeaver (or another process) has the database file locked

**🗄️ In DBeaver:**

1. Right-click your `jaffle_shop_shared` connection
2. Select "Disconnect"
3. Or quit DBeaver entirely

**📍 Then retry:**

```bash
dbt run --select stg_customers
```

**After dbt finishes**, you can reconnect DBeaver to query the results.

### "Compilation Error" or SQL syntax errors

**📍 In your terminal**, compile to see the error:

```bash
dbt compile --select stg_customers
```

Check the compiled SQL in `target/compiled/jaffle_shop_dbt/models/staging/stg_customers.sql`

**Common issues:**

- Missing comma in SELECT statement
- Typo in source name: must match schema.yml exactly
- Missing closing parenthesis or quote

### Model runs but produces 0 rows

**Test source data directly:**

**🗄️ In DBeaver**, run:

```sql
SELECT COUNT(*) FROM raw.raw_customers;
-- Should return 100

SELECT * FROM raw.raw_customers LIMIT 5;
-- Should show customer data
```

If source has data but model is empty, check your WHERE clauses or JOIN conditions

### "Not in correct directory" error

**Check where you are:**

```bash
pwd
# Should end with: .../jaffle_shop_dbt
```

**Navigate to correct directory (from your challenge directory):**

```bash
cd jaffle_shop_dbt
```

**Always run dbt commands from your project root** (where dbt_project.yml lives)

</details>

Now open the compiled output to see what dbt actually ran:

**📍 In your terminal:**

```bash
cat target/compiled/jaffle_shop_dbt/models/staging/stg_customers.sql
```

The `{{ source('jaffle_shop', 'raw_customers') }}` macro has been replaced with the real table reference — this is exactly what DuckDB executed. Any time you want to understand what a model actually runs, check `target/compiled/`.

## 🧪 Checkpoint 1: Push First Staging Model

**Before pushing, validate your staging model:**

**📍 In your terminal**, if you are not already in the challenge directory, navigate there now:

```bash
cd ..
```

Then run the tests:

```bash
pytest tests/test_staging_model.py -v
```

**Optional: Run all tests together:**

```bash
make
```

**If all tests pass**, commit your staging model:

```bash
# Stage the staging model
git add jaffle_shop_dbt/models/staging/

# Commit with descriptive message
git commit -m "Add first staging model: stg_customers"

# Push to GitHub (triggers automated tests)
git push origin master
```

**❌ Any failures?** → Review the 🔧 Troubleshooting dropdowns in each section above or raise a ticket with a TA!

**All checks passed?** Congratulations! You're ready to start building data transformations with dbt Core!

---

Your first staging model is running. `stg_customers` selects from the raw source using `source()` and renames columns for consistency — the foundation every other model in this unit builds on. The next challenge adds additional configuration to make those source references more precise.

---

<details>
<summary markdown="span">**Useful Tips and Resources**</summary>

**📍 Common dbt commands** you'll use in upcoming challenges:

```bash
# Run models
dbt run                          # All models
dbt run --select model_name      # One model
dbt run --select folder.*        # All in folder

# Test models
dbt test                         # All tests
dbt test --select model_name     # Tests for one model

# Documentation
dbt docs generate                # Build docs
dbt docs serve                   # View at localhost:8080

# Debugging
dbt compile                      # Compile without running
dbt debug                        # Test connection
dbt list                         # Show all models
```

**📝 In VS Code**, install the dbt Power User extension:

- Click Extensions icon (Cmd+Shift+X / Ctrl+Shift+X)
- Search "dbt Power User"
- Click Install
- Features: SQL syntax highlighting, model previews, lineage graphs

**💡 Tip:** Use VS Code's integrated terminal (View → Terminal) to run dbt commands

---

#### Resources

- [dbt Core Docs](https://docs.getdbt.com/docs/core/installation)
- [dbt-duckdb Adapter](https://github.com/duckdb/dbt-duckdb)
- [DuckDB SQL Reference](https://duckdb.org/docs/sql/introduction)
- [dbt Best Practices](https://docs.getdbt.com/guides/best-practices)

</details>

---

## 🎉 Challenge Complete

Raw data is in DuckDB and your first staging model is running.

**Key takeaways:**

- `source()` is a reference, not a string — update the source definition once and every model using it updates automatically
- DuckDB allows only one writer at a time — disconnect DBeaver before `dbt run`, reconnect to query results
- `target/compiled/` holds the plain SQL dbt generated — you saw this after running `stg_customers`: `{{ source() }}` is replaced with the real table reference before the query runs
# data-analytics-load-data-and-first-model
# data-analytics-load-data-and-first-model
