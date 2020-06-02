odoo.define('coop_account.export_wrong_reconciliation_move_lines', function(require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var crash_manager = require('web.crash_manager');
    var rpc = require('web.rpc');

    function export_wrong_reconciliation_move_lines() {
        rpc.query({
            model: 'account.move.line',
            method: 'export_wrong_reconciliation_ml',
            context: session.user_context || {},
        }).then(function(data) {
            $.blockUI();
            session.get_file({
                url: '/web/export/xls_view',
                data: {
                    data: data
                },
                complete: $.unblockUI
            });
        })
        .fail(function() {
            crash_manager.rpc_error.bind(crash_manager)
        });
    }

    core.action_registry.add("export_wrong_reconciliation_move_lines", export_wrong_reconciliation_move_lines);
});