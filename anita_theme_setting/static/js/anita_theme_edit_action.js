/**
 * company editor action
 */
odoo.define('anita.theme_edit_action', function (require) {
    "use strict";

    var core = require('web.core');

    /**
     * @param {*} parent
     * @param {*} action
     */
    function show_theme_editor(env, action) {
        core.bus.trigger('anita_show_theme_editor', action);
    }

    core.action_registry.add('theme_edit_action', show_theme_editor);
});