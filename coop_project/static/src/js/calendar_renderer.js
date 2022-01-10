odoo.define('coop_project.CalendarRenderer', function (require) {
    "use strict";

    var CalendarRenderer = require('web.CalendarRenderer');
    var core = require('web.core');
    var qweb = core.qweb;
    var config = require('web.config');
    var session = require('web.session');

    CalendarRenderer.include({
        _eventRender: function (event) {
            var qweb_context = {
                event: event,
                fields: this.state.fields,
                format: this._format.bind(this),
                isMobile: config.device.isMobile,
                read_only_mode: this.read_only_mode,
                record: event.record,
                user_context: session.user_context,
                widget: this,
            };
            this.qweb_context = qweb_context;
            if (_.isEmpty(qweb_context.record)) {
                return '';
            } else {
                return (this.qweb || qweb).render("calendar-box", qweb_context);
            }
        },
    });
});
