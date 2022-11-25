/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class AwesomeSystray extends owl.Component {

    setup() {
        this.hm = useService("awesome_app_board");
        this.studio = useService("studio");
        this.env.bus.on("ACTION_MANAGER:UI-UPDATED", this, (mode) => {
            if (mode !== "new") {
                this.render();
            }
        });
    }

    get buttonDisabled() {
        return !this.studio.isStudioEditable();
    }
    
    _onClick() {
        this.studio.open();
    }
}

// replace the systray item
AwesomeSystray.template = "awesome_theme_studio_patch.SystrayItem";

export const systrayItem = {
    Component: AwesomeSystray,
    isDisplayed: (env) => env.services.user.isSystem,
};

registry.category("systray").add("AwesomeSystrayItem", systrayItem, { sequence: 1 });
