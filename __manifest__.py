# -*- coding: utf-8 -*-

{
    'name': "Book Shop",
    'description':"""
Customisation for a Book Shop
=============================
EDI is the electronic interchange of business information using a standardized format.

This is the base module for import and export of invoices in various EDI formats, and the
the transmission of said documents to various parties involved in the exchange (other company,
governements, etc.)
    """,
    'version': '18.0.1.0.0',
    'category': 'Others',
    'depends' : ['base','website_sale','website','stock','product','account_followup','accountant','account','purchase','point_of_sale'],
    'author': 'SM Ashraf',
    'application': False,
    # 'post_init_hook': 'cleanup_old_data',

    'data': [
        'security/ir.model.access.csv',
        'data/product.category.csv',
        'data/product.public.category.csv',
        'data/book.binding.type.csv',
        'data/book_shop.xml',
        'data/product.genre.csv',
        'data/res.lang.csv',
        'views/product.xml',
        'views/partner_view.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/pos_product.xml',
        'views/website.xml',
        'views/stock_picking.xml',
        'views/invoice.xml',
        'views/templates.xml',
        'views/res_thana.xml',
        'views/account_payment.xml',
        'reports/product_product_templates.xml',
        'reports/invoice.xml',
        'reports/sale_order.xml',
        'data/book_shop_pages.xml',
        'reports/stock_piking.xml',
        'views/khan_store_page.xml',
        'views/menu.xml',
        'todo_applet/todo_applet_view.xml',
        'wizard/wizard_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'assets': {
        'point_of_sale._assets_pos': [
            'book_shop/static/src/css/pos_image_fix.css',
            'book_shop/static/src/xml/pos_product_card.xml',
            # 'book_shop/static/src/css/pos_receipt.css',
            # 'book_shop/static/src/xml/pos_receipt.xml',
            'book_shop/static/src/xml/receipt_header.xml',
            ],
        'web.assets_backend': [
                # 'book_shop/static/src/js/trim_tracking.js',
            ],
        'web.assets_frontend': [
            # 'book_shop/static/src/css/website.css',  # Include your css file here
            'book_shop/static/src/css/report_style.scss',  # Include your css file here
            'book_shop/static/src/js/product_pages.js',  # Include your JS file here
        ],
        },
    }
