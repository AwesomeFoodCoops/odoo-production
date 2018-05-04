# -*- coding: utf-8 -*-

import openerp
from openerp import http
from openerp.http import request
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers import main
import logging
import werkzeug
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)


class WebsiteRegisterMeeting(http.Controller):
    
    @http.route(['/discovery'], type='http',
                auth="none", website=True)
    def get_discover_meeting(self):

        main.ensure_db()

        REGISTER_USER_ID =\
            int(request.env['ir.config_parameter'].sudo(
            ).get_param('register_user_id'))
        captcha_site_key = request.env['ir.config_parameter'].sudo().get_param(
            'captcha_site_key')

        # Get event available
        event_obj = request.registry['event.event']
        event_ids = event_obj.search(request.cr, REGISTER_USER_ID, [
            ('is_discovery_meeting', '=', True),
            ('state', '=', 'confirm')
        ])
        events = event_obj.browse(request.cr, REGISTER_USER_ID, event_ids,
                                  context=request.context)
        value = {
            'events': events,
            'captcha_site_key': captcha_site_key,
        }
        return request.render("coop_membership.register_form", value)

    @http.route(['/web/membership/register/submit'], type='http',
                auth="public", methods=['POST'], csrf=False, website=True)
    def subscribe_discovery_meeting(self, **post):

        captcha_secret_key = request.env[
            'ir.config_parameter'].sudo().get_param('captcha_secret_key')
        capcha_response = post.get('g-recaptcha-response')
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {
            'secret': captcha_secret_key,
            'response': capcha_response
        }
        capcha_res = requests.post(verify_url, data=payload).json()

        if not capcha_res['success']:
            return request.render(
                "coop_membership.discovery_back")

        REGISTER_USER_ID =\
            int(request.env['ir.config_parameter'].sudo(
            ).get_param('register_user_id'))

        # Get data from form
        name = post.get('name', False)
        email = post.get('email', False)
        first_name = post.get('first_name', False)
        sex = post.get('sex', False)
        mobile = post.get('mobile', False)
        phone = post.get('phone', False)
        street1 = post.get('street1', False)
        street2 = post.get('street2', False)
        city = post.get('city', False)
        zipcode = post.get('zipcode', False)
        social_registration = post.get('social_registration', False)
        event_id = post.get('select_event', False)
        dob = post.get('dob', False)

        # conver dob to correct format in database
        try:
            dob = datetime.strptime(
                dob, "%m/%d/%Y").date().strftime('%Y-%m-%d')
        except:
            _logger.warn(
                'Convert birthdate from %s on discovery meeting form failed', dob)

        # Check email exist in database
        partner_obj = request.registry['res.partner']
        partner_id = partner_obj.search(request.cr, REGISTER_USER_ID, [
            ('email', '=', email),
        ])

        event_obj = request.registry['event.event']
        event = event_obj.browse(request.cr, REGISTER_USER_ID, int(event_id),
                                 context=request.context)

        is_event_valid = True

        # Check invalid and available seat event
        if event and event.is_discovery_meeting and event.state\
                == 'confirm':
            if event.seats_availability == 'limited' and event.seats_max\
                    and event.seats_available < 1:
                is_event_valid = False
        else:
            is_event_valid = False

        if partner_id:
            return request.render(
                "coop_membership.register_submit_form_err_email")
        elif not is_event_valid:
            return request.render(
                "coop_membership.register_submit_form_err_event")
        else:

            # create event registration
            val = {
                'event_id': event.id,
                'name': first_name + ', ' + name,
                'email': email,
            }
            attendee_id = self.create_event_registration(val, REGISTER_USER_ID)

            partner_val = {
                'name': first_name + ', ' + name,
                'sex': sex,
                'email': email,
                'street': street1,
                'street2': street2,
                'city': city,
                'zip': zipcode,
                'phone': phone,
                'mobile': mobile,
                'birthdate': dob,
            }
            # Create contact partner
            new_partner_id = self.create_contact_partner(
                partner_val, REGISTER_USER_ID)

            if new_partner_id:

                partner = partner_obj.browse(request.cr, REGISTER_USER_ID,
                                             new_partner_id,
                                             context=request.context)

                request.registry['event.registration'].write(
                    request.cr, REGISTER_USER_ID, attendee_id,
                    {'partner_id': new_partner_id},
                    context=request.context)

                if social_registration == 'yes':
                    partner.set_underclass_population()

                # Create attachment file
                # contract = partner.attach_report_in_mail()

                # Send email
                template_email = request.env.ref(
                    'coop_membership.register_confirm_email')
                if template_email:
                    # template_email.sudo().attachment_ids = [
                    #     (6, 0, (contract.ids))]
                    template_email.sudo().send_mail(attendee_id)

            return request.render(
                "coop_membership.register_submit_form_success")

    def create_event_registration(self, val, REGISTER_USER_ID):
        event_reg_obj = request.registry['event.registration']
        event_registration = event_reg_obj.create(
            request.cr, REGISTER_USER_ID, val, context=request.context)
        return event_registration

    def create_contact_partner(self, partner_val, REGISTER_USER_ID):
        partner_obj = request.registry['res.partner']
        partner_id = partner_obj.create(
            request.cr, REGISTER_USER_ID, partner_val, context=request.context)
        return partner_id
