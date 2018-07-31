# -*- coding: utf-8 -*-

import openerp
from openerp.addons.web import http
from openerp.http import request
from openerp import tools
from datetime import datetime
import pytz
import locale


class Website(openerp.addons.website.controllers.main.Website):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        user = request.env.user
        # Get member status
        member_status = user.partner_id.get_warning_member_state()

        # Get next shift
        shift_registration_env = request.env['shift.registration']
        shift = shift_registration_env.sudo().search(
            [
                ('partner_id', '=', user.partner_id.id),
                ('state', '!=', 'cancel'),
                ('date_begin', '>=', datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S'))
            ],
            order="date_begin", limit=1
        )

        # Get Turnover of the day
        lang = user.lang and (str(user.lang) + '.utf8') or 'fr_FR.utf8'
        locale.setlocale(locale.LC_TIME, lang)
        user_tz = user.tz or 'Europe/Paris'
        local = pytz.timezone(user_tz)
        date_begin = shift and datetime.strftime(pytz.utc.localize(
            datetime.strptime(
            shift.date_begin, "%Y-%m-%d %H:%M:%S")).astimezone(
            local),"%A, %B %d %Hh%M") or False

        local_dt = local.localize(datetime.strptime(
            '2018-06-29 18:17:00', '%Y-%m-%d %H:%M:%S'))
        start_local_native_dt = datetime.strptime(
            local_dt.strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S')
        start_local_tz_dt = local.localize(start_local_native_dt)
        start_utc_dt = start_local_tz_dt.astimezone(pytz.utc)

        turnover_the_day = request.env['pos.order'].sudo().search(
            [('state', '=', 'paid'),
             ('date_order', '>=', start_utc_dt.strftime('%Y-%m-%d %H:%M:%S')),
             ('date_order', '<=', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))]
        )
        turnover_the_day = sum(item.amount_total for item in turnover_the_day)

        values = {
            'date_begin': date_begin and date_begin.title() or False,
            'shift': shift,
            'turnover_the_day': turnover_the_day,
            'member_status': member_status
        }
        return http.request.render('foodcoop_memberspace.homepage', values)

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        r = super(Website, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            redirect = '/'
            return http.redirect_with_hash(redirect)
        return r

    @http.route('/mywork', type='http', auth='user', website=True)
    def page_mywork(self, **kwargs):
        user = request.env.user
        partner = user.partner_id
        # check standard member or ftop member
        datas = {
            'is_standard_member': user.partner_id.shift_type == 'standard',
            'is_ftop_member': user.partner_id.shift_type == 'ftop'
        }
        if user.partner_id.shift_type == 'standard':
            d = datetime.now()
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
            'foodcoop_memberspace.mywork', datas
        )

    @http.route('/standard/counter_classic', type='http',
        auth='user', website=True)
    def page_counter_classic(self, **kwargs):
        return request.render(
            'foodcoop_memberspace.counter',
            {
                'classic': True
            }
        )

    @http.route('/standard/counter_extra', type='http',
        auth='user', website=True)
    def page_counter_extra(self, **kwargs):
        return request.render(
            'foodcoop_memberspace.counter',
            {
                'extra': True
            }
        )

    @http.route('/standard/programmer_un_extra', type='http', auth='user', website=True)
    def page_programmer_un_extra(self, **kwargs):
        return request.render(
            'foodcoop_memberspace.counter',
            {
                'programmer_un_extra': True
            }
        )

    @http.route('/standard/echange_de_services', type='http', auth='user', website=True)
    def page_echange_de_services(self, **kwargs):
        return request.render(
            'foodcoop_memberspace.counter',
            {
                'echange_de_services': True
            }
        )

    @http.route('/ftop/my_counter', type='http', auth='user', website=True)
    def page_ftop_my_counter(self, **kwargs):
        return request.render(
            'foodcoop_memberspace.ftop_my_counter',
            {
                'is_ftop_member': True,
            }
        )

    @http.route('/myteam', type='http', auth='user', website=True)
    def page_myteam(self, **kwargs):
        return request.render(
            'foodcoop_memberspace.myteam',
            {}
        )
