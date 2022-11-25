/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { WebClient } from '@web/webclient/webclient';
import ThemeSetting from 'anita_theme_setting.theme_setting';


patch(WebClient.prototype, "anita_theme_setting_webclient", {

    mounted() {
        this._super.apply(this, arguments);
        this.update_setting();
    },

    /**
     * set the user setting
     */
    update_setting: function () {

        // update the style txt 
        this._update_style();
       
        //  set current theme mode
        if (ThemeSetting) {
            var cur_mode_name = ThemeSetting.cur_mode_name
            $('body').addClass(cur_mode_name);
        }
    },

    /**
     * 
     * update the style txt
     */
    _update_style: function () {
        var $body = $('body')

        if (ThemeSetting.mode_style_css) {
            var style_id = 'anita_mode_style_id';
            var styleText = ThemeSetting.mode_style_css
            var style = document.getElementById(style_id);
            if (style.styleSheet) {
                style.setAttribute('type', 'text/css');
                style.styleSheet.cssText = styleText;
            } else {
                style.innerHTML = styleText;
            }
            style && $body[0].removeChild(style);
            $body[0].appendChild(style);
        }

        // as the priority is highable
        if (ThemeSetting.style_txt) {
            var style_id = 'anita_style_id';
            var styleText = ThemeSetting.style_txt
            var style = document.getElementById(style_id);
            if (style.styleSheet) {
                style.setAttribute('type', 'text/css');
                style.styleSheet.cssText = styleText;
            } else {
                style.innerHTML = styleText;
            }
            style && $body[0].removeChild(style);
            $body[0].appendChild(style);
        }
    }
});
