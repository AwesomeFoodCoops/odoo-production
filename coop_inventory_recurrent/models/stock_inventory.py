# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    category_group_line_id = fields.Many2one(
        'stock.inventory.category.group.line',
        string='Category Group'
    )

    @api.multi
    def get_copi_variants(self):
        self.ensure_one()
        res = [{'obj': self}]
        if self.category_group_line_id.copies in ('1', '2'):
            res.append({
                'obj': self,
                'extra_title': _('First List'),
                'color': ''
            })
        if self.category_group_line_id.copies == '2':
            res.append({
                'obj': self,
                'extra_title': _('Second List'),
                'color': 'blue'
            })
        return res
    @api.multi
    def check_duplex(self):
        self.ensure_one()
        res = False
        est_line_nb = 35
        line_nb = len(self.line_ids)
        page_nb = int(line_nb/est_line_nb)
        if line_nb%est_line_nb > 0:
            page_nb += 1
        if page_nb%2 != 0:
            res = True
        return res
