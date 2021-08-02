import locale
import pytz
import werkzeug
from datetime import date, datetime, timedelta
from odoo import http, _
from odoo.http import request
from odoo.addons.website.controllers.main import Website as WebsiteController

import logging
_logger = logging.getLogger(__name__)


class Website(WebsiteController):
    @http.route("/", type="http", auth="public", website=True)
    def index(self, **kw):
        user = request.env.user
        # Get members
        members = (
            request.env["res.partner"]
            .sudo()
            .search(
                [
                    ("is_member", "=", True),
                    (
                        "cooperative_state",
                        "not in",
                        [
                            "blocked",
                            "unpayed",
                            "not_concerned",
                            "unsubscribed",
                        ],
                    ),
                ]
            )
        )
        # Get member status
        member_status = user.partner_id.get_warning_member_state()
        # Get next shift
        shift_registration_env = request.env["shift.registration"]
        shift_registration = shift_registration_env.sudo().search(
            [
                ("shift_id.shift_template_id.is_technical", "=", False),
                ("partner_id", "=", user.partner_id.id),
                ("state", "!=", "cancel"),
                (
                    "date_begin",
                    ">=",
                    datetime.now(),
                ),
            ],
            order="date_begin",
            limit=1,
        )
        default_lang = user.lang or user.company_id.partner_id.lang
        # Get Turnover of the day
        lang = "%s.%s" % (default_lang, "utf8")
        try:
            locale.setlocale(locale.LC_TIME, lang)
        except Exception as e:
            _logger.debug("Can't set locale: %s", e)
        user_tz = user.tz or "Europe/Paris"
        local = pytz.timezone(user_tz)
        date_begin = (
            shift_registration
            and datetime.strftime(
                pytz.utc.localize(shift_registration.date_begin).astimezone(local),
                "%A, %d %B %Hh%M",
            )
            or False
        )
        week_number = request.env['shift.template']._get_week_number(date.today())
        week_name = request.env['shift.template']._number_to_letters(week_number)
        values = {
            "date_begin": date_begin and date_begin.capitalize() or False,
            'week_number': week_number,
            'week_name': week_name,
            "num_of_members": len(members),
            "member_status": member_status,
        }
        return http.request.render("coop_memberspace.homepage", values)

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        r = super().web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params["login_success"]:
            redirect = "/"
            return http.redirect_with_hash(redirect)
        return r

    @http.route("/mywork", type="http", auth="user", website=True)
    def page_mywork(self, **kwargs):
        user = request.env.user
        partner = user.partner_id
        # Get next shift
        shift_registration_env = request.env["shift.registration"]
        member_status = partner.get_warning_member_state()
        shift_upcomming = shift_registration_env.sudo().search(
            [
                ("shift_id.shift_template_id.is_technical", "=", False),
                ("partner_id", "=", user.partner_id.id),
                ("state", "!=", "cancel"),
                #("exchange_state", "!=", "replacing"),
                (
                    "date_begin",
                    ">=",
                    datetime.now(),
                ),
            ],
            order="date_begin",
        )
        # check standard member or ftop member
        datas = {
            "is_standard_member": user.partner_id.shift_type == "standard",
            "is_ftop_member": user.partner_id.shift_type == "ftop",
            "shift_upcomming": shift_upcomming,
            "user": user,
            "member_status": member_status,
        }
        if user.partner_id.shift_type == "standard":
            d = datetime.now()
            next_registrations = (
                partner.sudo()
                .registration_ids.filtered(lambda r, d=d: r.date_begin >= d)
                .sorted(lambda r: r.date_begin)
            )
            partner.upcoming_registration_count = len(next_registrations)
            next_registrations = next_registrations.sorted(
                lambda r: r.date_begin
            )
            datas.update(
                {
                    "standard_point": user.partner_id.display_std_points,
                    "ftop_point": user.partner_id.display_ftop_points,
                    "next_registrations": next_registrations,
                }
            )
        elif user.partner_id.shift_type == "ftop":
            datas.update({"ftop_point": user.partner_id.display_ftop_points})
        return request.render("coop_memberspace.mywork", datas)

    @http.route(
        "/standard/counter_classic", type="http", auth="user", website=True
    )
    def page_counter_classic(self, **kwargs):
        user = request.env.user
        shift_counter_event_env = request.env["shift.counter.event"]
        shift_counter_events = shift_counter_event_env.sudo().search(
            [
                ("partner_id", "=", user.partner_id.id),
                ("type", "=", "standard"),
            ]
        )
        return request.render(
            "coop_memberspace.counter",
            {
                "classic": True,
                "shift_counter_events": shift_counter_events,
                "user": user,
            },
        )

    @http.route(
        "/standard/counter_extra", type="http", auth="user", website=True
    )
    def page_counter_extra(self, **kwargs):
        user = request.env.user
        shift_counter_event_env = request.env["shift.counter.event"]
        shift_counter_events = shift_counter_event_env.sudo().search(
            [("partner_id", "=", user.partner_id.id), ("type", "=", "ftop")]
        )
        return request.render(
            "coop_memberspace.counter",
            {
                "extra": True,
                "shift_counter_events_extra": shift_counter_events,
                "user": user,
            },
        )

    @http.route(
        "/standard/programmer_un_extra", type="http", auth="user", website=True
    )
    def page_programmer_un_extra(self, **kwargs):
        user = request.env.user
        tmpl = user.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.is_current
        )
        shift_env = request.env["shift.shift"]
        shifts_available = shift_env
        if tmpl:
            shifts_available = (
                shift_env.sudo()
                .search(
                    [
                        ("shift_template_id.is_technical", "=", False),
                        (
                            "shift_template_id",
                            "!=",
                            tmpl[0].shift_template_id.id,
                        ),
                        (
                            "date_begin",
                            ">=",
                            (datetime.now() + timedelta(days=1)).strftime(
                                "%Y-%m-%d 00:00:00"
                            ),
                        ),
                        '|',
                        ('registration_ids', '=', False),
                        ('registration_ids.partner_id', 'not in', user.partner_id.ids),
                        ('shift_template_id.shift_type_id.is_ftop', '=', False),
                        ('state', '!=', 'cancel')
                    ],
                    order='date_begin'
                )
            )
        return request.render(
            "coop_memberspace.counter",
            {
                "programmer_un_extra": True,
                "shifts_available": shifts_available,
                "user": user,
            },
        )

    @http.route(
        "/standard/echange_de_services", type="http", auth="user", website=True
    )
    def page_echange_de_services(self, **kwargs):
        user = request.env.user
        # Get next shift
        shift_registration_env = request.env["shift.registration"]
        shift_upcomming = shift_registration_env.sudo().search(
            [
                ("partner_id", "=", user.partner_id.id),
                ("state", "not in", ["cancel"]),
                # ("exchange_state", "!=", "replacing"),
                (
                    "date_begin",
                    ">=",
                    datetime.now(),
                ),
                ("shift_id.shift_type_id.is_ftop", "=", False),
            ],
            order="date_begin",
        )
        shifts_on_market = shift_registration_env.sudo().search(
            [
                ("partner_id", "!=", user.partner_id.id),
                ("state", "!=", "cancel"),
                ("exchange_state", "=", "in_progress"),
                (
                    "date_begin",
                    ">=",
                    datetime.now(),
                ),
            ],
            order="date_begin",
        )
        return request.render(
            "coop_memberspace.counter",
            {
                "echange_de_services": True,
                "shift_upcomming": shift_upcomming,
                "shifts_on_market": shifts_on_market,
                "user": user,
            },
        )

    @http.route("/ftop/my_counter", type="http", auth="user", website=True)
    def page_ftop_my_counter(self, **kwargs):
        user = request.env.user
        shift_counter_event_env = request.env["shift.counter.event"]
        shift_counter_events = shift_counter_event_env.sudo().search(
            [("partner_id", "=", user.partner_id.id), ("type", "=", "ftop")]
        )
        return request.render(
            "coop_memberspace.ftop_my_counter",
            {
                "is_ftop_member": True,
                "shift_counter_events": shift_counter_events,
                "user": user,
            },
        )

    @http.route("/myteam", type="http", auth="user", website=True)
    def page_myteam(self, **kwargs):
        user = request.env.user
        tmpl_lines = user.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.is_current
        )
        shift_tmpl = tmpl_lines and tmpl_lines[0].shift_template_id or False
        coordinators = (
            shift_tmpl
            and shift_tmpl.user_ids.sorted(key=lambda r: r.name)
            or []
        )
        members = (
            shift_tmpl
            and shift_tmpl.registration_ids.filtered(
                lambda r: r.is_current_participant
            )
            .mapped("partner_id")
            .filtered(lambda r: r.shift_type == "standard")
            .sorted(key=lambda r: r.name)
            or []
        )

        alias_leader = (
            shift_tmpl
            and request.env["memberspace.alias"].search(
                [
                    ("shift_id", "=", shift_tmpl.id),
                    ("type", "=", "coordinator"),
                ],
                limit=1,
            )
            or False
        )
        alias_leader = (
            alias_leader and alias_leader[0].alias_id.name_get()[0][1] or ""
        )

        alias_team = (
            shift_tmpl
            and request.env["memberspace.alias"].search(
                [("shift_id", "=", shift_tmpl.id), ("type", "=", "team")],
                limit=1,
            )
            or False
        )
        alias_team = (
            alias_team and alias_team[0].alias_id.name_get()[0][1] or ""
        )

        is_leader = user.partner_id in coordinators

        return request.render(
            "coop_memberspace.myteam",
            {
                "coordinators": coordinators,
                "members": members,
                "alias_team": alias_team,
                "alias_leader": alias_leader,
                "is_leader": is_leader,
                "current_member": user.partner_id,
            },
        )

    @http.route("/profile", type="http", auth="user", website=True)
    def page_myprofile(self, **kwargs):

        return request.render(
            "coop_memberspace.myprofile", {"user": request.env.user}
        )

    @http.route("/statistics", type="http", auth="user", website=True)
    def page_statistics(self, **kwargs):
        first_day_of_year = datetime.now().strftime("%Y-01-01 00:00:00")
        end_day_of_year = datetime.now().strftime("%Y-12-31 23:59:59")
        sales_count = request.env["pos.order"].sudo().search_count([
            ("state", "in", ["paid", "done", "invoiced"]),
            ("date_order", ">=", first_day_of_year),
            ("date_order", "<=", end_day_of_year),
        ])
        pos_session = request.env['pos.session'].sudo().search(
            [
                ('stop_at', '>=', first_day_of_year),
                ('stop_at', '<=', end_day_of_year),
                ('state', '=', 'closed')
            ]
        )
        if pos_session:
            total_with_tax = sum(pos_session.mapped('order_ids.amount_total'))
            total_tax = sum(pos_session.mapped('order_ids.amount_tax'))
            datas = [(total_with_tax - total_tax), total_with_tax]
        else:
            datas = [0, 0]

        return request.render(
            "coop_memberspace.statistics",
            {
                "user": request.env.user,
                "num_of_sales": sales_count,
                "turnover_year_wo_tax": int(datas[0]),
                "turnover_year_tax": int(datas[1]),
                "average_basket": int(datas[1]) / sales_count,
            },
        )

    @http.route("/documents", type="http", auth="user", website=True)
    def page_documents(self, **kwargs):
        return request.render("coop_memberspace.documents", {})

    @http.route("/proposal/confirm", type="http", auth="public", website=True)
    def proposal_confirm(self, *args, **kw):
        token = kw.get("token", False)
        action = kw.get("action", False)
        if not (token and action) or (action not in ["accept", "refuse"]):
            raise werkzeug.exceptions.NotFound()
        proposal_model = request.env["proposal"]
        proposal = proposal_model.sudo().search(
            [("token", "=", token), ("state", "=", "in_progress")], limit=1
        )
        values = {}
        request.context = dict(request.context,
                                       lang=request.env.user.lang)
        if not (proposal and proposal.token_valid):
            values["bootstrap_class"] = "alert alert-danger"
            values["message"] = _(
                "Sorry ... this proposal is no longer valid, it has been withdrawn"
                " or the member has exchanged this service with another person."
            )
        else:
            if action == "accept":
                proposal.accept_proposal()
                values["bootstrap_class"] = "alert alert-success"
                values["message"] = _(
                    "Your exchange is saved, your changes have been updated in the"
                    " 'My participation' section of your member area."
                )
            else:
                proposal.refuse_proposal()
                values["bootstrap_class"] = "alert alert-warning"
                values["message"] = _(
                    "Noted ! We hope you find an option that works for you."
                )
        return request.render("coop_memberspace.proposal_confirm", values)
