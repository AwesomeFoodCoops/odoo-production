from odoo.tests import common


class CoopProduceTest(common.TransactionCase):
    """ Base class - Test the Coop Produce.
    """

    def setUp(self):
        super(CoopProduceTest, self).setUp()
        # Useful models
        self.StockInventory = self.env['stock.inventory']
        self.OrderWeekPlanning = self.env['order.week.planning']
        self.StockInventoryWizard = self.env['stock.inventory.wizard']
        self.OrderWeekPlanning = self.env['order.week.planning']

        self.SupplierCoop = self.env['res.partner'].create({
            'name': 'Coop Supplier',
            'supplier': True,
        })
        self.CategoryCoop = self.env['product.category'].create({
            'name': 'Coop Category',
        })
        self.ProductCoop = self.env['product.template'].create({
            'name': 'Coop Product',
            'list_price': 14.0,
            'standard_price': 8.0,
            'type': 'product',
            'default_code': 'COOP_PRODUCT',
            'categ_id': self.CategoryCoop.id,
        })
        self.SupplierInfo = self.env['product.supplierinfo'].create({
            'name': self.SupplierCoop.id,
            'price': 8,
            'product_tmpl_id': self.ProductCoop.id,
            'product_id': self.ProductCoop.product_variant_id.id
        })
        self.ProductCoop.product_variant_id.default_packaging = 2
