
from odoo import _, api, fields, models

from odoo.exceptions import UserError, ValidationError



class TCBProcedureMasterLines(models.Model):
    _name = "tcb.patient.procedure.line"
    
    
    procedure_id = fields.Many2one('tcb.procedure.master', string="Procedures")
    procedure_price = fields.Float("Price", related='procedure_id.procedure_price' ,force_save=True, store=True)
    patient_procedure_id = fields.Many2one('tcb.patient.procedure', string="Patient Procedure ID")
    appointment_id = fields.Many2one('hms.appointment', related='patient_procedure_id.appointment_id', string="Appointment ID")
