from .common import CoopProduceTest
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestCoopProduce(CoopProduceTest):

    def test_coop_produce01(self):
        """
            Test the Coop Produce should take the quantities based on default
            packaging of the product and an advanced form view to plan orders
            of the week to send the supplier per day.
        """
        stock_inventory1 = self.StockInventory.create({
            'name': 'Inventory of V&F',
            'date': datetime.today().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT),
            'categ_ids': [(6, 0, [self.category_5_id])],
        })

        # Add products using "Add" button of Product categories
        stock_inventory1.action_add_category_supplier()

        # Inventory lines
        assert stock_inventory1.line_ids

        # Reset
        stock_inventory1.action_reset()

        # No Inventory lines after Reset
        assert not stock_inventory1.line_ids

        stock_inventory = self.StockInventory.create({
            'name': 'Inventory of V&F',
            'date': datetime.today().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT),
            'supplier_ids': [(6, 0, [self.supplier_id])],
        })

        # Add products using "Add" button of Supplliers
        stock_inventory.action_add_category_supplier()

        # Check Inventory lines adter added using suppliers' add button
        assert stock_inventory.line_ids

        # Validate F&V Inventory
        stock_inventory.action_done()

        # Check Week Date should not set by default
        self.assertFalse(stock_inventory.week_date,
                         "F&V inventory should not have week date"
                         " set when a new record.")

        stock_inventory_wizard = self.StockInventoryWizard.create({
            'week_date': datetime.today().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT)
        })

        ctx = {'active_id': stock_inventory.id}
        stock_inventory_wizard.with_context(ctx).action_ok()

        # I check that F&V Inventory is in the "Done" state
        self.assertEquals(stock_inventory.state, 'done')

        # Week Planification
        week_planification_id = stock_inventory.action_generate_planification()

        # Check week planification record created
        assert week_planification_id.get('res_id', False)

        orde_week_planning = self.OrderWeekPlanning.browse(
            week_planification_id.get('res_id'))

        # Monday: Create Purchase Order
        ctx = {'day_number': 1}
        orde_week_planning.with_context(ctx).create_purchase_orders()

        purchase_orders_action = orde_week_planning.action_view_orders()
        purchase_orders_domain = purchase_orders_action.get('domain', [])
        assert purchase_orders_domain

        purchase_orders = purchase_orders_domain[0][2]

        # Check purchase orders
        assert purchase_orders
