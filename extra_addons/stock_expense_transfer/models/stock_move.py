# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today: GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    inventory_value = fields.Float(
        string='Inventory Value', compute='_compute_inventory_value',
        store=True)

    # Compute Section
    @api.multi
    @api.depends('state')
    def _compute_inventory_value(self):
        """Inventory value is computed only when the move is done."""
        for move in self:
            inventory_value = 0.0
            if move.state == 'done':
                for quant in move.quant_ids:
                    if quant.location_id == move.location_dest_id\
                            and quant.inventory_value > 0:
                        inventory_value += quant.inventory_value
            move.inventory_value = inventory_value
