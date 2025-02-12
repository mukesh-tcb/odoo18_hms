from odoo import fields,api,models



class PaymentWizardInherit(models.TransientModel):
    _inherit='payment.wizard'
    
    
    hospitalization_id = fields.Many2one('tcb.hospitalization',stirng="Hospitalization Id")