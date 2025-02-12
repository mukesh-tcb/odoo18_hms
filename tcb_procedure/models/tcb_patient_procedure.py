from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class TcbPatientProcedure(models.Model):
    _name = "tcb.patient.procedure"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Patient Procedure"
    
    STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    # Basic Fields
    name = fields.Char(string="Name", states=STATES, tracking=True)
    patient_id = fields.Many2one('hms.patient', string='Patient', required=True, states=STATES, tracking=True)
    appointment_id = fields.Many2one('hms.appointment', string='Appointment', states=STATES, tracking=True)
    physician_id = fields.Many2one('hms.physician', string='Physician', required=True, states=STATES, tracking=True)
    
    # Date Fields
    datetime = fields.Datetime(string='Date', default=fields.Datetime.now, tracking=True)
    date = fields.Date(string='Date', default=fields.Date.today, tracking=True)
    
    # State Field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)


    #Procedure Lines Related Fields
    procedure_line_ids = fields.One2many('tcb.patient.procedure.line', 'patient_procedure_id', string='Procedure Lines', states=STATES, tracking=True)
    
    # Description
    description = fields.Text(string="Description", states=STATES, tracking=True)

        # Payment fields
    procedure_payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
        ('partially_reversed', 'Partially Reversed'),
        ('fully_reversed', 'Fully Reversed'),
    ], default='not_paid', string='Payment Status', compute='_compute_procedure_payment_status')
    
    procedure_payment_line_ids = fields.One2many('tcb.payment.receipt', 'procedure_id', string='Payment Lines')
    
    procedure_total_amount = fields.Float(string='Total Amount',store=True,tracking=True , compute='_compute_total_procedure_amount')
    
    procedure_amount_pending = fields.Float(string='Pending Amount', compute='_compute_pending_amount',store=True,tracking=True)
    
    procedure_discount_amount = fields.Float(string='Discount Amount',store=True,tracking=True)
    
    procedure_payable_amount = fields.Float(string='Payable Amount' , compute='_compute_payable_amount',store=True,tracking=True)      
    
    procedure_total_paid_amount = fields.Float(string='Paid Amount',compute='_compute_paid_amount',store=True,tracking=True)
    
    procedure_total_refunded_amount = fields.Float(string='Refunded Amount',store=True,tracking=True,compute='_compute_paid_amount')
    
    procedure_total_received_amount = fields.Float(string='Total Receivable Amount',store=True,tracking=True ,compute='_compute_received_amount')
    
    invoice_id = fields.Many2one('tcb.invoice', string='Invoice')
    # This is for invoice viewing Smart button 
    invoice_count = fields.Integer(string="Invoice Count",
        compute="_compute_invoice_count")
    

    @api.depends('procedure_payment_line_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env['tcb.invoice'].search_count([('procedure_id', '=', record.id)])

    def action_show_invoices(self):
        return {
            'name': 'Invoices',
            'view_mode': 'form,list',
            'res_model': 'tcb.invoice',
            'res_id': self.invoice_id.id,
            'domain': [('patient_id', '=', self.patient_id.id),('appointment_id', '=', self.id)],
            'context':{'create':False},
            'type': 'ir.actions.act_window',
        }
    ###############################################################
    
    
    # total paid amount and refunded amount
    @api.depends('procedure_payment_line_ids', 'procedure_payment_line_ids.payment_amount', 'procedure_payment_line_ids.state', 'procedure_payment_line_ids.payment_type')
    def _compute_paid_amount(self):
        for rec in self:
            rec.procedure_total_paid_amount = 0
            rec.procedure_total_refunded_amount = 0
            
            for payment in rec.procedure_payment_line_ids.filtered(lambda p : p.state =='posted'):
                if payment.payment_type == 'receive':
                    rec.procedure_total_paid_amount += payment.payment_amount 
                    
                elif payment.payment_type == 'send': #refund amount
                    rec.procedure_total_refunded_amount += payment.payment_amount
                
    
    @api.depends('procedure_line_ids', 'procedure_line_ids.procedure_price')
    def _compute_total_procedure_amount(self):
        for record in self:
            record.procedure_total_amount = sum(line.procedure_price for line in record.procedure_line_ids)

    # payable amount
    @api.depends('procedure_total_amount', 'procedure_discount_amount','procedure_payable_amount')
    def _compute_payable_amount(self):
        for rec in self:
            rec.procedure_payable_amount = rec.procedure_total_amount - rec.procedure_discount_amount 
            
            
    # pending amount
    @api.depends('procedure_payable_amount', 'procedure_total_paid_amount','procedure_amount_pending')
    def _compute_pending_amount(self):
        for rec in self:
            rec.procedure_amount_pending = rec.procedure_payable_amount - rec.procedure_total_paid_amount
    
    
    # total received amount
    @api.depends('procedure_payable_amount', 'procedure_total_paid_amount','procedure_total_refunded_amount','procedure_total_received_amount')
    def _compute_received_amount(self):
        for rec in self:
            rec.procedure_total_received_amount = rec.procedure_total_paid_amount - rec.procedure_total_refunded_amount
    # partner_id = fields.Many2one('res.partner', string='Partner', related = "patient_id.partner_id")
    
    @api.depends('procedure_payable_amount', 'procedure_total_paid_amount','procedure_total_refunded_amount','procedure_total_received_amount')
    def _compute_procedure_payment_status(self):
        for rec in self:
            if rec.procedure_total_paid_amount == 0:
                rec.procedure_payment_state = 'not_paid'
            elif rec.procedure_total_paid_amount < rec.procedure_payable_amount:
                rec.procedure_payment_state = 'partially_paid'
            elif rec.procedure_total_refunded_amount == rec.procedure_payable_amount:
                rec.procedure_payment_state = 'fully_reversed'
            elif rec.procedure_total_refunded_amount < rec.procedure_payable_amount and rec.procedure_total_refunded_amount > 0:
                rec.procedure_payment_state = 'partially_reversed'
            else:
                rec.procedure_payment_state = 'fully_paid'
                
                
    def action_cancel(self):
        # Cancel the procedure
        self.state = 'cancelled'
        # Find and cancel associated payment receipts
        payment_receipts = self.env['tcb.payment.receipt'].search([
            ('procedure_id', '=', self.id),
            ('state', '!=', 'cancelled')
        ])
        if payment_receipts:
            try:
                # Cancel payments
                payment_receipts.write({
                    'state': 'cancelled',
                })
                # Log a message in the chatter
                self.message_post(
                    body="Associated payments have been cancelled.",
                    subtype_xmlid="mail.mt_note"
                )
            except Exception as e:
                # Log any errors during payment cancellation
                self.message_post(
                    body=f"Error cancelling payments: {str(e)}",
                    subtype_xmlid="mail.mt_note"
                )
        return True
    
    def _domain_payment_lines(self):
        return [('state', '=', 'posted')]

    
    def action_refund_procedure(self):
        return {
            'name': 'Refund Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id' : self.patient_id.id,
                'default_appointment_id' : self.appointment_id.id,
                'default_invoice_id':self.invoice_id.id,
                'default_procedure_id': self.id,
                'default_payment_type': 'send',
                'default_payment_mode': 'cash',
                'default_payment_amount': self.procedure_total_paid_amount
            }
        }
        
    def action_confirm_with_payment(self):
        if not self.patient_id:
            raise ValidationError("Patient is required")
        if not self.procedure_line_ids:
            raise ValidationError("Procedure lines are required")
        self.state = 'running'
        self.ensure_one()
        
        # This part is for creating the invoice
        if self.invoice_id:
            invoice = self.invoice_id
        else:
            invoice_lines = []
            for proc_line in self.procedure_line_ids:
                line_vals = {
                    'product_id': proc_line.procedure_id.id,
                    'quantity': 1,
                    'price_unit': proc_line.procedure_price,
                }
                invoice_lines.append((0, 0, line_vals))
            
            invoice_vals = {
                'patient_id': self.patient_id.id,
                'invoice_line_ids': invoice_lines, 
                'appointment_id': self.appointment_id.id,
                'procedure_id': self.id,
                'state': 'posted',
                'physician_id': self.physician_id.id
            }
            
            invoice = self.env['tcb.invoice'].create(invoice_vals)
            self.invoice_id = invoice.id
            
            
        return {
            'name': 'Confirm Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id' : self.patient_id.id,
                'default_appointment_id' : self.appointment_id.id,
                'default_invoice_id': self.invoice_id.id,
                'default_procedure_id': self.id,
                'default_payment_type': 'receive',
                'default_payment_mode': 'cash',
                'default_payment_amount': self.procedure_amount_pending
            }
        }
        
    
    def action_confirm_without_payment(self):
        if not self.patient_id:
            raise ValidationError("Patient is required")
        if not self.procedure_line_ids:
            raise ValidationError("Procedure lines are required")
        self.state = 'running'
        # self.action_create_payment()
    
    def action_reset_to_draft(self):
        self.state = 'draft'
    

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('tcb.patient.procedure') or '/'
        return super(TcbPatientProcedure,self).create(vals)
    
    # Action Methods
    

    def action_done(self):
        self.state = 'done'

