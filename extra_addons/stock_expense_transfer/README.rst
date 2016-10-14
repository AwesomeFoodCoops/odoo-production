.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

========================
Stock - Expense Transfer
========================

This module was written to extend the functionality of odoo Stock and
Accounting about Expense Transfer.

This module is usefull in the case where you want to 'consume' for internal
reasons some products you usually sell. For exemple, shops that buy and sell
cleaning products and want to use some of them to wash the floor.

In that case, two things are required:

* products should go out of the stock, to have correct quantities on hand
* a accounting entry should be write to move expense from default expense
  account to a specific expense account

With this module, it is now possible to define on a internal picking type a
Expense Transfer Account and Journal. If set, it will be possible for
accountant people to generate accounting entries.


Installation
============

Normal installation.

Configuration
=============

* Go to 'Inventory' / 'Configuration' / 'Routes' / 'Picking Types'
* Edit or create a new picking type with 'Type of Operation' set to 'Internal'
* Set an expense transfer account and an Expense Transfer Journal

.. image:: /stock_expense_transfer/static/description/picking_type.png

Usage
=====

Product Consumption
-------------------

* Create a new picking as usual and validate the picking

Generate Entries
----------------

(For accountants)

* Go to 'Invoicing' / 'Adviser' / 'Transfer Expenses'
* Select pickings
* click on 'Action' / 'Generate Expense Transfer Accouting Entries' and next
  'Generate'


.. image:: /stock_expense_transfer/static/description/accounting_entry.png

Road Map
========

* this module computes inventory value for stock moves and based on related
  quants. It could be great to move this features into another generic module
  ('stock_move_inventory_value') and to make this module depends on the new
  one. (same for stock.picking)

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Sylvain LE GAL <https://twitter.com/legalsylvain>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
