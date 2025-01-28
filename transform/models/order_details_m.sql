{{ 
  config(
    materialized='view'
  ) 
}}


SELECT
    O.*
FROM
    {{ source('landing', 'order_details') }} O

