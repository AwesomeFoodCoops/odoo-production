# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models


class StockInventoryRecurrentWizard(models.TransientModel):
    _name = "stock.inventory.recurrent.wizard"
    _description = "Recurrent Inventory"

    category_group_ids = fields.Many2many(
        'stock.inventory.category.group',
        'stock_inventory_recurrent_category_group_rel',
        string='Category Groups'
    )

    @api.multi
    def _execute(self):
        self.ensure_one()
        vals = []
        inventories = self.env['stock.inventory']
        for categ_group in self.category_group_ids:
            for line in categ_group.line_ids:
                vals.append({
                    'name': line.category_id.name,
                    'filter': 'category',
                    'category_id': line.category_id.id,
                    'category_group_line_id': line.id
                })

        if vals:
            inventories = self.env['stock.inventory'].create(vals)
        inventories.action_start()
        return inventories

    @api.multi
    def action_execute(self):
        inventories = self.env['stock.inventory']
        for rec in self:
            inventories |= rec._execute()
        act_window = self.env.ref("stock.action_inventory_form")
        form_view = self.env.ref("stock.view_inventory_form")
        return {
            'name': act_window.name,
            'type': 'ir.actions.act_window',
            'res_model': 'stock.inventory',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'views': [
                    (act_window and act_window.view_id.id or False, 'tree'),
                    (form_view and form_view.id or False, 'form'),],
        }
