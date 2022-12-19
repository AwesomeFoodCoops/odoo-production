# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Coop - Delivery Category",
    "version": "12.0.1.0.0",
    "category": "purchase",
    "author": "Trobz",
    "website": "https://trobz.com",
    "license": "AGPL-3",
    "depends": [
        "purchase",
        "purchase_compute_order"
    ],
    "data": [
        "security/ir.model.access.csv",
        "view/view_delivery_category.xml",
        "view/view_product_template.xml",
        "view/view_computed_purchase_order.xml",
    ],
}
