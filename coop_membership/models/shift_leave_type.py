from odoo import fields, models


class ShiftLeaveType(models.Model):
    _inherit = 'shift.leave.type'

    is_temp_leave = fields.Boolean(string='Temporary Leave', default=False)
    is_incapacity = fields.Boolean(string='Incapacity', default=False)
    is_non_defined = fields.Boolean(string="Non Defined Type", default=False)
    is_anticipated = fields.Boolean(string='Anticipated Leave', default=False)
    anticipated_month = fields.Integer(string="Month", default=2)
