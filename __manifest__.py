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
    'depends' : ['website_sale','base','product','accountant','purchase','point_of_sale'],
    'author': 'SM Ashraf',
    'application': False,
    'data': [
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/partner_view.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/pos_product.xml',
        'views/website.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'assets': {
        'point_of_sale._assets_pos': [
            'book_shop/static/src/**/*',
            ],
        },
    }
