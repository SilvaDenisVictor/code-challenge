{{ 
  config(
    materialized='view'
  ) 
}}


SELECT
    -- O.order_id,
    -- O.product_id,
    -- O.unit_price,
    -- O.quantity,
    -- O.discount
    O.*
FROM
    {{ source('landing', 'order_details') }} O

