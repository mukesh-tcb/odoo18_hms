# -*- coding: utf-8 -*-

{
    'name': "TCB Prescription Order Module",
    'summary': """
    This module is for Prescription Order and its management""",

    'description': """ """,
    'author': "Mukesh Kumar-TCB Infotech",
    'website': "",

    'category': 'Medical',
    'version': '0.1',

    'depends': ['base','mail','tcb_hms_base','product'],

    'data': [
        'data/sequence.xml',
        'data/tcb_prescription_data.xml',
        'security/ir.model.access.csv',
        'views/tcb_prescription_order_view.xml',
        'views/product_medicines_view.xml',
        'views/tcb_appointment_view_inherit.xml',
        # 'views/product_template_view.xml',
        ],
    
    'assets': {
        'web.assets_backend': [],
    },
    
    'installable': True,
    'application': True,
    }