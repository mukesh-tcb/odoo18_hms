from odoo import fields,models,api,_



class TcbPrescriptionline(models.Model):
    _inherit = "tcb.prescription.line"
    
    ophthalmology_id = fields.Many2one('tcb.ophthalmology.evaluation', string="Ophthalmology Id")
    
    
    oph_eye = fields.Selection([
        ('both_eyes', 'BOTH EYES'),
        ('left_eye', 'LEFT EYE'),
        ('right_eye', 'RIGHT EYE')
    ], default='both_eyes', required=True)
    
    
class TcbPrescriptionOrder(models.Model):
    _inherit = "tcb.prescription.order"
    
    ophthalmology_id = fields.Many2one('tcb.ophthalmology.evaluation', string="Ophthalmology Id")
