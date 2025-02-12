from odoo import fields,api,models

class TCBPaymentReceiptInherit(models.Model):
    _inherit = "tcb.payment.receipt"
    
    
    
    procedure_id = fields.Many2one('tcb.patient.procedure',string="Procedure",readonly=True)
