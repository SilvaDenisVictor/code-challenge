{{ 
  config(
    materialized='table'
  ) 
}}


SELECT
    O.order_id,
    O.customer_id,
    O.employee_id,
    O.order_date,
    O.required_date,
    O.shipped_date,
    O.ship_via,
    O.freight,
    O.ship_name,
    O.ship_address,
    O.ship_city,
    O.ship_region,
    O.ship_postal_code,
    O.ship_country,
    O._sdc_extracted_at,
    O._sdc_received_at,
    O._sdc_batched_at,
    O._sdc_deleted_at,
    O._sdc_sequence,
    O._sdc_table_version,
    O._sdc_sync_started_at
FROM
    {{ source('landing', 'orders') }} O

