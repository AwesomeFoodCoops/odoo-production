##############################################################################
#
#    Sale - Food Module for Odoo
#    Copyright (C) 2012-Today GRAP (http://www.grap.coop)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _


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
                tmp = data.rack_number_of_packages + (" - " + tmp if tmp else "")
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
    ingredients = fields.Text(string="Ingredients")
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
    weight_net = fields.Float("Net Weight", default=0)

    price_volume = fields.Char(
        compute="_compute_price_volume", string="Price by liter"
    )
    price_weight_net = fields.Char(
        compute="_compute_price_weight_net", string="Price by kg"
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
        "Rack Instruction",
        help="""For example, the number of packages that
        should be stored on the rack""",
    )
    rack_location = fields.Char(
        "Rack Location", help="""The name or place of the rack"""
    )
    rack_number_of_packages = fields.Char("Number of packages on the rack")
    farming_method = fields.Char("Farming Method", help="""Organic Label""")
    other_information = fields.Char("Other Information")
    pricetag_rackinfos = fields.Char(
        compute=_compute_pricetag_rackinfos, string="Coop rack fields"
    )
    pricetag_coopinfos = fields.Char(
        compute=_compute_pricetag_coopinfos, string="Coop custom fields"
    )
    category_print_id = fields.Many2one(
        comodel_name="product.category.print", string="Print Category"
    )

    # Compute Section
    @api.depends("list_price", "volume")
    @api.multi
    def _compute_price_volume(self):
        """Return the price by liter"""
        for data in self:
            if data.list_price and data.volume:
                data.price_volume = "%.2f" % round(data.list_price / data.volume, 2)
            else:
                data.price_volume = ""

    @api.depends("list_price", "weight_net")
    @api.multi
    def _compute_price_weight_net(self):
        """Return the price by kg"""
        for data in self:
            if data.list_price and data.weight_net:
                data.price_weight_net = "%.2f" % round(
                    data.list_price / data.weight_net, 2
                )
            else:
                data.price_weight_net = ""

    @api.depends("origin_description", "country_id")
    @api.multi
    def _compute_pricetag_origin(self):
        for data in self:
            tmp = ""
            if data.origin_description:
                tmp = data.origin_description
            if data.country_id:
                tmp = data.country_id.name.upper() + (" - " + tmp if tmp else "")
            if data.maker_description:
                tmp = (tmp and (tmp + " - ") or "") + data.maker_description
            data.pricetag_origin = tmp

    @api.depends("fresh_category", "fresh_range")
    @api.multi
    def _compute_extra_food_info(self):
        """Return extra information about food for legal documents"""
        for data in self:
            tmp = ""
            if data.fresh_range:
                tmp += _(" - Range: ") + data.fresh_range
            if data.fresh_category:
                tmp += _(" - Category: ") + data.fresh_category
            data.extra_food_info = tmp
