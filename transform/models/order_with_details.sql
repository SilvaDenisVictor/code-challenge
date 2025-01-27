{{ 
  config(
    materialized='table'
  ) 
}}

SELECT 
  O.*,
  O_d.product_id,
  O_d.unit_price,
  O_d.quantity,
  O_d.discount
FROM 
  {{ source('landing', 'orders') }} O
JOIN 
  {{ source('landing', 'order_details') }} O_d
ON 
  O.order_id = O_d.order_id