
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Appointment(models.Model):
    _inherit = 'hms.appointment'

    #Smart button for ophthalmology creating of that patient also show the count of ophthalmology
    ophthalmology_id = fields.Many2one('tcb.ophthalmology.evaluation', string="Ophthalmology")
    ophthalmology_created = fields.Boolean(string="Ophthalmology Created", default=False)
    def action_create_ophthalmology_request(self):
        self.ensure_one()
        if self.state in ['draft', 'confirmed']:
            ophthalmology = self.env['tcb.ophthalmology.evaluation'].create({
                'patient_id': self.patient_id.id,
                'physician_id': self.physician_id.id,
                'appointment_id': self.id,
            })
            self.ophthalmology_id = ophthalmology
            self.ophthalmology_created = True
            print("ophthalmology-----------", ophthalmology)
            print("ophthalmology_created-----------", self.ophthalmology_created)
            return ophthalmology
        
        
    ophthalmology_count = fields.Integer(string="Ophthalmology Count",
        compute="_compute_ophthalmology_count"
    )

    @api.depends('ophthalmology_id','ophthalmology_created')
    def _compute_ophthalmology_count(self):
        for record in self:
            record.ophthalmology_count = self.env['tcb.ophthalmology.evaluation'].search_count([('patient_id', '=', record.patient_id.id),('appointment_id', '=', record.id)])

    #Smart button for ophthalmology showing of that patient also show the count of ophthalmology
    def action_show_ophthalmology(self):
        self.ensure_one()
        # ophthalmology_count = self.env['tcb.ophthalmology.evaluation'].search_count([('patient_id', '=', self.patient_id.id)])
        action = self.env.ref("tcb_ophthalmology.ophthalmology_action").read()[0]
        action['domain'] = [('patient_id', '=', self.patient_id.id),
                            ('appointment_id', '=', self.id),('physician_id', '=', self.physician_id.id)]
        action['context'] = {'default_patient_id': self.patient_id.id,
                            'default_appointment_id': self.id,
                            'default_physician_id': self.physician_id.id}
        return action

        
        