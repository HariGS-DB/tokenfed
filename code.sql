select event_time, source_ip_address, user_agent, user_identity, service_name, action_name, request_params  from system.access.audit where workspace_id=3658107809096140
and action_name in ('mintOAuthToken', 'mintOAuthAuthorizationCode', 'oidcTokenAuthorization')
and event_date='2025-12-03'
order by event_time desc



create table hsdb.default.sales_customers2 as
select * from samples.bakehouse.sales_customers

select date(datetime) as date, sum(totalprice) as price  from
 hsdb.default.sales_transactions t
 inner join hsdb.default.sales_customers c
 on t.customerid = c.customerid group by date(datetime) order by date(datetime)



select date(datetime), sum(totalprice)  from
 hsdb.default.sales_transactions t
 inner join hsdb.default.sales_customers2 c
 on t.customerid = c.customerid group by date(datetime) order by date(datetime)


 select * from hsdb.default.sales_customers

 CREATE POLICY `hsfiltercountry`
ON SCHEMA hsdb.default
ROW FILTER hsdb.default.filter_user_country
TO `account users`
FOR TABLES
WHEN hasTag('hs_customers')
MATCH COLUMNS hasTag('hs_country') AS u0
USING COLUMNS (u0)