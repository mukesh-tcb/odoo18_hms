from odoo import api,fields,models



class TCBInvoiceInherit(models.Model):
    _inherit = "tcb.invoice"    
    
    
    procedure_id = fields.Many2one('tcb.patient.procedure',string="Procedure")
    
    