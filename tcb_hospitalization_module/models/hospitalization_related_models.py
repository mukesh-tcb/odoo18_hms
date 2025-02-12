from odoo import api, fields, models, _
from odoo.exceptions import UserError



class TcbProcedureType(models.Model):
    _name = "tcb.procedure.type"
    _description = "This is the custom Procedure Type model"
    
    
    name = fields.Char(string="Procedure Type")


class TcbPatientCategory(models.Model):
    _name = "tcb.patient.category"
    _description = "This is the custom Patient Category model"
    
    name = fields.Char(string="Patient Category")


class TcbHmsServices(models.Model):
    _name = "tcb.hms.services"
    _description = "This is the custom Services charges for hospitalization"
    
    name = fields.Char(string="Name")
    price = fields.Float(string="Price")
    max_limit = fields.Integer(string="Max Limit",default=1)


class TcbHmsServicesLines(models.Model):
    _name = "tcb.hms.services.lines"
    _description = "This is the custom Services charges for hospitalization"
    
    
    name = fields.Char(string="Name",related='service_id.name',readonly=False)
    datetime = fields.Datetime(string="Date",default=fields.Datetime.today(),readonly=False)
    add_in_bill = fields.Boolean(string="Add in Bill" , default=True,readonly=False)
    service_id = fields.Many2one('tcb.hms.services', string="Service",readonly=False)
    price = fields.Float(string="Price" , related = "service_id.price",readonly=False)
    quantity = fields.Integer(string="Quantity",readonly=False,default=1)
    hospitalization_id = fields.Many2one('tcb.hospitalization', string="Hospitalization",readonly=False)
    max_limit = fields.Integer(string="Max Limit",related='service_id.max_limit',readonly=True)    
    
    # api.depends('quantity','service_id.max_limit')
    @api.onchange('quantity','max_limit','service_id')
    def _onchange_quantity(self):
        if self.quantity > self.max_limit and self.max_limit != 0:
            raise UserError("Max limit reached for %s"%self.service_id.name)
    
    

class DischargePrescriptionLines(models.Model):
    _name = "discharge.prescription.lines"
    _description = "This is the custom Discharge Prescription Lines model"
    
    
    hospitalization_id = fields.Many2one('tcb.hospitalization',string="Linking Field")
    eye_selection = fields.Selection([
        ('left_eye', 'Left Eye'),
        ('right_eye', 'Right Eye'),
        ('both_eye', 'Both Eye'),
        ('tab','Tab'),
        ('syrup','Syrup'),
        ('capsule','Capsule'),
    ], string='Eye')
    product_id = fields.Many2one('product.product', ondelete="cascade", string='Product', domain=[('hospital_product_type', '=', 'medicament')], context ={'default_hospital_product_type': 'medicament','default_is_medicament_product':True})
    frequency_id = fields.Many2one('tcb.prescription.frequency', ondelete="cascade", string='Frequency')
    notes = fields.Text(string="Notes")

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    
class FollowUpLines(models.Model):
    _name="followup.line"
    _description="Follow Up Lines"

    hospitalization_id = fields.Many2one('tcb.hospitalization',string="Linking Field")
    follow_up = fields.Date(string="Follow Up")
    clinical_examination = fields.Html(string="Clinical Examination")
    treatment = fields.Html(string="Treatment")

