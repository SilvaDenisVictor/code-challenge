{{ 
  config(
    materialized='view'
  ) 
}}


SELECT
    O.*
FROM
    {{ source('landing', 'orders') }} O

