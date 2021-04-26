from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        allow_inactive_search_fields = ["barcode"]
        allow_inactive_search_field_domain = filter(
            lambda arg: isinstance(arg, (list, tuple))
            and arg[0] in allow_inactive_search_fields,
            args,
        )
        if list(allow_inactive_search_field_domain):
            args.append("|")
            args.append(("active", "=", True))
            args.append(("active", "=", False))
        return super(ProductProduct, self).search(
            args=args, offset=offset, limit=limit, order=order, count=count
        )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        allow_inactive_search_fields = ["barcode"]
        allow_inactive_search_field_domain = filter(
            lambda arg: isinstance(arg, (list, tuple))
            and arg[0] in allow_inactive_search_fields,
            args,
        )
        if list(allow_inactive_search_field_domain):
            args.append("|")
            args.append(("active", "=", True))
            args.append(("active", "=", False))
        return super(ProductTemplate, self).search(
            args=args, offset=offset, limit=limit, order=order, count=count
        )


class ProductCategory(models.Model):
    _inherit = "product.category"

    type = fields.Selection([
        ('view','View'),
        ('normal','Normal')],
        string='Category Type',
        default='normal'
    )
