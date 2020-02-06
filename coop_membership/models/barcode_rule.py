# Copyright (C) 2014 GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today GRAP (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    for_type_A_capital_subscriptor = fields.Boolean(
        string='For Type A Subscriptors',
        help="If checked, Louve members that subscribe type A capital will"
             " have this barcode rule by default.")

    for_associated_people = fields.Boolean(
        string='For Associated People',
        help="If checked, Associated people will have this barcode rule by"
             " default.")

    @api.multi
    @api.constrains('for_type_A_capital_subscriptor')
    def _check_for_type_A_capital_subscriptor(self):
        if len(self.search(
                [('for_type_A_capital_subscriptor', '=', True)])) > 1:
            raise ValidationError(_(
                "'For Type A Subscriptors' field should be unique."))

    @api.multi
    @api.constrains('for_associated_people')
    def _check_for_associated_people(self):
        if len(self.search(
                [('for_associated_people', '=', True)])) > 1:
            raise ValidationError(_(
                "'For Associated People' field should be unique."))
