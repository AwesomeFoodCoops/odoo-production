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

        self.Product5 = self.env.ref('product.product_product_5')
        self.Product5.default_packaging = 2
        self.category_5_id = self.ref('product.product_category_5')
        self.supplier_id = self.ref('base.res_partner_12')
