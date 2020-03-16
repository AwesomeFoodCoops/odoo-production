
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    def name_get(self):
        """Return the product name without ref when the
        name_get is called from order planning form
        """
        res = []
        if self.env.context.get('order_planning_context'):
            for record in self:
                res.append((record['id'], record['name']))
        else:
            res = super(ProductProduct, self).name_get()
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_packaging = fields.Float(
        'Default packaging', digits=dp.get_precision('Product Price'),
        default=1.0)

    @api.constrains('default_packaging')
    def check_default_packaging(self):
        for product in self:
            if product.default_packaging <= 0.0:
                raise UserError(
                    _("Default packaging of %s must be positive ! " % (
                        product.name,)))
