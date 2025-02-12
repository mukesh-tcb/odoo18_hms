
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, date


class TCBPaymentReceipt(models.Model):
    _name = "tcb.payment.receipt"
    _description = "This is the custom Payment Receipt model"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    
    @api.model
    def _get_financial_year(self):
        today = date.today()
        if today.month < 4:
            financial_year_start = date(today.year - 1, 4, 1)
            financial_year_end = date(today.year, 3, 31)
        else:
            financial_year_start = date(today.year, 4, 1)
            financial_year_end = date(today.year + 1, 3, 31)
        return financial_year_start, financial_year_end

    @api.model
    def _get_next_sequence(self, payment_mode, payment_type):
        # Determine prefix based on payment mode and type
        if payment_type == 'send':
            prefix_map = {
                'cash': 'RCSH-',
                'bank': 'RBNK-'
            }
        else:
            prefix_map = {
                'cash': 'CSH-',
                'bank': 'BNK-'
            }
        
        prefix = prefix_map.get(payment_mode, 'CSH-')
        
        # Get financial year
        fy_start, fy_end = self._get_financial_year()
        
        # Construct domain for sequence
        domain = [
            ('payment_date', '>=', fy_start),
            ('payment_date', '<=', fy_end),
            ('payment_mode', '=', payment_mode),
            ('payment_type', '=', payment_type)
        ]
        
        # Count existing records and generate sequence
        count = self.search_count(domain)
        return f"{prefix}{fy_start.year}-{count + 1:05d}"

    name=fields.Char(string="Payment Recipt Number" , copy=False, compute='_compute_name', store=True,readonly=False,tracking=True) 
    
    payment_date=fields.Date(string="Payment Date" , default=fields.Date.context_today,tracking=True)
    
    payment_mode=fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], string="Payment Mode" , default='cash',tracking=True)
    
    payment_datetime=fields.Datetime(string="Payment Date Time", default=fields.Datetime.now,tracking=True)
    
    patient_id=fields.Many2one('hms.patient', string="Patient",tracking=True)
    
    payment_amount=fields.Float(string="Payment Amount",tracking=True)
    
    payment_type = fields.Selection([('receive', 'Receive'), ('send', 'Send')], string="Payment Type" , default='receive',tracking=True)
    
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'),('cancelled', 'Cancelled')], string="Status", default='draft',tracking=True)
    
    appointment_id = fields.Many2one('hms.appointment', string="Appointment",tracking=True)
        
    physician_id = fields.Many2one('hms.physician', string="Physician",tracking=True)
    
    invoice_id = fields.Many2one('tcb.invoice', string="Invoice",tracking=True)
    
    refund_reason = fields.Char(string="Refund Reason",tracking=True)
    
    # memo = fields.Char(string="Memo",tracking=True)
    
    
    
    @api.depends('payment_mode', 'payment_type', 'payment_date')
    def _compute_name(self):
        for record in self:
            if record.payment_mode and record.payment_type and record.payment_date:
                record.name = self._get_next_sequence(
                    record.payment_mode, 
                    record.payment_type
                )
            else:
                record.name = False

    def action_post(self):
        for record in self:
            if not record.name:
                record._compute_name()
            record.state = 'posted'
            
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
            

    def action_reset_to_draft(self):
        for record in self:
            record.state = 'draft'
            
    @api.onchange('appointment_id')
    def _onchange_appointment(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id
            self.physician_id = self.appointment_id.physician_id
            self.payment_amount = self.appointment_id.amount_total
            self.payment_date = fields.Date.today()
            self.payment_mode = 'cash' # Default payment mode
            self.payment_type = 'receive'# Default payment type