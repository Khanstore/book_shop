odoo.define('your_module.product_configurator', function (require) {
    "use strict";

    var ProductConfigurator = require('website_sale.ProductConfigurator');

    ProductConfigurator.include({
        _onProductOptionChange: function (ev) {
            this._super(ev);
            var variant = this.product_variant;

            // Update custom field dynamically
//            if (this.selectedOptions.color === 'red') {
//                variant.custom_field = 'Red Color Selected';
//            } else {
//                variant.custom_field = 'Other Color Selected';
//            }

            // Update the custom field display on the page
            this._updateCustomFieldDisplay();
        },

        _updateCustomFieldDisplay: function () {
            var customFieldElem = document.querySelector('.publication_date');
            if (customFieldElem) {
                customFieldElem.innerHTML = this.product_variant.publication_date;
            }
        }
    });
});
