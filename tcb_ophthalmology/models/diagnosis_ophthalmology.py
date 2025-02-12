
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class TcbDiagnosisOphthalmology(models.Model):
    _inherit = "tcb.ophthalmology.evaluation"

    # Diagnosis
    diagnosis_details_re = fields.Many2one('tcb.diagnosis.details', string="Diagnosis Details RE")
    diagnosis_details_le = fields.Many2one('tcb.diagnosis.details', string="Diagnosis Details LE")
    diagnosis_diseases_re = fields.Many2one('tcb.eye.disease', string="Diagnosis Diseases RE")
    diagnosis_diseases_le = fields.Many2one('tcb.eye.disease', string="Diagnosis Diseases LE")
    diagnosis_icd_code_re = fields.Char(string="ICD RE")
    diagnosis_icd_code_le = fields.Char(string="ICD LE")
    diagnosis_doctor_comments_re = fields.Char(string="Doctor Comments RE")
    diagnosis_doctor_comments_le = fields.Char(string="Doctor Comments LE")

    # Procedure
    diagnosis_procedure_ids = fields.One2many('tcb.eye.procedure.line', 'ophthalmology_id',string="Procedure")
    
    # OT Counselling
    diagnosis_ot_counselling_re = fields.Many2one('tcb.eye.procedure', string="OT Counselling RE")
    diagnosis_ot_counselling_le = fields.Many2one('tcb.eye.procedure', string="OT Counselling LE")
    diagnosis_ot_counselling_comments = fields.Char(string="OT Counselling Comments")

    # Treatment
    diagnosis_treatment = fields.Text(string="Treatment")

    # Speciality Page
    spec_ac_cells_re = fields.Char(string="Ac. Cells RE")
    spec_flare_re = fields.Char(string="Flare RE")
    spec_kps_re = fields.Char(string="KP's RE")
    spec_hypopyon_re = fields.Char(string="Hypopyon RE")
    spec_vt_cells_re = fields.Char(string="Vt. Cells RE")

    spec_ac_cells_le = fields.Char(string="Ac. Cells LE")
    spec_flare_le = fields.Char(string="Flare LE")
    spec_kps_le = fields.Char(string="KP's LE")
    spec_hypopyon_le = fields.Char(string="Hypopyon LE")
    spec_vt_cells_le = fields.Char(string="Vt. Cells LE")

    patient_image_clicked = fields.Binary(string="Patient Image")
    image_1920 = fields.Binary(string="Patient Image")

    #Prescription Fields 
    #Prescription Fields One 2 many 
    oph_prescription_line_ids = fields.One2many('tcb.prescription.line', 'ophthalmology_id', string="Prescription Line")
    
    oph_prescription_id = fields.Many2one('tcb.prescription.order', string="Prescription id")
    oph_old_prescription_id = fields.Many2one('tcb.prescription.order', string="Old Prescriptions")
    
    
    @api.onchange('patient_id')
    def onchange_patient_ophthalmology(self):
        if self.patient_id:
            prescription = self.env['tcb.prescription.order'].search([('patient_id', '=', self.patient_id.id),('state','=','prescribed')], order='id desc', limit=1)
            self.oph_old_prescription_id = prescription.id if prescription else False

    @api.onchange('oph_old_prescription_id')
    def get_old_prescription_lines_ophthalmology(self):
        appointment_id = self.appointment_id and self.appointment_id.id or False
        product_lines = []
        for line in self.oph_old_prescription_id.prescription_order_line_ids:
            product_lines.append((0,0,{
                'oph_eye': line.oph_eye or False,
                'product_id': line.product_id.id,
                'name': line.name,
                'price_unit': line.price_unit,
                'route_name': line.route_name,
                'frequency_id': line.frequency_id.id,
                'quantity': line.quantity,
                'prescription_days': line.prescription_days,
                'note': line.note,
                'duration_id': line.duration_id.id,
                'appointment_id': appointment_id,
                'dosage': line.dosage
            }))
        self.oph_prescription_line_ids = product_lines
        
    def copy_last_line(self):
        for line in self:
            if line.oph_prescription_line_ids:
                last_line = line.oph_prescription_line_ids[-1]
                new_line_vals = {
                    'ophthalmology_id': last_line.ophthalmology_id.id,
                    'oph_eye': last_line.oph_eye,
                    'product_id': last_line.product_id.id,
                    'name': last_line.name,
                    'price_unit': last_line.price_unit,
                    'route_name': last_line.route_name,
                    'frequency_id': last_line.frequency_id.id,
                    'quantity': last_line.quantity,
                    'prescription_days': last_line.prescription_days,
                    'note': last_line.note,
                    'duration_id': last_line.duration_id.id,
                    'appointment_id': last_line.appointment_id.id,
                    'dosage': last_line.dosage
                    }
                self.env['tcb.prescription.line'].create(new_line_vals)
        return True

    # @api.onchange('diagnosis_diseases_re', 'diagnosis_diseases_le')
    # def onchange_set_icd_code_of_disease(self):
    #     for rec in self:
    #         if rec.diagnosis_diseases_re:
    #             rec.diagnosis_icd_code_re = rec.diagnosis_diseases_re.disease_icd_code
    #         if rec.diagnosis_diseases_le:
    #             rec.diagnosis_icd_code_le = rec.diagnosis_diseases_le.disease_icd_code

    # def tcb_open_websitefrom_appointment_url(self):
    #     self.ensure_one()
    #     if self.patient_id:
    #         return {
    #             'type': 'ir.actions.act_url',
    #             'url': '/tcb/webcam/' + self._name + '/' + str(self.id),
    #             'target': 'self',
    #         }
    #     else:
    #         raise ValidationError(_("Please Save the ophthalmology and then take a picture."))

    # def tcb_webcam_retrun_action(self):
    #     self.ensure_one()
    #     return self.env.ref('tcb_hms_ophthalmology.action_tcb_ophthalmology_evaluation').id




class TcbEyeProcedure(models.Model):
    _name = "tcb.eye.procedure"

    name = fields.Char(string="Name")


class TcbEyeOTCounselling(models.Model):
    _name = "tcb.eye.ot.counselling"

    name = fields.Char(string="Name")


class TcbEyeProcedureLine(models.Model):
    _name = "tcb.eye.procedure.line"

    diagnosis_eye = fields.Selection([
        ('none', 'NONE'),
        ('both_eyes', 'BOTH EYES'),
        ('left_eye', 'LEFT EYE'),
        ('right_eye', 'RIGHT EYE')
    ], default='none', required=True)
    procedure_id = fields.Many2one('tcb.procedure.master', string="Procedure")
    doctor_comments = fields.Char(string="Doctor Comments")
    ophthalmology_id = fields.Many2one('tcb.ophthalmology.evaluation', string="Ophthalmology Id")
