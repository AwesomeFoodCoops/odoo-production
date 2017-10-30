# -*- coding: utf-8 -*-
from openerp.tools import config


def run(session, logger):
    """Update all modules."""
    if session.is_initialization:
        config['load_language'] = 'fr_FR'
        modules = [
        'coop_membership_access_rights',
        'smile_base',
        'louve_custom_product',
        'louve_custom_purchase',
         
        'account_payment_transfer_account',
        'account_asset',
        'coop_purchase',
        'louve_custom_account',
        'louve_custom_pos',
        'portal_sale',
        'account_product_fiscal_classification',
        'board',
        'l10n_fr_fec',
        'louve_custom_inventory',
        'louve_welcome_email',
        'mail_tip',
        'partner_validate_email',
        'portal_stock',
        'pos_payment_terminal_return',
         
        'product_history_for_cpo',
        'stock_expense_transfer',
        'account_bank_statement_import_caisse_epargne',
        'account_bank_statement_import_ofx',
        'account_bank_statement_reconcile_option',
        'account_budget',
        'account_check_deposit',
        'account_journal_inactive',
        'account_payment_confirm',
        'account_payment_select_account',
        'account_payment_term_restricted',
        'account_reconcile_writeoff_improve',
        'account_voucher',
        'auth_crypt',
        'base_import',
        'base_technical_features',
        'hr_equipment',
        'hw_cashlogy',
        'louve_custom_cpo',
        'louve_custom_email',
        'louve_date_search_extended',
        'mass_editing',
        'mass_mailing_access',
        'payment_transfer',
        'pos_access_right',
        'pos_automatic_validation',
        'pos_customer_required',
        'pos_empty_home',
        'pos_price_to_weight',
        'pos_quick_logout',
        'pos_reprint',
        'pos_restrict_scan',
        'pos_return_order',
        'pos_session_summary',
        'pos_transfer_account',
        'procurement_jit',
        'scheduler_error_mailer',
        'stock_inventory_by_category',
        'web_calendar',
        'web_diagram',
        'web_favicon',
        'web_settings_dashboard',
        'web_sheet_full_width',
        'web_view_editor',
        'web_widget_image_webcam',
        'pos_product_barcodes',
        'pos_automatic_cashdrawer',
        #'coop_product_coefficient',

          
        ]
        session.install_modules(modules)
        logger.info(
            "Fresh database ! Installing foodcoops la louve- modules: %r",
            modules
        )
        session.env.cr.commit()
        return
    # specific case
    logger.info("Default upgrade procedure : updating all modules.")

    # expected installed module for a given version
    # format: { 'Num version': [ 'module to install', ...], }
    ins_modules_version = {}

    up_modules = ['all']
    ins_modules = []

    for version, module in ins_modules_version.items():
        if session.db_version <= version:
            ins_modules.extend(module)

    if ins_modules:
        session.update_modules_list()
        logger.info("installing modules %r", ins_modules)
        session.install_modules(ins_modules)

    if up_modules:
        logger.info("updating modules %r", up_modules)
        session.update_modules(up_modules)

    # I don't remember if this is necessary, anyway we commit!
    session.cr.commit()
