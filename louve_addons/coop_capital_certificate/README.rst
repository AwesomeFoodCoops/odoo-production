.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

===================
Coop Capital Certificate
===================

* Create a Capital Certificate wizard available for group_account_manager
* Parameter is fiscal year (default = N-1)
* The wizard generates a single report for each partner that has any capital fundraising moves in the selected year. For that, we consider the capital_account_id defined in the fundraising category.
* The wizard sends an email with attached report to all partner that have bought capital in the selected year
* The report uses the external layout defined fot the company
* Additional parameters are in Accounting/Configuration/Configuration:
    * header of report
    * image of the signature

Issues / Roadmap
================

Credits
=======

Contributors
------------

* Julien Weste <julien.weste@akretion.com>
