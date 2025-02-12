
from odoo import api, fields, models, _

class Appointment(models.Model):
    _inherit = 'hms.appointment'

    #Smart button for prescription creating of that patient also show the count of prescription
    prescription_id = fields.Many2one('tcb.prescription.order', string="Prescription Id")
        
    prescription_count = fields.Integer(string="Prescription Count",
        compute="_compute_prescription_count"
    )

    @api.depends('prescription_id')
    def _compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['tcb.prescription.order'].search_count([('patient_id', '=', record.patient_id.id),('appointment_id', '=', record.id)])

    #Smart button for prescription showing of that patient also show the count of prescription
    def action_show_prescription(self):
        self.ensure_one()
        # prescription_count = self.env['tcb.prescription.evaluation'].search_count([('patient_id', '=', self.patient_id.id)])
        action = self.env.ref("tcb_prescription_order.action_tcb_prescription_order").read()[0]
        action['domain'] = [('patient_id', '=', self.patient_id.id),
                            ('appointment_id', '=', self.id),('physician_id', '=', self.physician_id.id)]
        action['context'] = {'default_patient_id': self.patient_id.id,
                            'default_appointment_id': self.id,
                            'default_physician_id': self.physician_id.id}
        return action

        
        