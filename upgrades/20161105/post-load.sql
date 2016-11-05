update res_partner set barcode_base = barcode_base_moved0::int where barcode_base_moved0 != '';
update shift_template set start_datetime = to_timestamp(start_date::text, 'YYYY-MM-DD')  + (start_time - 1) * 3600::text::interval;
update shift_template set end_datetime = to_timestamp(start_date::text, 'YYYY-MM-DD')  + (end_time - 1) * 3600::text::interval;
