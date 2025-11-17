#!/usr/bin/env python3
import os
import sys
import msal


# ── Config ────────────────────────────────────────────────────────────────────
TENANT_ID = "bf465dc7-3bc8-4944-b018-092572b5c20d"
CLIENT_ID = "2e50ad87-8336-4a04-8817-6aeac7d63390"


# FULL workspace URL for the SDK (must include https://)
DATABRICKS_HOST = "https://dbc-0bff3115-71d9.cloud.databricks.com/"


# Your *custom audience* that your Databricks federation policy allows
# (make sure your policy's audiences contains *exactly* this "api://<GUID>" value)
#SCOPES = [f"api://{AUDIENCE_APP_ID}/.default"]  # or a named scope, e.g., api://<GUID>/access_as_user
SCOPES = ["api://2e50ad87-8336-4a04-8817-6aeac7d63390/databricksscope"]


# ── MSAL: get Entra access token for your custom audience ────────────────────
authority = f"https://login.microsoftonline.com/{TENANT_ID}"
app = msal.PublicClientApplication(client_id=CLIENT_ID, authority=authority)

result = None
accounts = app.get_accounts()
print(accounts)
if accounts:
   print("In Account")
   result = app.acquire_token_silent(scopes=SCOPES, account=accounts[0], redirect_uri="http://localhost:5000")


if not result:
   # If you prefer device code (no browser), replace the next line with device-flow calls.
   result = app.acquire_token_interactive(scopes=SCOPES, max_age=200)
   



if "access_token" not in result:
   print(f"Failed to acquire Entra token: {result.get('error')}: {result.get('error_description')}", file=sys.stderr)
   sys.exit(1)


entra_jwt = result["access_token"]
print(entra_jwt)


print("✔ Got Entra access token from Entra")


# ── Hand the IdP token to the SDK and let it exchange it ─────────────────────
# The Databricks SDK uses the same env configuration as the CLI.
# env-oidc => SDK will call POST /oidc/v1/token for you.
os.environ["DATABRICKS_HOST"] = DATABRICKS_HOST
os.environ["DATABRICKS_AUTH_TYPE"] = "env-oidc"
os.environ["DATABRICKS_OIDC_TOKEN"] = entra_jwt


# If your federation policy is *service-principal-scoped*, you may also need:
# os.environ["DATABRICKS_CLIENT_ID"] = "<service-principal-app-id>"


from databricks.sdk import WorkspaceClient


# Create the SDK client (no manual HTTP; no manual exchange)
w = WorkspaceClient()  # reads env above


# ── Who am I? (Current user) ─────────────────────────────────────────────────
me = w.current_user.me()
print("\nCurrent Databricks identity:")
print(f"  user_name: {me.user_name}")
print(f"  display_name: {me.display_name}")
print(f"  active: {me.active}")


# ── List SQL Warehouses via SDK ───────────────────────────────────────────────
print("\nSQL Warehouses:")
# In the SDK, this maps to GET /api/2.0/sql/warehouses
for wh in w.warehouses.list():
   print(f"- {wh.name} (id={wh.id}, state={wh.state}, type={wh.warehouse_type}, size={wh.cluster_size})")


# ── Execute SQL Query ─────────────────────────────────────────────────────────
WAREHOUSE_ID = "ec354449db0ae20a"
SQL_QUERY = """
SELECT
  dim_company.city,
  AVG(fact_markethistory.yield) AS average_yield
FROM
  tpcdi.gold_market.fact_markethistory
    JOIN tpcdi.gold_market.dim_company
      ON fact_markethistory.sk_companyid = dim_company.sk_companyid
GROUP BY
  dim_company.city
ORDER BY
  average_yield DESC
"""

print(f"\n{'='*80}")
print(f"Executing SQL Query on Warehouse: {WAREHOUSE_ID}")
print(f"{'='*80}")
print(f"Query:\n{SQL_QUERY}")
print(f"{'='*80}")

try:
    # Execute the SQL statement
    statement = w.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=SQL_QUERY,
        wait_timeout="30s"
    )
    
    
    
    # Display results
    if statement.result and statement.result.data_array:
        print(f"\nResults ({len(statement.result.data_array)} rows):")
        print(f"{'-'*80}")
        
        # Print header
        if statement.manifest and statement.manifest.schema and statement.manifest.schema.columns:
            headers = [col.name for col in statement.manifest.schema.columns]
            print(f"{'  |  '.join(headers)}")
            print(f"{'-'*80}")
        
        # Print data rows
        for row in statement.result.data_array:
            print(f"{'  |  '.join(str(val) if val is not None else 'NULL' for val in row)}")
    else:
        print("\nNo results returned.")
        
except Exception as e:
    print(f"\n❌ Error executing query: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()

