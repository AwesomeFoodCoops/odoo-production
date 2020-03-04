# Copyright (C) 2012-Today GRAP (http://www.grap.coop)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    _FRESH_CATEGORY_KEYS = [
        ("extra", "Extra"),
        ("1", "Category I"),
        ("2", "Category II"),
        ("3", "Category III"),
    ]
    _FRESH_RANGE_KEYS = [
        ("1", "1 - Fresh"),
        ("2", "2 - Canned"),
        ("3", "3 - Frozen"),
        ("4", "4 - Uncooked and Ready to Use"),
        ("5", "5 - Cooked and Ready to Use"),
        ("6", "6 - Dehydrated and Shelf"),
    ]

    @api.depends("farming_method", "other_information")
    @api.multi
    def _compute_pricetag_coopinfos(self):
        for pt in self:
            tmp = ""
            if pt.other_information:
                tmp = pt.other_information
            if pt.farming_method:
                tmp = pt.farming_method + (" - " + tmp if tmp else "")
            pt.pricetag_coopinfos = tmp

    @api.depends(
        "rack_instruction",
        "rack_location",
        "rack_number_of_packages",
        "default_seller_id",
    )
    @api.multi
    def _compute_pricetag_rackinfos(self):
        for data in self:
            tmp = ""
            if data.rack_instruction:
                tmp = data.rack_instruction
            if data.rack_location:
                tmp = data.rack_location + (" - " + tmp if tmp else "")
            if data.rack_number_of_packages:
                tmp = data.rack_number_of_packages + \
                    (" - " + tmp if tmp else "")
            if data.default_seller_id.package_qty:
                tmp = str(data.default_seller_id.package_qty) + (
                    " - " + tmp if tmp else ""
                )
            data.pricetag_rackinfos = tmp

    # Columns section
    label_ids = fields.Many2many(
        string="Labels",
        comodel_name="product.label",
        relation="product_label_product_rel",
        column_1="product_id",
        column_2="label_id",
    )
    expiration_date_days = fields.Integer(
        string="Expiration Date (Days)",
        help="Field used to compute the"
        " expiration date. (Number of days after packaging the product)",
    )
    expiration_comsumption_days = fields.Integer(
        string="Expiration Consumption (Days)"
    )
    ingredients = fields.Text()
    extra_note_bizerba_pricetag_1 = fields.Char(
        string="Extra Note printed on Bizerba Pricetags #1"
    )
    extra_note_bizerba_pricetag_2 = fields.Char(
        string="Extra Note printed on Bizerba Pricetags #2"
    )
    is_mercuriale = fields.Boolean(
        "Mercuriale Product",
        help="A product in mercuriale has price"
        " that changes very regularly.",
    )
    price_volume = fields.Monetary(
        compute="_compute_price_volume",
        string="Price by liter",
        store=True,
        currency_field='currency_id',
    )
    price_weight = fields.Monetary(
        compute="_compute_price_weight",
        string="Price by kg",
        store=True,
        currency_field='currency_id',
    )
    country_id = fields.Many2one(
        string="Origin Country",
        comodel_name="res.country",
        help="Country of production of the product",
    )
    origin_description = fields.Char(
        string="Origin Complement",
        help="Production location complementary information",
    )
    maker_description = fields.Char(string="Maker")
    pricetag_origin = fields.Char(
        compute="_compute_pricetag_origin", string="Text about origin"
    )
    fresh_category = fields.Selection(
        _FRESH_CATEGORY_KEYS,
        string="Category for Fresh Product",
        help="Extra - Hight Quality : product without default ;\n"
        "Quality I - Good Quality : Product with little defaults ;\n"
        "Quality II - Normal Quality : Product with default ;\n"
        "Quality III - Bad Quality : Use this option only in"
        " specific situation.",
    )
    fresh_range = fields.Selection(
        _FRESH_RANGE_KEYS, "Range for Fresh Product"
    )
    extra_food_info = fields.Char(
        compute="_compute_extra_food_info",
        string="Extra information for invoices",
    )
    rack_instruction = fields.Char(
        help="""For example, the number of packages that
        should be stored on the rack""",
    )
    rack_location = fields.Char(
        help="""The name or place of the rack"""
    )
    rack_number_of_packages = fields.Char("Number of packages on the rack")
    farming_method = fields.Char(help="""Organic Label""")
    other_information = fields.Char()
    pricetag_rackinfos = fields.Char(
        compute=_compute_pricetag_rackinfos, string="Coop rack fields"
    )
    pricetag_coopinfos = fields.Char(
        compute=_compute_pricetag_coopinfos, string="Coop custom fields"
    )
    category_print_id = fields.Many2one(
        comodel_name="product.print.category", string="Print Category"
    )
    scale_logo_code = fields.Char(readonly=True)
    volume = fields.Float(digits=dp.get_precision('Volume'))

    # Compute Section
    @api.depends("list_price", "volume")
    def _compute_price_volume(self):
        """Return the price by liter"""
        for data in self:
            if data.list_price and data.volume:
                data.price_volume = data.list_price / data.volume
            else:
                data.price_volume = 0.0

    @api.depends("list_price", "weight")
    def _compute_price_weight(self):
        """Return the price by kg"""
        for data in self:
            if data.list_price and data.weight:
                data.price_weight = data.list_price / data.weight
            else:
                data.price_weight = 0.0

    @api.depends("origin_description", "country_id")
    def _compute_pricetag_origin(self):
        for data in self:
            tmp = ""
            if data.origin_description:
                tmp = data.origin_description
            if data.country_id:
                tmp = data.country_id.name.upper() + \
                    (" - " + tmp if tmp else "")
            if data.maker_description:
                tmp = (tmp and (tmp + " - ") or "") + data.maker_description
            data.pricetag_origin = tmp

    @api.depends("fresh_category", "fresh_range")
    def _compute_extra_food_info(self):
        """Return extra information about food for legal documents"""
        for data in self:
            tmp = ""
            if data.fresh_range:
                tmp += _(" - Range: ") + data.fresh_range
            if data.fresh_category:
                tmp += _(" - Category: ") + data.fresh_category
            data.extra_food_info = tmp

    @api.model
    def create(self, vals):
        vals['scale_logo_code'] = '1'
        if 'label_ids' in vals:
            label_ids_val = vals.get("label_ids", [])
            if label_ids_val and isinstance(label_ids_val, list) and \
                    len(label_ids_val[0]) == 3:
                label_ids = label_ids_val[0][2]
                labels = self.env['product.label'].browse(label_ids)
                vals['scale_logo_code'] = labels and \
                    labels[0].scale_logo_code or '1'

        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'label_ids' in vals:
            res = True
            for product in self:
                current_logo_code = product.scale_logo_code
                res = super(ProductTemplate, product).write(vals)

                # Browse again to see check the value
                updated_prod = self.browse(product.id)
                new_logo_code = updated_prod.label_ids and \
                    updated_prod.label_ids[0].scale_logo_code or '1'

                # Only trigger the change if it is actually change
                if current_logo_code != new_logo_code:
                    res = super(ProductTemplate, updated_prod).write(
                        {'scale_logo_code': new_logo_code}
                    )
            return res
        return super(ProductTemplate, self).write(vals)
