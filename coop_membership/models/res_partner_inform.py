from odoo import fields, models


class ResPartnerInform(models.Model):
    _name = 'res.partner.inform'
    _description = 'Res Partner Inform'

    name = fields.Char()
