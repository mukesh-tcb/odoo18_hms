# -*- coding: utf-8 -*-

{
    'name': "TCB Hospitalization Module",
    'summary': """
    This module is for Hospitalization(IPD).
        """,

    'description': """ """,
    'author': "Mukesh Kumar-TCB Infotech",
    'website': "",

    'category': 'Medical',
    'version': '0.1',

    'depends': ['base','mail','tcb_hms_base','tcb_prescription_order'],

    'data': [
        'security/ir.model.access.csv',
        'reports/discharge_summary_report.xml',
        'data/sequence.xml',
        'data/bed_products_data.xml',
        'views/tcb_hospitalization_view.xml',
        'views/hospital_ward_bed_view.xml',
        'views/patient_accommodation_history_view.xml',
        'views/tcb_hms_services.xml',
        'wizard/payment_wizard_view_inherit.xml',
                    ],
    
    'assets': {
        'web.assets_backend': [
            ],
    },
    
    'installable': True,
    'application': True,
    }