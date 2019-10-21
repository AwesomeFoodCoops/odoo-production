.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
Point of Sale - Barcode Rule Force
==================================

This module adds a new field on the product: Force Barcode Rule

If set, when this product is scanned on the POS, it will try to use that 
barcode rule instead of the one that matched the pattern first.

This rule has to still match the pattern, and it should belong to the
same nomenclature that's being used on the POS.


Configuration
=============

* Go to any product
* Edit Force Barcode Rule

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/pos/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======


Contributors
------------

* Iván Todorovich <ivan.todorovich@druidoo.io>


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
