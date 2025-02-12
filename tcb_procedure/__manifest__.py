# -*- coding: utf-8 -*-

{
    'name': "TCB Procedure Module",
    'summary': """
    This module is for Procedures and its management""",

    'description': """ """,
    'author': "Mukesh Kumar-TCB Infotech",
    'website': "",

    'category': 'Medical',
    'version': '0.1',

    'depends': ['base','mail','tcb_hms_base'],

    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/tcb_procedure_master_view.xml',
        'views/tcb_patient_procedure_view.xml',
        'wizard/payment_wizard_view_inherit.xml',
        'views/tcb_payment_receipt.xml',
        'views/appointment_view_inherit_for_procedure.xml',
        ],
    
    'assets': {
        'web.assets_backend': [],
    },
    
    'installable': True,
    'application': True,
    }