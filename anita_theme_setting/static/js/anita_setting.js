odoo.define('awesome.settings', function (require) {
    "use strict";

    var settings = require('base.settings')
    var BaseSettingRenderer = settings.Renderer

    var BaseSettingRenderer = BaseSettingRenderer.include({

        events: _.extend({}, BaseSettingRenderer.prototype.events, {
            "click .anita_setting_toggler": "_on_toggler_click"
        }),

        _on_toggler_click: function (event) {
            if (this.$('.settings_tab').hasClass('hide')) {
                this.$('.settings_tab').removeClass('hide')
                this.$('.anita_setting_toggler .fa-angle-double-left').removeClass('d-none')
                this.$('.anita_setting_toggler .fa-angle-double-right').addClass('d-none')
            } else {
                this.$('.settings_tab').addClass('hide')
                this.$('.anita_setting_toggler .fa-angle-double-left').addClass('d-none')
                this.$('.anita_setting_toggler .fa-angle-double-right').removeClass('d-none')
            }
        }
    });
});
