# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import Warning


class ProductTemplate(models.Model):
    _inherit = "product.template"

    force_unavailable_in_pos = fields.Boolean()

    @api.multi
    def write(self, vals):
        if vals.get('force_unavailable_in_pos'):
            vals['force_unavailable_in_pos'] = False
        return super(ProductTemplate, self).write(vals)

    @api.multi
    def check_pos_session_running(self):
        pos_sessions = self.env["pos.session"].search(
            [("state", "in", ["opening_control", "opened"])]
        )
        if pos_sessions:
            return False
        return True

    @api.onchange('available_in_pos')
    def onchange_available_in_pos(self):
        if not self.available_in_pos and not self.check_pos_session_running():
            self.force_unavailable_in_pos = True
            self.available_in_pos = True

    @api.multi
    def confirm_unavailable_in_pos(self):
        if self._context.get('confirm'):
            self.available_in_pos = False
        self.force_unavailable_in_pos = False
