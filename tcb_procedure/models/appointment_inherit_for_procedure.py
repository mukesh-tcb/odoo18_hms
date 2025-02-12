
from odoo import api, fields, models, _

class Appointment(models.Model):
    _inherit = 'hms.appointment'

    #Smart button for procedure creating of that patient also show the count of procedure
    procedure_id = fields.Many2one('tcb.patient.procedure', string="Procedure Id")
        
    procedure_count = fields.Integer(string="Procedure Count",
        compute="_compute_procedure_count"
    )

    @api.depends('procedure_id')
    def _compute_procedure_count(self):
        for record in self:
            record.procedure_count = self.env['tcb.patient.procedure'].search_count([('patient_id', '=', record.patient_id.id),('appointment_id', '=', record.id)])

    #Smart button for procedure showing of that patient also show the count of procedure
    def action_show_procedure(self):
        self.ensure_one()
        # procedure_count = self.env['tcb.procedure.evaluation'].search_count([('patient_id', '=', self.patient_id.id)])
        action = self.env.ref("tcb_procedure.action_patient_procedure").read()[0]
        action['domain'] = [('patient_id', '=', self.patient_id.id),
                            ('appointment_id', '=', self.id),('physician_id', '=', self.physician_id.id)]
        action['context'] = {'default_patient_id': self.patient_id.id,
                            'default_appointment_id': self.id,
                            'default_physician_id': self.physician_id.id}
        return action

        
        