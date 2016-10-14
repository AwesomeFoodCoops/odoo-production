# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ResContactOrigin(models.Model):
    _name = 'res.contact.origin'

    name = fields.Char(
        string='Name', required=True)

    partner_ids = fields.One2many(
        comodel_name='res.partner', inverse_name='contact_origin_id',
        string='Members')

