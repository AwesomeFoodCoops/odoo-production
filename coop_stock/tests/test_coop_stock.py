from odoo.tests import Form
from odoo.tests.common import TransactionCase


class CoopStockTest(TransactionCase):

    def setUp(self):
        super(CoopStockTest, self).setUp()

        self.inventory = self.env['stock.inventory']
        self.inventory_line = self.env['stock.inventory.line']
        self.categ_unit = self.env.ref('uom.product_uom_categ_unit')
        self.uom_unit = self.env['uom.uom'].search([
                        ('category_id', '=', self.categ_unit.id),
                        ('uom_type', '=', 'reference')], limit=1)
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.partner_3 = self.env.ref('base.res_partner_3')

    def test_01_stock_inventory_post_inventory(self):
        def create_product(name, uom_id, routes=()):
            prod = Form(self.env['product.product'])
            prod.name = name
            prod.type = 'product'
            prod.uom_id = uom_id
            prod.uom_po_id = uom_id
            prod.route_ids.clear()
            for route in routes:
                prod.route_ids.add(route)
            return prod.save()
        product_a = create_product('Product D', self.uom_unit)
        inventory = self.inventory.create({
            'name': 'Inventory Product KG',
            'product_id': product_a.id,
            'filter': 'product'})
        inventory.action_start()
        self.assertFalse(inventory.line_ids,
                         "Inventory line should not created.")
        self.inventory_line.create({
            'inventory_id': inventory.id,
            'product_id': product_a.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 20,
            'location_id': self.stock_location.id
        })
        inventory.action_validate()
        inventory.post_inventory()

    def test_02_stock_picking(self):
        picking_form = Form(self.env['stock.picking'])
        self.picking_type = self.env.ref('stock.picking_type_out')
        self.product = self.env.ref('product.product_delivery_01')
        picking_form.partner_id = self.partner_3
        picking_form.picking_type_id = self.picking_type
        self.picking = picking_form.save()
        self.picking.onchange_picking_type()
        self.move = self.env['stock.move'].create({
            'picking_id': self.picking.id,
            'product_id': self.product.id,
            'name': 'Test',
            'product_uom_qty': 20,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
            'quantity_done': 20,
            'product_qty_package': 20,
            'location_id': self.picking.location_id.id,
            'location_dest_id': self.picking.location_dest_id.id,
        })
        self.picking.copy_expected_qtys()
