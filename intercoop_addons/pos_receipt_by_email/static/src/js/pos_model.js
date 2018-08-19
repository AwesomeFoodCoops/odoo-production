/*
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
*/


odoo.define('pos_receipt_by_email.pos_model', function (require) {
    "use strict";

    var pos_model = require('point_of_sale.models');
    pos_model.load_fields("res.partner", "email_pos_receipt");

});
