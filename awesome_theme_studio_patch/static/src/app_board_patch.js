/** @odoo-module **/


import { AppBoard } from "@awesome_theme_enterprise/components/app_board/awesome_app_board";

const { patch } = require("web.utils");


patch(AppBoard.prototype, "awesome_theme_studio_app_board_patch", {

    mounted() {
        super.mounted();
        this.canEditIcons = true;
        this.el.classList.add("o_studio_home_menu");
    },

    /**
     * append new appp
     */
    get displayedApps() {
        return this.state.availableApps.concat([{
            isNewAppButton: true,
            label: "New App",
            svg: "",
        }]);
    },

    /**
     * @override
     * @private
     */
    async _openMenu(menu) {
        if (menu.isNewAppButton) {
            this.canEditIcons = false;
            return this.studio.open(this.studio.MODES.APP_CREATOR);
        } else {
            try {
                await this.studio.open(this.studio.MODES.EDITOR, menu.actionID);
                this.menus.selectMenu(menu);
            } catch (e) {
                if (e instanceof NotEditableActionError) {
                    const options = { type: "danger" };
                    this.notifications.add(
                        this.env._t("This action is not editable by Studio"),
                        options
                    );
                    return;
                }
                throw e;
            }
        }
    },

    /**
     * @private
     * @param {Object} app
     */
    onEditIconClick(app) {
        if (!this.canEditIcons) {
            return;
        }
        const editedAppData = {};
        if (app.webIconData) {
            Object.assign(editedAppData, {
                webIconData: app.webIconData,
                type: "base64",
            });
        } else {
            Object.assign(editedAppData, {
                backgroundColor: app.webIcon.backgroundColor,
                color: app.webIcon.color,
                iconClass: app.webIcon.iconClass,
                type: "custom_icon",
            });
        }

        const dialogProps = {
            editedAppData,
            appId: app.id,
        };
        this.dialog.add(IconCreatorDialog, dialogProps);
    }
});
