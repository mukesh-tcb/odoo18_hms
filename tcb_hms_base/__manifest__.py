# -*- coding: utf-8 -*-

{
    'name': "Clinic Management System(Base)",
    'summary': """
    This module is for Clinic  """,

    'description': """ """,
    'author': "Mukesh Kumar-TCB Infotech",
    'website': "",

    'category': 'Hospitalization',
    'version': '0.1',

    'depends': ['base','mail','product',],

    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        # 'views/hms_menus.xml',
            'views/patient_view.xml',
            'reports/report_tcb_invoice.xml',
            'views/product_template_inherit.xml',
            'views/physician_view.xml',
            'reports/report_actions.xml',
            'views/appointment_view.xml',
            'wizard/payment_wizard_view.xml',
            'reports/appointment_report.xml',
            'reports/header_footer.xml',
            'views/tcb_invoice_view.xml',
            'views/tcb_payment_receipt_view.xml',
            'views/res_company_inherit.xml',
            
            ],
    
    'assets': {
        'web.assets_backend': [],
    },
    
    'installable': True,
    'application': True,
    }