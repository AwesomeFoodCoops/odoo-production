# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today: GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models, api, _
from openerp.exceptions import UserError


class StockPickingWizardExpenseTransfer(models.TransientModel):
    _name = 'stock.picking.wizard.expense.transfer'

    # Default Section
    def default_selected_picking_qty(self):
        return len(self._context.get('active_ids', []))

    # Columns Section
    selected_picking_qty = fields.Integer(
        string='Selected Picking Quantity', readonly=True,
        default=default_selected_picking_qty)

    @api.multi
    def button_generate_expense_entry(self):
        picking_obj = self.env['stock.picking']
        for wizard in self:
            pickings = picking_obj.search([
                ('id', 'in', self._context.get('active_ids', 0)),
                ('is_expense_transfer', '=', True),
                ('state', '=', 'done'),
                ('expense_transfer_move_id', '=', False)])
            if len(pickings) == 0:
                raise UserError(_(
                    "No pickings can generate Expense Transfer Entries."))
            else:
                pickings.generate_expense_entry()
