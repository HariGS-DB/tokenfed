-- Market History Analysis
-- Calculate average market yield by city from TPC-DI data

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

