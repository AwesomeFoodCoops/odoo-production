.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Louve Custom - Account
======================

Features
--------

* On payment form, make 'Communication' field required, if payment type is
  'internal'.

* Add 'communication' field on account.payment tree view.

* Add 'partner_code' field on payment, related to parter_id.barcode_base
  Display partner_code on tree view and search view

* [account_tax_balance] Make function '_compute_move_type' on account.move'
  public.

Note
----
the function compute_move_type can will be removed, after the initialization
of account_tax_balance.

* Make supplier invoice date field equired

Credits
=======

Contributors
------------

* Sylvain LE GAL
* Julien Weste

Funders
-------

The development of this module has been financially supported by:

* La Louve (http://www.lalouve.net)
