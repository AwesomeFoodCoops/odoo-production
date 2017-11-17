# -*- coding: utf-8 -*-


def update_attachment(session, logger, ins_modules, up_modules):
    """Install large object in the db"""
    if session.db_version < '1.1' or not session.db_version:
        ins_modules.add('attachment_large_object')
        parameter = session.registry('ir.config_parameter')
        logger.info('Setup paramter to use advanced attachment')
        parameter.set_param(
            session.cr, session.uid, 'ir_attachment.location',
            'postgresql:lobject')
        session.cr.commit()
