ALTER TABLE res_partner DROP column cooperative_state;
UPDATE ir_cron SET name = 'Partner : Update Working State', function = 'update_working_state' WHERE name = 'Partner : Update Cooperative State';
