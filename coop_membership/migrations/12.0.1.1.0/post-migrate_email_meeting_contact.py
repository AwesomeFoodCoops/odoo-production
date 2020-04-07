from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    ir_config = env['ir.config_parameter']
    email_meeting_contact = ir_config.get_param('email_meeting_contact')
    company_name = ir_config.get_param('company_name')
    company_vals = {}
    companies = env['res.company'].search([])
    if email_meeting_contact:
        company_vals['email_meeting_contact'] = email_meeting_contact
    if company_name:
        company_vals['company_name'] = company_name
    companies.write(company_vals)
    config = ir_config.search(
        [('key', 'in', ('email_meeting_contact', 'company_name'))]
    )
    config.unlink()
