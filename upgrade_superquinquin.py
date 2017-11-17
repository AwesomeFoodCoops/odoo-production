# -*- coding: utf-8 -*-
from openerp.tools import config


def run(session, logger):
    """Update all modules."""
    if session.is_initialization:
        config['load_language'] = 'fr_FR'
        modules = [
            'account_accountant',
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

    if session.db_version <= '1.0' or not session.db_version:
        cleanup_ir_model_data_product_category_9815(session)

    for version, module in ins_modules_version.items():
        if session.db_version <= version:
            ins_modules.extend(module)

    update_attachment(session, logger, ins_modules, up_modules)

    if ins_modules:
        session.update_modules_list()
        logger.info("installing modules %r", ins_modules)
        session.install_modules(ins_modules)

    if up_modules:
        logger.info("updating modules %r", up_modules)
        session.update_modules(up_modules)

    # I don't remember if this is necessary, anyway we commit!
    session.cr.commit()


def update_attachment(session, logger, ins_modules, up_modules):
    """Install large object in the db"""
    if session.db_version < '1.1' or not session.db_version:
        ins_modules.append('attachment_large_object')
        parameter = session.registry('ir.config_parameter')
        logger.info('Setup paramter to use advanced attachment')
        parameter.set_param(
            session.cr, session.uid, 'ir_attachment.location',
            'postgresql:lobject')
        session.cr.commit()


def cleanup_ir_model_data_product_category_9815(session):
    '''#9815: product module do not have product_category_Souscriptions
    definition and some product template are using this category.

    While updating product module, as there is no more
    product_category_Souscription definition in source code Odoo tries to
    remove this category, but it used somehow in product template where
    categ_id is require field. So we needs to remove this ir_model_data entry
    to define this data as manage by user instead code source to avoid to
    remove it in the database.
    '''
    session.env.cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE name = 'product_category_Souscriptions' AND
              module = 'product' AND
              model = 'product.category'
        """
    )
    # I wonder why, updating module open new transactions, needs to commit
    # before
    session.cr.commit()
