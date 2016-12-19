# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Mathieu VATEL (http://www.julius.fr/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    group_pos_automatic_cashlogy = fields.Many2one(
        comodel_name='res.groups',
        compute='_compute_group_pos_automatic_cashlogy',
        string='Point of Sale - Allow Cashlogy connection',
        help="This field is there to pass the id of the "
        "'PoS - Allow Cashlogy connection'"
        " Group to the Point of Sale Frontend.")

    @api.multi
    def _compute_group_pos_automatic_cashlogy(self):
        for config in self:
            config.group_pos_automatic_cashlogy = \
                self.env.ref('pos_automatic_cashdrawer.'
                             'group_pos_automatic_cashlogy')

    group_pos_automatic_cashlogy_config = fields.Many2one(
        comodel_name='res.groups',
        compute='_compute_group_pos_automatic_cashlogy_config',
        string='Point of Sale - Allow Cashlogy Config',
        help="This field is there to pass the id of the "
        "'PoS - Allow Cashlogy config'"
        " Group to the Point of Sale Frontend.")

    @api.multi
    def _compute_group_pos_automatic_cashlogy_config(self):
        for config in self:
            config.group_pos_automatic_cashlogy_config = \
                self.env.ref('pos_automatic_cashdrawer.'
                             'group_pos_automatic_cashlogy_config')
