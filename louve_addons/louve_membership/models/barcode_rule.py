# -*- coding: utf-8 -*-
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today GRAP (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    is_louve_member = fields.Boolean(
        string='Checked for Louve Members', help="If checked, Louve members"
        " will have this barcode rule by default.")

    is_associated_people = fields.Boolean(
        string='Checked for Associated People', help="If checked, Associated"
        " people will have this barcode rule by default.")
