.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================
Point of Sale - Barcode Rule Transform
======================================

This module extends Odoo Point Of Sale features, to allow to configure
a python expression to transform the captured value in the barcode.

This is usefull in the case you have a barcode with price information in it,
but you need to add a margin, for instance.

This happens when the supplier is the one printing the label, and you don't
have control over the barcode.


Configuration
=============

* Go to 'Point of Sale' / 'Configuration' / 'Barcode Nomenclatures'
* Edit your barcode rules, according to your barcodes settings
* Add a transform expression to the rule

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
