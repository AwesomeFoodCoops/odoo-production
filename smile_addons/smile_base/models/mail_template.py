# -*- coding: utf-8 -*-

from openerp import api, models, tools, _
from openerp.exceptions import UserError
from openerp.addons.mail.models.mail_template import format_tz, mako_template_env, mako_safe_template_env, _logger


class MailTemplate(models.Model):
    _inherit = "mail.template"

    @api.multi
    def format_numeric(self, value, column, options=None):
        try:
            model, fieldname = column.split(',')
            field = self.env[model]._fields[fieldname]
            converter = self.env['ir.qweb.field.%s' % field.type]
            return converter.value_to_html(value, field, options)
        except:
            return value

    @api.model
    def render_template(self, template_txt, model, res_ids, post_process=False):
        """ Render the given template text, replace mako expressions ``${expr}``
        with the result of evaluating these expressions with an evaluation
        context containing:

         - ``user``: browse_record of the current user
         - ``object``: record of the document record this mail is related to
         - ``context``: the context passed to the mail composition wizard

        :param str template_txt: the template text to render
        :param str model: model name of the document record this mail is related to.
        :param int res_ids: list of ids of document records those mails are related to.
        """
        multi_mode = True
        if isinstance(res_ids, (int, long)):
            multi_mode = False
            res_ids = [res_ids]

        results = dict.fromkeys(res_ids, u"")

        # try to load the template
        try:
            mako_env = mako_safe_template_env if self.env.context.get('safe') else mako_template_env
            template = mako_env.from_string(tools.ustr(template_txt))
        except Exception:
            _logger.info("Failed to load template %r", template_txt, exc_info=True)
            return multi_mode and results or results[res_ids[0]]

        # prepare template variables
        records = self.env[model].browse(filter(None, res_ids))  # filter to avoid browsing [None]
        res_to_rec = dict.fromkeys(res_ids, None)
        for record in records:
            res_to_rec[record.id] = record
        variables = {
            'format_tz': lambda dt, tz=False, format=False, context=self._context: format_tz(self.pool, self._cr, self._uid, dt, tz, format, context),
            'format_numeric': lambda value, column, options=None:  self.format_numeric(value, column, options),  # Added by Smile
            'user': self.env.user,
            'ctx': self._context,  # context kw would clash with mako internals
        }
        for res_id, record in res_to_rec.iteritems():
            variables['object'] = record
            try:
                render_result = template.render(variables)
            except Exception:
                _logger.info("Failed to render template %r using values %r" % (template, variables), exc_info=True)
                raise UserError(_("Failed to render template %r using values %r") % (template, variables))
                render_result = u""
            if render_result == u"False":
                render_result = u""
            results[res_id] = render_result

        if post_process:
            for res_id, result in results.iteritems():
                results[res_id] = self.render_post_process(result)

        return multi_mode and results or results[res_ids[0]]
