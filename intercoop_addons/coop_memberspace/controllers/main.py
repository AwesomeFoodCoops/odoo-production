# -*- coding: utf-8 -*-

from __future__ import division
import openerp
from openerp.addons.web import http
from openerp.http import request
from openerp import fields, tools, _
from datetime import date, datetime, timedelta
import pytz
import logging
import locale
_logger = logging.getLogger(__name__)
import werkzeug


class Website(openerp.addons.website.controllers.main.Website):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        user = request.env.user

        # Get members
        members = request.env['res.partner'].sudo().search([
            ('is_member', '=', True),
            ('cooperative_state', 'not in',
             ['blocked', 'unpayed', 'not_concerned', 'unsubscribed'])
        ])

        # Get member status
        member_status = user.partner_id.get_warning_member_state()

        # Get next shift
        shift_registration_env = request.env['shift.registration']
        shift_registration = shift_registration_env.sudo().search([
            ('shift_id.shift_template_id.is_technical', '=', False),
            ('partner_id', '=', user.partner_id.id),
            ('state', '!=', 'cancel'),
            ('date_begin', '>=', datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S'))
        ], order="date_begin", limit=1)

        # Get Turnover of the day
        lang = user.lang and (str(user.lang) + '.utf8') or 'fr_FR.utf8'
        try:
            locale.setlocale(locale.LC_TIME, lang)
        except Exception as e:
            _logger.debug("Can't set locale: %s", e)

        user_tz = user.tz or 'Europe/Paris'
        local = pytz.timezone(user_tz)
        date_begin = shift_registration and datetime.strftime(pytz.utc.localize(
            datetime.strptime(
                shift_registration.date_begin, "%Y-%m-%d %H:%M:%S")).astimezone(
                local), "%A, %d %B %Hh%M") or False

        today = date.today()
        week_number = request.env['shift.template']._get_week_number(date.today())
        week_name = request.env['shift.template']._number_to_letters(week_number)
        values = {
            'date_begin': date_begin and date_begin.capitalize() or False,
            'week_number': week_number,
            'week_name': week_name,
            'num_of_members': len(members),
            'member_status': member_status
        }
        return http.request.render('coop_memberspace.homepage', values)

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        r = super(Website, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            redirect = '/'
            return http.redirect_with_hash(redirect)
        return r

    @http.route('/planning', type='http', auth='user', website=True)
    def page_planning(self, **kwargs):
        user = request.env.user
        upcoming_shifts = request.env['shift.shift'].sudo().search([
            ('shift_template_id.is_technical', '=', False),
            ('date_begin', '>=', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('state', '=', 'confirm'),
        ], order="date_begin") or []
        return request.render(
            'coop_memberspace.planning',
            {
                'user': user,
                'shift_type': user.partner_id.shift_type,
                'upcoming_shifts': upcoming_shifts,
            }
        )

    @http.route('/mywork', type='http', auth='user', website=True)
    def page_mywork(self, **kwargs):
        user = request.env.user
        partner = user.partner_id
        # Get next shift
        shift_registration_env = request.env['shift.registration']
        member_status = partner.get_warning_member_state()
        shift_upcomming = shift_registration_env.sudo().search([
            ('shift_id.shift_template_id.is_technical', '=', False),
            ('partner_id', '=', user.partner_id.id),
            ('state', '!=', 'cancel'),
            ('exchange_state', '!=', 'replacing'),
            ('date_begin', '>=', datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S'))
        ],  order="date_begin")
        # check standard member or ftop member
        datas = {
            'is_standard_member': user.partner_id.shift_type == 'standard',
            'is_ftop_member': user.partner_id.shift_type == 'ftop',
            'shift_upcomming': shift_upcomming,
            'user': user,
            'member_status': member_status
        }
        if user.partner_id.shift_type == 'standard':
            d = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            next_registrations = partner.sudo().registration_ids.filtered(
                lambda r, d=d: r.date_begin >= d).sorted(
                lambda r: r.date_begin)
            partner.upcoming_registration_count = len(next_registrations)
            next_registrations = next_registrations.sorted(
                lambda r: r.date_begin)
            datas.update({
                'standard_point': user.partner_id.display_std_points,
                'ftop_point': user.partner_id.display_ftop_points,
                'next_registrations': next_registrations
            })
        elif user.partner_id.shift_type == 'ftop':
            datas.update({
                'ftop_point': user.partner_id.display_ftop_points
            })
        return request.render(
            'coop_memberspace.mywork', datas
        )

    @http.route('/standard/counter_classic', type='http',
        auth='user', website=True)
    def page_counter_classic(self, **kwargs):
        user = request.env.user
        shift_counter_event_env = request.env['shift.counter.event']
        shift_counter_events =  shift_counter_event_env.sudo().search([
            ('partner_id', '=', user.partner_id.id),
            ('type', '=', 'standard')
        ])
        return request.render(
            'coop_memberspace.counter',
            {
                'classic': True,
                'shift_counter_events': shift_counter_events,
                'user': user
            }
        )

    @http.route('/standard/counter_extra', type='http',
        auth='user', website=True)
    def page_counter_extra(self, **kwargs):
        user = request.env.user
        shift_counter_event_env = request.env['shift.counter.event']
        shift_counter_events =  shift_counter_event_env.sudo().search([
            ('partner_id', '=', user.partner_id.id),
            ('type', '=', 'ftop')
        ])
        return request.render(
            'coop_memberspace.counter',
            {
                'extra': True,
                'shift_counter_events_extra': shift_counter_events,
                'user': user
            }
        )

    @http.route('/standard/programmer_un_extra', type='http',
        auth='user', website=True)
    def page_programmer_un_extra(self, **kwargs):
        user = request.env.user
        tmpl = user.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.is_current)
        shift_env = request.env['shift.shift']
        shifts_available = shift_env
        if tmpl:
            shifts_available = shift_env.sudo().search([
                ('shift_template_id.is_technical', '=', False),
                ('shift_template_id', '!=', tmpl[0].shift_template_id.id),
                ('date_begin', '>=', (
                    datetime.now() + timedelta(days=1)).strftime(
                        '%Y-%m-%d 00:00:00'))
            ]).filtered(
                lambda r, user=request.env.user: user.partner_id not in
                r.registration_ids.mapped('partner_id')
                and not r.shift_template_id.shift_type_id.is_ftop
            ).sorted(key=lambda r: r.date_begin)
        return request.render(
            'coop_memberspace.counter',
            {
                'programmer_un_extra': True,
                'shifts_available': shifts_available,
                'user': user
            }
        )

    @http.route('/standard/echange_de_services', type='http', auth='user',
        website=True)
    def page_echange_de_services(self, **kwargs):
        user = request.env.user
        # Get next shift
        shift_registration_env = request.env['shift.registration']
        shift_upcomming = shift_registration_env.sudo().search([
            ('partner_id', '=', user.partner_id.id),
            ('state', 'not in', ['cancel']),
            ('exchange_state', '!=', 'replacing'),
            ('date_begin', '>=', datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')),
            ('shift_id.shift_type_id.is_ftop', '=', False)
        ], order="date_begin")
        shifts_on_market = shift_registration_env.sudo().search([
            ('partner_id', '!=', user.partner_id.id),
            ('state', '!=', 'cancel'),
            ('exchange_state', '=', 'in_progress'),
            ('date_begin', '>=', datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S'))
        ], order="date_begin")
        return request.render(
            'coop_memberspace.counter',
            {
                'echange_de_services': True,
                'shift_upcomming': shift_upcomming,
                'shifts_on_market': shifts_on_market,
                'user': user
            }
        )

    @http.route('/ftop/my_counter', type='http', auth='user', website=True)
    def page_ftop_my_counter(self, **kwargs):
        user = request.env.user
        shift_counter_event_env = request.env['shift.counter.event']
        shift_counter_events =  shift_counter_event_env.sudo().search([
            ('partner_id', '=', user.partner_id.id),
            ('type', '=', 'ftop')
        ])
        return request.render(
            'coop_memberspace.ftop_my_counter',
            {
                'is_ftop_member': True,
                'shift_counter_events': shift_counter_events,
                'user': user
            }
        )

    @http.route('/myteam', type='http', auth='user', website=True)
    def page_myteam(self, **kwargs):
        user = request.env.user
        tmpl_lines = user.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.is_current)
        shift_tmpl = tmpl_lines and tmpl_lines[0].shift_template_id or False
        coordinators = shift_tmpl and shift_tmpl.user_ids.sorted(
            key=lambda r: r.name) or []
        members = shift_tmpl and shift_tmpl.registration_ids.filtered(
            lambda r: r.is_current_participant).mapped('partner_id').filtered(
                lambda r: r.shift_type == 'standard').sorted(
            key=lambda r: r.name) or []

        alias_leader = shift_tmpl and request.env['memberspace.alias'].search(
            [('shift_id', '=', shift_tmpl.id), ('type', '=', 'coordinator')],
            limit=1) or False
        alias_leader = alias_leader and \
            alias_leader[0].alias_id.name_get()[0][1] or ''

        alias_team = shift_tmpl and \
            request.env['memberspace.alias'].search(
                [('shift_id', '=', shift_tmpl.id), ('type', '=', 'team')],
                limit=1) or False
        alias_team = alias_team and \
            alias_team[0].alias_id.name_get()[0][1] or ''

        is_leader = user.partner_id in coordinators

        return request.render(
            'coop_memberspace.myteam',
            {
                'coordinators': coordinators,
                'members': members,
                'alias_team': alias_team,
                'alias_leader': alias_leader,
                'is_leader': is_leader,
                'current_member': user.partner_id
            }
        )

    @http.route('/profile', type='http', auth='user', website=True)
    def page_myprofile(self, **kwargs):

        return request.render(
            'coop_memberspace.myprofile',
            {
                'user': request.env.user
            }
        )

    @http.route('/statistics', type='http', auth='user', website=True)
    def page_statistics(self, **kwargs):
        first_day_of_year = datetime.now().strftime("%Y-01-01 00:00:00")
        end_day_of_year = datetime.now().strftime("%Y-12-31 23:59:59")
        sales = request.env['pos.order'].sudo().search([
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('date_order', '>=', first_day_of_year),
            ('date_order', '<=', end_day_of_year)
        ])

        try:
            turnover_year_wo_tax_sql = '''
            SELECT SUM(amount_subtotal) as turnover_year_wo_tax, SUM(total_amount)
                as turnover_year_tax
            FROM pos_session
            WHERE stop_at BETWEEN '%s' AND '%s'
                AND state = 'closed'
            ''' % (first_day_of_year, end_day_of_year)
            request.env.cr.execute(turnover_year_wo_tax_sql)
            datas = request.env.cr.fetchone()
        except:
            datas = [0, 0]

        return request.render(
            'coop_memberspace.statistics',
            {
                'user': request.env.user,
                'num_of_sales': len(sales),
                'turnover_year_wo_tax': int(datas[0]),
                'turnover_year_tax': int(datas[1]),
                'average_basket': int(datas[1])/len(sales)
            }
        )

    @http.route('/documents', type='http', auth='user', website=True)
    def page_documents(self, **kwargs):
        return request.render('coop_memberspace.documents', {})

    @http.route('/proposal/confirm', type='http', auth='public', website=True)
    def proposal_confirm(self, *args, **kw):
        token = kw.get('token', False)
        action = kw.get('action', False)
        if not (token and action) or (action not in ['accept', 'refuse']):
            raise werkzeug.exceptions.NotFound()
        proposal_model = request.env['proposal']
        proposal = proposal_model.sudo().search([
            ('token', '=', token),
            ('state', '=', 'in_progress')
        ], limit=1)
        values = {}
        request.context.update({
            'lang': request.env.user.lang
        })
        if not (proposal and proposal.token_valid):
            values['bootstrap_class'] = 'alert alert-danger'
            values['message'] = _('Désolé... cette proposition n’est plus valide, elle a été retirée ou le membre a échangé ce service avec une autre personne.')
        else:
            if action == 'accept':
                proposal.accept_proposal()
                values['bootstrap_class'] = 'alert alert-success'
                values['message'] = _("Votre échange est enregistré, vos changements ont été actualisés dans la section 'Ma participation' de votre espace membre.")
            else:
                proposal.refuse_proposal()
                values['bootstrap_class'] = 'alert alert-warning'
                values['message'] = _('C’est noté ! Nous espérons que vous trouverez une option qui vous conviendra.')
        return request.render('coop_memberspace.proposal_confirm', values)
