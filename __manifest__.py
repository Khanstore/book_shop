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
    'depends' : ['website_sale','website','base','product','accountant','purchase','point_of_sale'],
    'author': 'SM Ashraf',
    'application': False,
    'data': [
        'security/ir.model.access.csv',
        'data/product.category.csv',
        'data/product.public.category.csv',
        'data/book.binding.type.csv',
        'data/book_shop.xml',
        'views/product.xml',
        'views/partner_view.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/pos_product.xml',
        'views/website.xml',
        'views/stock_picking.xml',
        'views/invoice.xml',
        'reports/product_product_templates.xml',
        'reports/invoice.xml',
        'data/book_shop_pages.xml',
        'wizard/wiard_views.xml',
        'reports/daily_admin_report.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'assets': {
        'point_of_sale._assets_pos': [
            'book_shop/static/src/**/*',
            ],
        'website.assets_frontend': [
            'book_shop/static/src/js/product_configurator.js',  # Include your JS file here
        ],
        },
    }
