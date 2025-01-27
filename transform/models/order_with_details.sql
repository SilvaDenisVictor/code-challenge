{{ 
  config(
    materialized='table'
  ) 
}}

SELECT 
  ord.order_id AS order_id_orders,  -- Renomeia order_id da tabela orders
  ord_d.order_id AS order_id_order_details  -- Renomeia order_id da tabela order_details
FROM 
  {{ source('landing', 'orders') }} ord
JOIN 
  {{ source('landing', 'order_details') }} ord_d
ON 
  ord.order_id = ord_d.order_id