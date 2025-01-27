{{ 
  config(
    materialized='table'
  ) 
}}


SELECT
    O.order_id,
    O.product_id,
    O.unit_price,
    O.quantity,
    O.discount
FROM
    {{ source('landing', 'order_details') }} O

