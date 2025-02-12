from odoo import fields,api,models



class PaymentWizardInherit(models.TransientModel):
    _inherit='payment.wizard'
    
    
    procedure_id = fields.Many2one('tcb.patient.procedure',stirng="Procedure Id")