from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    configuration_user_ids = fields.Many2many(comodel_name="res.users")
