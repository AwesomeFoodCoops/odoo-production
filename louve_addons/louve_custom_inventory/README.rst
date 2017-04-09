.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Louve Custom - Inventory
========================

Features
--------

* On inventory line, add 2 new fields to make more easy inventory.
    * product_qty1 : product quantity in the ground floor
    * product_qty2 : product quantity in the underground
    * the field 'product_qty' begins computed, based on product_qty1 and
      product_qty2

* Change Stock Inventory Report, removing some useless fields and adding new
  ones.

Warning
-------

This module overwrite stock.inventory.line features. Make sure all the features
using stock.inventory.line are patched with product_qty1 and product_qty2
fields.

Images
------

* Stock Inventory Form

.. figure:: louve_custom_inventory/static/description/stock_inventory.png
   :width: 800 px



* Product Quantity Adjustment Form

.. figure:: louve_custom_inventory/static/description/update_product_qty.png
   :width: 800 px



* Stock Inventory Report
.. figure:: louve_custom_inventory/static/description/report_stock_inventory.png
   :width: 800 px

Credits
=======

Contributors
------------

* Julien WESTE
* Sylvain LE GAL

Funders
-------

The development of this module has been financially supported by:

* La Louve (http://www.lalouve.net)
