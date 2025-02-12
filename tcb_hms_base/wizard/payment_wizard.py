from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PaymentWizard(models.TransientModel):
    _name = 'payment.wizard'
    _description = 'Payment Wizard'

    # Fields similar to payment receipt model
    patient_id=fields.Many2one('hms.patient', string="Patient")
    appointment_id = fields.Many2one('hms.appointment', string='Appointment')
    payment_amount = fields.Float(string='Payment Amount', required=True)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today)
    payment_mode = fields.Selection([ ('cash', 'Cash'), ('bank', 'Bank'),], string='Payment Mode', default='cash')
    reference = fields.Char(string='Reference')
    
    refund_reason = fields.Char(string="Refund Reason")
    payment_type = fields.Selection([('receive', 'Receive'), ('send', 'Send')], string='Payment Type', default='receive')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft')
    
    invoice_id = fields.Many2one('tcb.invoice', string="Invoice")
    currency_id = fields.Many2one('res.currency', string='Currency', 
        default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', 
        default=lambda self: self.env.company)
    
    @api.model
    def default_get(self, fields_list):
        # Pre-fill data from active appointment if available
        defaults = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        
        if active_model == 'hms.appointment' and active_id:
            appointment = self.env['hms.appointment'].browse(active_id)
            defaults['appointment_id'] = active_id
            defaults['patient_id'] = appointment.patient_id.id
        
        return defaults

    def action_confirm_payment(self):
        """
        Confirm payment and create payment receipt
        """
        self.ensure_one()
        
        # Validate payment_amount
        if self.payment_amount <= 0:
            raise ValidationError(_("Payment payment_amount must be positive"))
        
        # Create payment receipt
        payment_receipt = self.env['tcb.payment.receipt'].create({
            'patient_id': self.patient_id.id,
            'appointment_id': self.appointment_id.id,
            'payment_amount': self.payment_amount,
            'payment_date': self.payment_date,
            'payment_mode': self.payment_mode,  
            'payment_type': self.payment_type,
            'invoice_id': self.invoice_id.id,
        })
        # Confirm the payment receipt
        payment_receipt.action_post()
        
        # Update appointment payment status if needed
        if self.appointment_id:
            self.appointment_id.appointment_payment_state = 'fully_paid'
        
        # Return action to show created payment receipt
        return {
            'type': 'ir.actions.act_window_close',
        }
    def action_reverse_payment(self):
        """
        Confirm payment and create reverse payment receipt
        """
        self.ensure_one()
        
        # Validate payment_amount
        if self.payment_amount <= 0:
            raise ValidationError(_("Payment payment_amount must be positive"))
        
        # Create payment receipt
        payment_receipt = self.env['tcb.payment.receipt'].create({
            'patient_id': self.patient_id.id,
            'appointment_id': self.appointment_id.id,
            'payment_amount': self.payment_amount,
            'payment_date': self.payment_date,
            'payment_mode': self.payment_mode,  
            'payment_type': self.payment_type,
            'invoice_id': self.invoice_id.id,
            'refund_reason': self.refund_reason
        })
        # Confirm the payment receipt
        payment_receipt.action_post()
        # Update appointment payment status if needed
        if self.appointment_id:
            self.appointment_id.appointment_payment_state = 'fully_paid'
        # Return action to show created payment receipt
        return {
            'type': 'ir.actions.act_window_close',
        }
    def action_cancel(self):
        """
        Cancel the payment wizard
        """
        self.state = 'cancelled'
        return {'type': 'ir.actions.act_window_close'}