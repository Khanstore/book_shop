odoo.define('book_shop.TrimTrackingRef', function (require) {
    "use strict";

    const fieldRegistry = require('web.field_registry');
    const basicFields = require('web.basic_fields');
    const Dialog = require('web.Dialog');

    const TrackingRefField = basicFields.FieldChar.extend({
        _onInput: function (event) {
            this._super.apply(this, arguments);
            let value = event.target.value;

            if (value && value.startsWith("0")) {
                Dialog.confirm(this, _t("This tracking number starts with 0. Do you want to trim it?"), {
                    confirm_callback: () => {
                        let trimmed = value.replace(/^0+/, "");
                        this._setValue(trimmed);
                    },
                });
            }
        },
    });

    fieldRegistry.add('trim_tracking_ref', TrackingRefField);
});
