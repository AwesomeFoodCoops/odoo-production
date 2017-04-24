.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

===================
Coop Capital Certificate
===================

* Create a Capital Certificate wizard available for group_account_manager
* Parameter are:
    * fiscal year (default = N-1)
    * partner selection: selection of partners OR all partners
    * send mail: you can choose to send automatically the email or not
* The wizard generates a single report for each partner that has any capital fundraising moves in the selected year. For that, we consider the capital_account_id defined in the fundraising category.
* The wizard sends an email with attached report to all partner that have bought capital in the selected year OR create an attachment that you can access from partner view
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
