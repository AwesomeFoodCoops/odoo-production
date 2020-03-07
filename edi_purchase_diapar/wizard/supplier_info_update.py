# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, models, _
from odoo.exceptions import ValidationError


class SupplierInfoUpdate(models.TransientModel):
    _inherit = "supplier.info.update"

    @api.model
    def compute_edi_partner(self, partner_id):
        """
        :param partner_id: purchase order/invoice supplier
        :return: EDI supplier used in FTP prices operations
        """
        ecs_obj = self.env["edi.config.system"]
        if partner_id.is_edi:
            edi_system = ecs_obj.search(
                [("supplier_id", "=", partner_id.id)], limit=1
            )
            if not edi_system:
                raise ValidationError(
                    _("No Config FTP for this supplier %s!") % partner_id.name
                )
            if edi_system.parent_supplier_id:
                return edi_system.parent_supplier_id
            else:
                return edi_system.supplier_id
        else:
            return True

    @api.model
    def update_lines_prices(self, obj_lines_values):
        """
        Updates PO/invoice lines prices depending on active_model
        :param obj_lines_values:
        :return: True
        """
        active_model = self._context.get("active_model", "")
        active_id = self._context.get("active_id", False)
        active_obj = self.env[active_model].browse(active_id)
        if active_model == "purchase.order":
            active_obj.write({"order_line": obj_lines_values})
        elif active_model == "account.invoice":
            active_obj.write({"invoice_line_ids": obj_lines_values})
        return True

    @api.model
    def update_prices_edi(
        self, lines, active_model, seller_values_lines, supplier, edi_supplier
    ):
        """
            :param lines: Wizard lines to Update.
            :param seller_values_lines: List of dictionnary of lines to update.
            :param supplier: Supplier.
            :return: Updated lines.
        """
        # Only for EDI suppliers
        if supplier.is_edi:
            # Clear old list elements
            del lines[0:]
            obj_lines_values = []
            for seller_values in seller_values_lines:
                # Look for product and product.supplierinfo datas
                supplier_id = supplier.id
                product_id = seller_values.get("product_id", False)
                product_tmpl_id = (
                    self.env["product.product"]
                    .browse(product_id)
                    .product_tmpl_id.id
                )
                product = self.env["product.template"].browse(product_tmpl_id)
                selected_seller_id = product.seller_ids.search([
                    ("name", "=", supplier_id),
                    ("product_tmpl_id", "=", product.id),
                ])
                selected_seller_id = (
                    selected_seller_id and selected_seller_id[0] or False
                )
                # Look for product code
                product_code = selected_seller_id.product_code
                if not product_code:
                    raise ValidationError(_(
                        "No supplier code given for product: %s for supplier: \
                        %s!, please give a "
                        "supplier code to continue prices operation update"
                    ) % (product.name, supplier.name))
                # Look for EDI latest price
                edi_price = self.env["supplier.price.list"].search([
                    ("supplier_id", "=", edi_supplier.id),
                    ("supplier_code", "=", product_code),
                ], order="import_date DESC")
                if edi_price:
                    price = edi_price[0]
                    price_dict = {"price_unit": price.price}
                    line_key = (
                        active_model == "purchase.order" and
                        "po_line_id" or
                        "invoice_line_id"
                    )
                    line_id = seller_values.get(line_key, False)
                    obj_lines_values.append((1, line_id, price_dict))
                    seller_values.update(price_dict)
                    # Reconstruct lines variable
                    lines.append((0, 0, seller_values))
            #### Update order/invoice lines with latest prices ####
            self.update_lines_prices(obj_lines_values)
        return lines

    @api.model
    def compute_process_lines(self, active_model, active_obj):
        """
        Overwritten to update product prices/order line prices based on latest EDI supplier prices (Only for EDI suppliers)
        :param active_model: Current active model
        :param active_obj: Current active object
        :return: computed lines
        """
        lines = super(SupplierInfoUpdate, self).compute_process_lines(
            active_model, active_obj
        )
        seller_values_lines = [line[2] for line in lines]
        partner_id = active_obj.partner_id
        edi_supplier = self.compute_edi_partner(partner_id)
        return self.update_prices_edi(
            lines, active_model, seller_values_lines, partner_id, edi_supplier
        )
