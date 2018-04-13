/*############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2012 OpenERP SA (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################*/

openerp.web_shortcuts = function (instance) {

var QWeb = instance.web.qweb,
    _t = instance.web._t;

instance.web_shortcuts.Shortcuts = instance.web.Widget.extend({
    template: 'Systray.Shortcuts',

    init: function() {
        this._super();
        this.on('load', this, this.load);
        this.on('add', this, this.add);
        this.on('display', this, this.display);
        this.on('remove', this, this.remove);
        this.on('click', this, this.click);
        this.model = new instance.web.Model('web.shortcut');
    },
    start: function() {
        var self = this;
        this._super();
        this.trigger('load');
        this.$el.on('click', '.oe_systray_shortcuts_items a', function() {
            self.trigger('click', $(this));
        });
    },
    load: function() {
        var self = this;
        this.$el.find('.oe_systray_shortcuts_items').empty();
        return this.model.call('get_user_shortcuts', [
            instance.session.uid,
            instance.web.pyeval.eval('context', {})
        ]).done(function(shortcuts) {
            _.each(shortcuts, function(sc) {
                self.trigger('display', sc);
            });
        });
    },
    add: function (sc) {
        var self = this;
        this.model.call('create', [sc]).then(function(out){
            self.trigger('load');
        });
    },
    display: function(sc) {
        var self = this;
        this.$el.find('.oe_systray_shortcuts_items').append();
        var $sc = $(QWeb.render('Systray.Shortcuts.Item', {'shortcut': sc}));
        $sc.appendTo(self.$el.find('.oe_systray_shortcuts_items'));
    },
    remove: function (menu_id) {
        var menu_id = this.session.active_id;
        var $shortcut = this.$el.find('.oe_systray_shortcuts_items li a[data-id=' + menu_id + ']');
        var shortcut_id = $shortcut.data('shortcut-id');
        $shortcut.remove();
        this.model.call('unlink', [shortcut_id]);
    },
    click: function($link) {
        var self = this,
            id = $link.data('id');
        self.session.active_id = id;
        // TODO: Use do_action({menu_id: id, type: 'ir.actions.menu'})
        new instance.web.Model('ir.ui.menu').query(['action']).filter([['id', '=', id]]).context(null).all().then(function(menu) {
            var action_str = menu[0].action;
            var action_str_parts = action_str.split(',');
            var action_id = parseInt(action_str_parts[1])
            self.rpc('/web/action/load', {'action_id': action_id}).done(function(action) {
                instance.webclient.on_menu_action({action_id: action.id});
            });
        });
        this.$el.find('.oe_systray_shortcuts').trigger('mouseout');
    },
    has: function(menu_id) {
        return !!this.$el.find('a[data-id=' + menu_id + ']').length;
    }
});

instance.web.UserMenu.include({
    do_update: function() {
        var self = this;
        this._super.apply(this, arguments);
        this.update_promise.done(function() {
            if (self.shortcuts) {
                self.shortcuts.trigger('load');
            } else {
                self.shortcuts = new instance.web_shortcuts.Shortcuts(self);
                self.shortcuts.appendTo(instance.webclient.$el.find('.oe_systray'));
            }
        });
    },
});

instance.web.ViewManagerAction.include({
    switch_mode: function (view_type, no_store) {
        var self = this;
        this._super.apply(this, arguments).done(function() {
            self.shortcut_check(self.views[view_type]);
        });
    },
    shortcut_check : function(view) {
        var self = this;
        var shortcuts_menu = instance.webclient.user_menu.shortcuts;
        var grandparent = this.getParent() && this.getParent().getParent();
        // display shortcuts if on the first view for the action
        var $shortcut_toggle = this.$el.find('.oe_shortcuts_toggle');
        if (!this.action.name ||
                !(view.view_type === this.views_src[0].view_type
                    && view.view_id === this.views_src[0].view_id)) {
            $shortcut_toggle.hide();
            return;
        }
        // Anonymous users don't have user_menu
        if (shortcuts_menu) {
            $shortcut_toggle.toggleClass('oe_shortcuts_remove', shortcuts_menu.has(self.session.active_id));
            $shortcut_toggle.unbind("click").click(function() {
                if ($shortcut_toggle.hasClass("oe_shortcuts_remove")) {
                    shortcuts_menu.trigger('remove', self.session.active_id);
                } else {
                    shortcuts_menu.trigger('add', {
                        'user_id': self.session.uid,
                        'menu_id': self.session.active_id,
                        'name': self.action.name
                    });
                }
                $shortcut_toggle.toggleClass("oe_shortcuts_remove");
            });
        }
    }
});

};
