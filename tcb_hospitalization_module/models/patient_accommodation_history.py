from odoo import fields,api,models,_
from odoo.exceptions import ValidationError

class PatientAccommodationHistory(models.Model):
    _name = "patient.accommodation.history"
    _rec_name = "patient_id"
    _description = "Patient Accommodation History"


    hospitalization_id = fields.Many2one('tcb.hospitalization', ondelete="cascade", string='Inpatient')
    
    patient_id = fields.Many2one('hms.patient', ondelete="restrict", string='Patient', required=True)
    ward_id = fields.Many2one('hospital.ward', ondelete="restrict", string='Ward/Room')
    bed_id = fields.Many2one('hospital.bed', ondelete="restrict", string='Bed No.')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')

    @api.constrains('end_date')
    def _check_end_date(self):
        for rec in self:
            if rec.end_date:
                if rec.end_date < rec.start_date:
                    raise ValidationError("End Date cannot be less than Start Date")

