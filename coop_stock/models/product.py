from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        allow_inactive_search_fields = ["barcode"]
        not_allow_inactive = ["name"]
        allow_inactive_search_field_domain = filter(
            lambda arg: isinstance(arg, (list, tuple))
            and arg[0] in allow_inactive_search_fields,
            args,
        )
        not_allow_inactive_domain = filter(
            lambda arg: isinstance(arg, (list, tuple))
            and arg[0] in not_allow_inactive,
            args,
        )
        if not list(not_allow_inactive_domain) and \
                list(allow_inactive_search_field_domain):
            args.append("|")
            args.append(("active", "=", True))
            args.append(("active", "=", False))
        return super(ProductProduct, self).search(
            args=args, offset=offset, limit=limit, order=order, count=count
        )

    @api.multi
    def toggle_active(self):
        super(ProductProduct, self).toggle_active()
        for variant in self:
            if variant.active:
                if not variant.product_tmpl_id.active:
                    variant.product_tmpl_id.active = True
            elif variant.product_tmpl_id.active:
                other_variants = variant.product_tmpl_id.mapped(
                    'product_variant_ids').filtered(lambda v: v.active)
                if not other_variants:
                    variant.product_tmpl_id.active = False


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        allow_inactive_search_fields = ["barcode"]
        not_allow_inactive = ["name"]
        allow_inactive_search_field_domain = filter(
            lambda arg: isinstance(arg, (list, tuple))
            and arg[0] in allow_inactive_search_fields,
            args,
        )
        not_allow_inactive_domain = filter(
            lambda arg: isinstance(arg, (list, tuple))
            and arg[0] in not_allow_inactive,
            args,
        )
        if not list(not_allow_inactive_domain) and \
                list(allow_inactive_search_field_domain):
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
