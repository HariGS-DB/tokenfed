# Databricks notebook source
# MAGIC %md
# MAGIC # Market History Analysis
# MAGIC This notebook queries the TPC-DI market history data to calculate average yields by city.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   dim_company.city,
# MAGIC   AVG(fact_markethistory.yield) AS average_yield
# MAGIC FROM
# MAGIC   tpcdi.gold_market.fact_markethistory
# MAGIC     JOIN tpcdi.gold_market.dim_company
# MAGIC       ON fact_markethistory.sk_companyid = dim_company.sk_companyid
# MAGIC GROUP BY
# MAGIC   dim_company.city
# MAGIC ORDER BY
# MAGIC   average_yield DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Results
# MAGIC The query above shows cities ranked by their average market yield in descending order.

