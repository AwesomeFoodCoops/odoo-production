-- update barcode_base field, due to change from char to integer field
update res_partner set barcode_base = barcode_base_moved0::int where barcode_base_moved0 != '';
-- Initialize start_datetime and end_datetime based on obsolete value and current timezone. (GMT +1)
update shift_template set start_datetime = to_timestamp(start_date::text, 'YYYY-MM-DD')  + (start_time - 1) * 3600::text::interval;
update shift_template set end_datetime = to_timestamp(start_date::text, 'YYYY-MM-DD')  + (end_time - 1) * 3600::text::interval;
