
from odoo import _, api, fields, models

from odoo.exceptions import UserError, ValidationError



class TCBProcedureMasterLines(models.Model):
    _name = "tcb.patient.procedure.line"
    
    
    procedure_id = fields.Many2one('product.template', string="Procedures" ,required=True , ondelete='cascade', 
                                domain=[('hospital_product_type', '=', 'procedure')] , context ={'default_hospital_product_type': 'procedure'})
    procedure_price = fields.Float("Price", related='procedure_id.list_price' ,store=True,readonly=False)
    patient_procedure_id = fields.Many2one('tcb.patient.procedure', string="Patient Procedure ID")
    appointment_id = fields.Many2one('hms.appointment', related='patient_procedure_id.appointment_id', string="Appointment ID")
