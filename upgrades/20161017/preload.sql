-- Force to recompute cooperative_state field
ALTER TABLE res_partner DROP column cooperative_state ;

-- Update CRON (that is set as noupdate=1)
UPDATE ir_cron SET name = 'Partner : Update Working State', function = 'update_working_state' WHERE name = 'Partner : Update Cooperative State';
