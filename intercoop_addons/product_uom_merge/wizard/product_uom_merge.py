# -*- coding: utf-8 -*-
from openerp import fields, api, models, _
from openerp.exceptions import Warning as UserError, ValidationError
from openerp.tools import mute_logger
from openerp.osv import fields as fields_osv
from openerp.osv.orm import browse_record
import itertools
import functools

import logging
_logger = logging.getLogger(__name__)


class ProductUomMerge(models.TransientModel):
    _name = "product.uom.merge"

    @api.model
    def default_get(self, fields):
        res = super(ProductUomMerge, self).default_get(fields)
        if (
            self.env.context.get('active_model') == 'product.uom'
            and self.env.context.get('active_ids', [])
        ):
            res['uom_ids'] = [
                (4, i) for i in self.env.context.get('active_ids', [])]
            res['target_uom_id'] = self.env.context.get('active_id')
        return res

    uom_ids = fields.Many2many(
        "product.uom",
        string="UoMs to merge",
        required=True,
    )

    target_uom_id = fields.Many2one(
        "product.uom",
        string="Target UoM",
        help="The operations will be merged with this UoM",
        required=True,
    )

    @api.onchange('uom_ids')
    def _onchange_uom_ids(self):
        if (
            self.uom_ids
            and (
                not self.target_uom_id
                or self.target_uom_id not in self.uom_ids
            )
        ):
            self.target_uom_id = self.uom_ids[0]


    @api.model
    def get_fk_on(self, table):
        self.env.cr.execute("""
            SELECT
                cl1.relname as table,
                att1.attname as column
            FROM
                pg_constraint as con,
                pg_class as cl1,
                pg_class as cl2,
                pg_attribute as att1,
                pg_attribute as att2
            WHERE
                con.conrelid = cl1.oid
            AND con.confrelid = cl2.oid
            AND array_lower(con.conkey, 1) = 1
            AND con.conkey[1] = att1.attnum
            AND att1.attrelid = cl1.oid
            AND cl2.relname = %s
            AND att2.attname = 'id'
            AND array_lower(con.confkey, 1) = 1
            AND con.confkey[1] = att2.attnum
            AND att2.attrelid = cl2.oid
            AND con.contype = 'f'
        """, (table,))
        return self.env.cr.fetchall()

    @api.model
    def _update_foreign_keys(self, records, target):
        target.ensure_one()
        if records._name != target._name:
            raise ValidationError(_(
                "Records and target have to be of the same model\n"
                "%s != %s") % (records._name, target._name))
        _logger.debug(
            '_update_foreign_keys for target(%s): %s for records(%s): %r',
            target._name,
            target.id,
            records._name,
            records.ids,
        )

        # find the many2one relations
        for table, column in self.get_fk_on(records._table):
            query = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name LIKE '%s'
            """ % (table)
            self.env.cr.execute(query, ())
            columns = []
            for data in self.env.cr.fetchall():
                if data[0] != column:
                    columns.append(data[0])

            query_dic = {
                'table': table,
                'column': column,
                'value': columns[0],
            }

            if len(columns) <= 1:
                # unique key treated
                query = """
                    UPDATE "%(table)s" as ___tu
                    SET %(column)s = %%s
                    WHERE
                        %(column)s = %%s AND
                        NOT EXISTS (
                            SELECT 1
                            FROM "%(table)s" as ___tw
                            WHERE
                                %(column)s = %%s AND
                                ___tu.%(value)s = ___tw.%(value)s
                        )""" % query_dic
                for rec in records:
                    self.env.cr.execute(query, (target.id, rec.id, target.id))
            else:
                with mute_logger('openerp.sql_db'), self.env.cr.savepoint():
                    query = """
                        UPDATE "%(table)s"
                        SET %(column)s = %%s
                        WHERE %(column)s IN %%s
                    """ % query_dic
                    self.env.cr.execute(query, (target.id, tuple(records.ids)))

                    # Handle parents
                    if (
                        column == records._parent_name
                        and table == records._table
                    ):
                        query = """
                            WITH RECURSIVE cycle(id, %(column)s) AS (
                                    SELECT id, %(column)s
                                    FROM %(table)s
                                UNION
                                    SELECT  cycle.id, t.%(column)s
                                    FROM    %(table)s AS t, cycle
                                    WHERE   t.id = cycle.%(column)s AND
                                            cycle.id != cycle.%(column)s
                            )
                            SELECT id FROM cycle
                            WHERE id = %(column)s AND id = %%s
                        """ % query_dic
                        self.env.cr.execute(query, (target.id,))

    @api.model
    def _update_reference_fields(self, records, target):
        target.ensure_one()
        if records._name != target._name:
            raise ValidationError(_(
                "Records and target have to be of the same model\n"
                "%s != %s") % (records._name, target._name))
        _logger.debug(
            '_update_reference_fields for target(%s): %s for records(%s): %r',
            target._name,
            target.id,
            records._name,
            records.ids,
        )

        def update_records(model, src, field_model='model', field_id='res_id'):
            if model not in self.env:
                return
            recs = self.env[model].sudo().search([
                (field_model, '=', records._name),
                (field_id, '=', src.id)])
            try:
                with mute_logger('openerp.sql_db'), self.env.cr.savepoint():
                    return recs.write({field_id: target.id})
            except psycopg2.Error:
                # updating fails, most likely due to a violated unique
                # constraint keeping record with nonexistent record is useless,
                # better delete it
                return recs.unlink()

        update_records = functools.partial(update_records)

        for rec in records:
            update_records('ir.attachment', src=rec, field_model='res_model')
            update_records('mail.followers', src=rec, field_model='res_model')
            update_records('mail.message', src=rec)
            update_records('ir.model.data', src=rec)

        # remove duplicated __export__ ir.model.data
        self.env['ir.model.data'].search([
            ('model', '=', target._name),
            ('res_id', '=', target.id),
            ('module', '=', '__export__'),
        ]).unlink()

        fields = self.env['ir.model.fields'].sudo().search([
            ('ttype', '=', 'reference')])
        for field in fields:
            try:
                proxy_model = self.env[field.model].sudo()
                column = proxy_model._columns[field.name]
            except KeyError:
                # unknown model or field => skip
                continue
            if isinstance(column, fields_osv.function):
                continue
            for rec in records:
                proxy_model.search([
                    (field.name, '=', '%s,%d' % (rec._name, rec.id))
                ]).write({
                    field.name: '%s,%d' % (target._name, target.id),
                })

    @api.model
    def _update_values(self, records, target):
        target.ensure_one()
        if records._name != target._name:
            raise ValidationError(_(
                "Records and target have to be of the same model\n"
                "%s != %s") % (records._name, target._name))
        _logger.debug(
            '_update_values for target(%s): %s for records(%s): %r',
            target._name,
            target.id,
            records._name,
            records.ids,
        )

        columns = target.fields_get().keys()

        def write_serializer(column, item):
            if isinstance(item, browse_record):
                return item.id
            else:
                return item

        values = dict()
        for column in columns:
            field = target._fields[column]
            if field.type not in ('many2many', 'one2many') and field.compute is None:
                for item in itertools.chain(records, [target]):
                    if item[column]:
                        values[column] = write_serializer(column, item[column])

        values.pop('id', None)
        parent_id = values.pop(target._parent_name, None)
        target.write(values)
        if parent_id and parent_id != target.id:
            try:
                target.write({target._parent_name: parent_id})
            except ValidationError:
                _logger.info('Skip recursive record hierarchies for parent_id %s of record: %s', parent_id, target.id)


    @api.multi
    def merge(self):
        self.ensure_one()
        target = self.target_uom_id
        records = self.uom_ids
        # Sanity checks
        target.ensure_one()
        if records._name != target._name:
            raise ValidationError(_(
                "Records and target have to be of the same model\n"
                "%s != %s") % (records._name, target._name))
        if len(records) < 2:
            return
        if len(records.mapped('category_id')) > 1:
            raise UserError(_(
                "All uoms must belong to the same uom category."))
        # Check consistancy between uom values
        for rec in records:
            if target.uom_type == 'reference':
                if (
                    (rec.uom_type == 'bigger' and rec.factor_inv != 1.00)
                    or (rec.uom_type == 'smaller' and rec.factor != 1.00)
                ):
                    raise UserError(_(
                        "All uoms should represent the same quantities.\n"
                        "You can't merge uom with different conversion "
                        "factors."))
            else:
                if (
                    rec.uom_type != target.uom_type
                    or (
                        rec.uom_type == 'bigger'
                        and rec.factor_inv != target.factor_inv
                    ) or (
                        rec.uom_type == 'smaller'
                        and rec.factor != target.factor
                    )
                ):
                    raise UserError(_(
                        "All uoms should represent the same quantities.\n"
                        "You can't merge uom with different conversion "
                        "factors."))
        # Merge all
        records = records - target
        self._update_foreign_keys(records, target)
        self._update_reference_fields(records, target)
        self._update_values(records, target)
        _logger.info(
            '(uid = %s) merged the records(%s) %r with %s',
            self.env.user.id,
            records._name,
            records.ids,
            target.id,
        )
        # Notify
        if hasattr(target, 'message_post'):
            target.message_post(
                body='%s %s' % (
                    _("Merged with the following records:"),
                    ", ".join(
                        "%s (ID %s)" % (n[1], n[0])
                        for n in records.name_get()
                    )
                )
            )
        # Safely remove duplicates
        for rec in records:
            rec.unlink()
