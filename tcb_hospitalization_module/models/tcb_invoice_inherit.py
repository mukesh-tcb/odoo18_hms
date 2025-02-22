from odoo import api,fields,models



class TCBInvoiceInherit(models.Model):
    _inherit = "tcb.invoice"    
    
    
    hospitalization_id = fields.Many2one('tcb.hospitalization',string="Procedure")
    
    