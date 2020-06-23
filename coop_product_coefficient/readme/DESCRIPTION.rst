This module was written to extend the functionality of Odoo Product module.

This module add 'Product Coefficients' Model and a complete system to compute
theoritical sale price, depending of a supplier price.

Product Coefficients
--------------------

A coefficient can be:

* A coefficient of Shipping (it will be used at the beginning of the computation)
* A coefficient of Loss (it will be used after for the computation)
* A Custom Coefficient (it will be used at the middle of the computation)
* A Coefficient of Margin (it will be used at the end of the computation)

Two operation are allowed:

* 'Multiplier' : A multiplication will be done
* 'Fixed Amount' : A fixed amount will be added

.. image:: ../static/description/product_coefficient.png

Products
--------

6 Coefficients can be set on products.

On the product form, a new page displays price details, using
category coefficients previously defined.

The base price is based on the supplier sale price. (see technical information
below).

.. image:: ../static/description/product_template.png

This module provides a theoritical sale price, based on the sale price and
the coefficients. If the theoritical sale price is different of the real
sale price, a button is available to apply the change on the product form.

.. image:: ../static/description/use_theoritical_price_one.png

User can select all the products that have a sale price differents and can
change prices massively, using a wizard :

.. image:: ../static/description/use_theoritical_price_multi.png

You can mass edit coefficient on many products, via a new tree editable view

.. image:: ../static/description/product_template_tree.png

Technical Information
---------------------

If user set end dates on supplier info, base prices will be incorrect after
a certain date. For that purpose, an extra button is available on the product
form, and cron task is available to recompute base prices each night.