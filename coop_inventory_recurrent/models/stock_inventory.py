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
        res0 = []
        res1 = []
        res2 = []
        for inventory in self:
            if inventory.category_group_line_id.copies in ('1', '2'):
                res1.append({
                    'obj': inventory,
                    'extra_title': _('First List'),
                    'color': ''
                })
            if inventory.category_group_line_id.copies == '2':
                res2.append({
                    'obj': inventory,
                    'extra_title': _('Second List'),
                    'color': 'blue'
                })
            if not inventory.category_group_line_id.copies:
                res0.append({'obj': inventory})
        res = res0 + res1 + res2
        return res

    @api.multi
    def check_duplex(self):
        self.ensure_one()
        res = False
        first_page_nb = int(self.env['ir.config_parameter'].sudo().\
            get_param("report.first_page_nb", 35))  # 31
        page_nb = 1
        est_line_nb = int(self.env['ir.config_parameter'].sudo().\
            get_param("report.est_line_nb", 39))  # 37
        line_nb = len(self.line_ids) - first_page_nb
        if line_nb > 0:
            page_nb += int(line_nb/est_line_nb)
            if line_nb%est_line_nb > 0:
                page_nb += 1
        if page_nb%2 != 0:
            res = True
        return res
