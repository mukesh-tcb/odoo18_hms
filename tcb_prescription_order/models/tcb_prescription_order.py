from odoo import fields,models,api,_
from datetime import date,datetime


class TcbPrescriptionOrder(models.Model):
    _name = 'tcb.prescription.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    STATES = {
        'cancel': [('readonly', True)],
        'prescribed': [('readonly', True)],
    }

    
    name = fields.Char(copy=False , readonly=True , tracking=True)
    
    patient_id = fields.Many2one('hms.patient', string='Patient', required=True , tracking=True )
    
    physician_id = fields.Many2one('hms.physician', string='Prescribing Doctor', required=True , tracking=True )
    date = fields.Date(required=True , default=fields.Date.context_today , tracking=True )
    
    datetime = fields.Datetime(required=True , default=fields.Datetime.now , tracking=True )
    pregnancy_warning_bool = fields.Boolean(string="Pregnancy Warning" , tracking=True )
    
    old_prescription_id = fields.Many2one('tcb.prescription.order', string="Old Prescription")
    
    appointment_id = fields.Many2one('hms.appointment', string="Appointment Id" , tracking=True)
    
    disease_id = fields.Many2many('tcb.hms.disease' , string="Disease Id")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('prescribed', 'Prescribed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    prescription_order_line_ids = fields.One2many('tcb.prescription.line', 'prescription_order_id', string='Prescription Order Lines')
    
    prescription_notes = fields.Text(string="Prescription Notes" ,tracking=True)
    
    total_amount = fields.Float(string="Total Amount", compute="calculate_total_amount", store=True, readonly=True)
    #Calculate Total Amount 
    
    @api.depends('prescription_order_line_ids')
    def calculate_total_amount(self):
        total_amount = 0.0
        for line in self.prescription_order_line_ids:
            total_amount += line.price_subtotal
        
        self.total_amount = total_amount
    
    
    #Generate Prescription Order Number
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('tcb.prescription.order') or '/'
        return super(TcbPrescriptionOrder,self).create(vals)
    
    def action_prescribe_with_payment(self):
        self.write({'state': 'prescribed'})
        
        
    def action_prescribe_without_payment(self):
        self.write({'state': 'prescribed'})
        
    def action_cancel(self):
        self.write({'state' : 'cancelled'})
        
    
    def action_reset_to_draft(self):
        self.write({'state':'draft'})
        
    
