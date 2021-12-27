# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models


class StockInventoryRecurrentReportWizard(models.TransientModel):
    _name = "stock.inventory.recurrent.report.wizard"
    _description = "Recurrent Inventory Report"

    inventory_ids = fields.Many2many(
        'stock.inventory',
        'stock_inventory_recurrent_report_rel',
        string='Inventory Adjustments',
        default=lambda self: self.get_default_inventory()
    )

    @api.model
    def get_default_inventory(self):
        ctx = self._context
        inventory_ids = []
        if ctx.get('active_ids') and \
                ctx.get('active_model') == 'stock.inventory':
            inventory_ids = ctx['active_ids']
        return [(6, 0, inventory_ids)]

    @api.multi
    def _execute(self):
        self.ensure_one()
        vals = []
        inventories = self.env['stock.inventory']
        for categ_group in self.category_group_ids:
            for categ in categ_group.category_ids:
                vals.append({
                    'name': categ.name,
                    'filter': 'category',
                    'category_id': categ.id,
                    'category_group_id': categ_group.id
                })
        if vals:
            inventories = self.env['stock.inventory'].create(vals)
        return inventories

    @api.multi
    def action_print(self):
        self.ensure_one()
        action = self.env.ref(
            'stock.action_report_inventory')
        inventories = self.inventory_ids.sorted(lambda i: i.name)
        return action.report_action(inventories, config=False)
