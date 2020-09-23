[![Build Status](https://travis-ci.com/AwesomeFoodCoops/odoo-production.svg?branch=12.0)](https://travis-ci.com/AwesomeFoodCoops/odoo-production)
[![codecov](https://codecov.io/gh/AwesomeFoodCoops/odoo-production/branch/12.0/graph/badge.svg)](https://codecov.io/gh/AwesomeFoodCoops/odoo-production)

FoodCoops
=========

These modules provide an Open Source solution to managing cooperative supermarkets in Odoo.

This repository aims to handle a commom Odoo source code for the food coops that take part in the mutualization (and found it). Our code is free, so that coops don't want to fit in the previsous rules can freely fork this Github repository. However, we higly encourage them to not fork the common modules. In that case it would be very difficult for them to enter in the mutualization in the future.

<!-- prettier-ignore-start -->
[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[account_asset_management_xlsx](account_asset_management_xlsx/) | 12.0.1.0.0 | account_asset_management_xlsx
[account_bank_statement_import_caisse_epargne](account_bank_statement_import_caisse_epargne/) | 12.0.1.0.0 | Import CSV Bank Statement from Caisse d'Epargne
[account_bank_statement_reconcile_option](account_bank_statement_reconcile_option/) | 12.0.1.0.0 | Give options on the reconciliation propositions
[account_bank_statement_reconciliation_report](account_bank_statement_reconciliation_report/) | 12.0.1.0.0 | Account Bank Statement Summary
[account_invoice_merge](account_invoice_merge/) | 12.0.1.0.0 | Account Invoice Merge Wizard
[account_invoice_refund_option](account_invoice_refund_option/) | 12.0.1.0.0 | Account Invoice Refund Option
[account_partner_journal](account_partner_journal/) | 12.0.1.0.0 | Define default journal on partner
[account_payment_confirm](account_payment_confirm/) | 12.0.1.0.0 | Improve payment confirmation
[account_payment_select_account](account_payment_select_account/) | 12.0.1.0.0 | Account Payment - Select Account
[account_payment_term_restricted](account_payment_term_restricted/) | 12.0.1.0.0 | Account Payment Terms - Customer / Supplier Restrictions
[account_reconcile_pos_payments](account_reconcile_pos_payments/) | 12.0.1.0.0 | Bank Auto Reconcille POS Payments
[capital_subscription](capital_subscription/) | 12.0.1.0.0 | Provide extra accounting features for Capital Subscription
[coop_account](coop_account/) | 12.0.1.1.0 | Coop Account
[coop_account_check_deposit](coop_account_check_deposit/) | 12.0.1.1.0 | Manage deposit of checks to the bank
[coop_account_product_fiscal_classification](coop_account_product_fiscal_classification/) | 12.0.1.0.0 | Provide extra features for Fiscal Classification
[coop_badge_reader](coop_badge_reader/) | 12.0.1.0.0 | Provide light Ionic Apps to read user Badge
[coop_capital_certificate](coop_capital_certificate/) | 12.0.1.0.0 | Provide a Fiscal Certificate report for capital subscriptions
[coop_default_pricetag](coop_default_pricetag/) | 12.0.1.0.1 | Coop Default Price Tag
[coop_disable_product](coop_disable_product/) | 12.0.1.0.0 | Coop Limit Creation of Product
[coop_inventory](coop_inventory/) | 12.0.1.0.0 | Coop - Inventory
[coop_membership](coop_membership/) | 12.0.4.0.0 | Custom settings for membership
[coop_memberspace](coop_memberspace/) | 12.0.1.0.0 | Coop Memberspace
[coop_numerical_keyboard](coop_numerical_keyboard/) | 12.0.1.0.0 | Create a new POS numerical keyboard
[coop_parental_leave](coop_parental_leave/) | 12.0.1.0.0 | Custom settings for Parental Leave
[coop_point_of_sale](coop_point_of_sale/) | 12.0.1.0.1 | Customize Point of Sale Display Custom Barcode Rules for Coop article weight and price.
[coop_print_badge](coop_print_badge/) | 12.0.1.0.0 | Print partner's badge
[coop_produce](coop_produce/) | 12.0.1.0.0 | Coop Produce
[coop_product_coefficient](coop_product_coefficient/) | 12.0.1.1.0 | Coop Product Coefficients
[coop_purchase](coop_purchase/) | 12.0.1.0.0 | Coop Purchase
[coop_shift](coop_shift/) | 12.0.2.0.0 | Coop Shift
[coop_stock](coop_stock/) | 12.0.1.0.0 | Custom settings for stock
[edi_purchase_base](edi_purchase_base/) | 12.0.1.0.0 | EDI Purchase
[edi_purchase_config](edi_purchase_config/) | 12.0.1.0.0 | EDI Config
[edi_purchase_diapar](edi_purchase_diapar/) | 12.0.1.0.0 | EDI Purchase DIAPAR
[email_validation_check](email_validation_check/) | 12.0.1.0.0 | Email Validation Check
[field_image_preview](field_image_preview/) | 12.0.1.0.0 | Adds functional preview (open/popup) image in original size Enlarge image Enlarge images product images preview product images picture foto product photo product preview enlarge
[l10n_fr_coop_default_pricetag](l10n_fr_coop_default_pricetag/) | 12.0.1.0.0 | l10n fr Coop Default Price Tag
[l10n_fr_fec_background](l10n_fr_fec_background/) | 12.0.1.0.0 | Fichier d'Échange Informatisé (FEC) for France
[l10n_fr_fec_group_sale_purchase](l10n_fr_fec_group_sale_purchase/) | 12.0.1.0.0 | Fichier d'Échange Informatisé (FEC) for France
[mass_mailing_access](mass_mailing_access/) | 12.0.1.0.0 | Limit mass sending to new 'Mass Mailing Manager' group member
[partner_validate_email](partner_validate_email/) | 12.0.1.0.0 | Partner - Validate Email
[pos_automatic_cashdrawer](pos_automatic_cashdrawer/) | 12.0.1.0.0 | Manage Automatic Cashdrawer device from POS front end
[pos_automatic_validation](pos_automatic_validation/) | 12.0.1.0.0 | Manage Automatic Validation after complete payment in the POS front end
[pos_barcode_rule_force](pos_barcode_rule_force/) | 12.0.1.0.0 | On the product template, allow to force a specific rule
[pos_barcode_rule_transform](pos_barcode_rule_transform/) | 12.0.1.0.0 | Transforms the value read in the barcode with a JS expression
[pos_order_wait_save](pos_order_wait_save/) | 12.0.1.0.0 | POS Order Wait Save
[pos_payment_terminal](pos_payment_terminal/) | 12.0.0.1.0 | Manage Payment Terminal device from POS front end
[pos_payment_terminal_return](pos_payment_terminal_return/) | 12.0.1.0.0 | Manage Payment Terminal device from POS front end with return
[pos_restrict_scan](pos_restrict_scan/) | 12.0.1.0.0 | POS Restrict Scanning Product
[pos_search_improvement](pos_search_improvement/) | 12.0.1.0.0 | Search Exactly Products
[pos_ticket_send_by_mail](pos_ticket_send_by_mail/) | 12.0.1.0.0 | POS Receipt By Email
[product_average_consumption](product_average_consumption/) | 12.0.1.0.0 | Product - Average Consumption
[product_history](product_history/) | 12.0.2.0.0 | Product - History
[product_history_for_cpo](product_history_for_cpo/) | 12.0.1.0.0 | Product History for CPO
[product_print_category](product_print_category/) | 12.0.1.0.0 | Automate products print, when data has changed
[product_to_scale_bizerba](product_to_scale_bizerba/) | 12.0.1.0.0 | Synchronize Odoo database with Scales
[purchase_compute_order](purchase_compute_order/) | 12.0.1.0.0 | Computed Purchase Order
[purchase_package_qty](purchase_package_qty/) | 12.0.1.0.0 | Purchase - Package Quantity
[res_partner_account_move_line](res_partner_account_move_line/) | 12.0.1.0.0 | Button to access partner's account move lines

[//]: # (end addons)
<!-- prettier-ignore-end -->
