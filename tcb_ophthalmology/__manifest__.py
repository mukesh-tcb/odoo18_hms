# -*- coding: utf-8 -*-

{
    'name': "Ophthalmology(CMS)",
    'summary': """
    This module is for Ophthalmology.
        """,

    'description': """ """,
    'author': "Mukesh Kumar",
    'website': "",

    'category': 'Medical',
    'version': '0.1',

    'depends': ['web','web_editor','base','mail','tcb_hms_base','tcb_prescription_order','tcb_procedure'],

    'data': [
        'security/ir.model.access.csv',
        'data/ophthalmology_complaints_data.xml',
        'data/sequence.xml',
        # 'data/update_dilation_durations.xml',
        'views/parent_view_optometry_page_ophthalmology.xml',
        'views/doctor_examination_page_ophthalmology.xml',
        'views/presenting_complaints_page_ophthalmology.xml',
        'views/patient_complaints_page_ophthalmology.xml',
        'views/ophthalmology_refraction_readings_page.xml',
        'views/examination_page.xml',
        'views/contact_lens_page_ophthalmology.xml',
        'views/diagnosis_page_ophthalmology.xml',
        'views/appointment_view_inherit_for_ophthalmology.xml',
        'views/speciality_page_ophthalmology_view.xml',
            ],
    
    'assets': {
        'web.assets_backend': [
                    # 'tcb_ophthalmology/static/src/js/drawing_widget.js',
                    'tcb_ophthalmology/static/src/xml/drawing_template.xml',
                    # 'tcb_ophthalmology/static/src/js/ophthalmology_custom.js',
                    # 'tcb_ophthalmology/static/src/js/test.js',
                    # 'tcb_ophthalmology/static/src/js/dilation_timer.js',
                    # 'tcb_ophthalmology/static/src/xml/dilation_timer.xml',
                    'tcb_ophthalmology/static/src/css/ophthalmology.css',
                    'tcb_ophthalmology/static/src/css/style.css',
                    # 'tcb_ophthalmology/static/src/js/ophthalmology_drawing.js',   
                    
                    
            ],
    },
    
    'installable': True,
    'application': True,
    }