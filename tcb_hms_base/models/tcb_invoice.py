from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import num2words

class TCBInvoice(models.Model):
    _name = "tcb.invoice"
    _description = "This is the custom Invoice model"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='draft', tracking=True)
    
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
        ('partially_reversed', 'Partially Reversed'),
        ('fully_reversed', 'Fully Reversed'),
    ], default='not_paid', string='Payment Status', compute='_compute_payment_status')
    
    name = fields.Char(
        string="Invoice Number",  copy=False, readonly=True,index=True,default=lambda self: _('New')
    )
    
    invoice_date = fields.Date(
        string="Invoice Date", 
        default=fields.Date.context_today)
    
    patient_id = fields.Many2one('hms.patient', string="Patient",tracking=True,required=True)
    
    amount_total = fields.Float(string="Total Amount", compute='_compute_total_amount', store=True,tracking=True)
        
    invoice_datetime = fields.Datetime(string="Invoice Date Time", default=fields.Datetime.now)
    
    patient_name = fields.Char(string="Patient", related="patient_id.patient_name", store=True , readonly=False,tracking=True)
    physician_id = fields.Many2one('hms.physician', string="Physician",tracking=True)
    # Invoice Lines
    invoice_line_ids = fields.One2many('tcb.invoice.line', 'invoice_id', string="Invoice Lines")
    payment_line_ids = fields.One2many('tcb.payment.receipt', 'invoice_id', string="Payment Lines")
    appointment_id = fields.Many2one('hms.appointment', string="Appointment")
    
    amount_pending = fields.Float(string='Pending Amount', compute='_compute_pending_amount',store=True,tracking=True)
    
    discount_amount = fields.Float(string='Discount Amount',store=True,tracking=True)
    
    payable_amount = fields.Float(string='Payable Amount' , compute='_compute_payable_amount',store=True,tracking=True)      
    
    total_paid_amount = fields.Float(string='Paid Amount',compute='_compute_paid_amount',store=True,tracking=True)
    
    total_refunded_amount = fields.Float(string='Refunded Amount',store=True,tracking=True,compute='_compute_paid_amount')
    
    total_received_amount = fields.Float(string='Total Receivable Amount',store=True,tracking=True ,compute='_compute_received_amount')
    
    invoice_id = fields.Many2one('tcb.invoice', string='Invoice')
    
    amount_total_words = fields.Char(string="Amount in Words", compute="_compute_amount_words", store=True) 
    
    currency_id = fields.Many2one(
        'res.currency', 
        string="Currency", 
        default=lambda self: self.env.company.currency_id
    )
        # total paid amount and refunded amount
    @api.depends('payment_line_ids', 'payment_line_ids.payment_amount', 'payment_line_ids.state', 'payment_line_ids.payment_type')
    def _compute_paid_amount(self):
        for rec in self:
            rec.total_paid_amount = 0
            rec.total_refunded_amount = 0
            
            for payment in rec.payment_line_ids.filtered(lambda p : p.state =='posted'):
                if payment.payment_type == 'receive':
                    rec.total_paid_amount += payment.payment_amount 
                    
                elif payment.payment_type == 'send': #refund amount
                    rec.total_refunded_amount += payment.payment_amount
                
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # payable amount
    @api.depends('amount_total', 'discount_amount','payable_amount')
    def _compute_payable_amount(self):
        for rec in self:
            rec.payable_amount = rec.amount_total - rec.discount_amount 
            
            
    # pending amount
    @api.depends('payable_amount', 'total_paid_amount','amount_pending')
    def _compute_pending_amount(self):
        for rec in self:
            rec.amount_pending = rec.payable_amount - rec.total_paid_amount
    
    
    # total received amount
    @api.depends('payable_amount', 'total_paid_amount','total_refunded_amount','total_received_amount')
    def _compute_received_amount(self):
        for rec in self:
            rec.total_received_amount = rec.total_paid_amount - rec.total_refunded_amount
    @api.depends('payable_amount', 'total_paid_amount','total_refunded_amount','total_received_amount')
    def _compute_payment_status(self):
        for rec in self:
            if rec.total_paid_amount == 0:
                rec.payment_state = 'not_paid'
            elif rec.total_paid_amount < rec.payable_amount:
                rec.payment_state = 'partially_paid'
            elif rec.total_refunded_amount == rec.payable_amount:
                rec.payment_state = 'fully_reversed'
            elif rec.total_refunded_amount < rec.payable_amount and rec.total_refunded_amount > 0:
                rec.payment_state = 'partially_reversed'
            else:
                rec.payment_state = 'fully_paid'
    # Compute total amount
    @api.depends('invoice_line_ids.subtotal')
    def _compute_total_amount(self):
        for invoice in self:
            invoice.amount_total = sum(line.subtotal for line in invoice.invoice_line_ids)
    
    
    # Compute amount in words using Indian convention
    @api.depends('amount_total')
    def _compute_amount_words(self):
        for rec in self:
            rec.amount_total_words = rec._amount_to_indian_words(rec.amount_total)

    def _amount_to_indian_words(self, amount):
        """
        Convert a number to words in Indian numbering format (Lakhs and Crores).
        """
        if self.currency_id:
            currency = self.currency_id.name  # Get currency name
        else:
            currency = "Rupees"

        # Convert amount to integer and decimal parts
        amount_integer = int(amount)
        amount_decimal = int(round((amount - amount_integer) * 100))  # Convert fraction to paise

        # Convert integer part using Indian numbering system
        amount_words = self._convert_to_indian_format(amount_integer)

        if amount_decimal > 0:
            amount_words += f" and {num2words.num2words(amount_decimal)} paise"
        
        return f"{amount_words.capitalize()} {currency} Only"

    def _convert_to_indian_format(self, num):
        """
        Convert a number to words using the Indian number system (Lakhs and Crores).
        """
        words = []
        crores = num // 10000000
        num %= 10000000
        lakhs = num // 100000
        num %= 100000
        thousands = num // 1000
        num %= 1000
        hundreds = num // 100
        num %= 100
        tens_units = num

        if crores:
            words.append(num2words.num2words(crores) + " Crore")
        if lakhs:
            words.append(num2words.num2words(lakhs) + " Lakh")
        if thousands:
            words.append(num2words.num2words(thousands) + " Thousand")
        if hundreds:
            words.append(num2words.num2words(hundreds) + " Hundred")
        if tens_units:
            if words:
                words.append("and " + num2words.num2words(tens_units))
            else:
                words.append(num2words.num2words(tens_units))

        return " ".join(words)
    
    
    # Generate invoice number
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('tcb.invoice') or _('New')
        return super(TCBInvoice, self).create(vals)
    
    # Action to confirm invoice
    def action_confirm(self):
        if not self.invoice_line_ids:
            raise UserError("Invoice must have at least one invoice line.")
        self.write({
            'state': 'posted',
            'invoice_date': fields.Date.today()
        })
    def action_register_payment(self):
        self.state = 'posted'
        self.ensure_one()
        return {
            'name': 'Confirm Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id':self.patient_id.id,
                'default_invoice_id':self.id,
                'default_appointment_id': self.appointment_id.id,
                'default_payment_type': 'receive',
                'default_payment_mode': 'cash',
                'default_payment_amount': self.amount_pending
            }
        }
    
    def action_refund_payment(self):
        return {
            'name': 'Refund Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id':self.patient_id.id,
                'default_invoice_id':self.id,
                'default_appointment_id': self.appointment_id.id,
                'default_payment_type': 'send',
                'default_payment_mode': 'cash',
                'default_payment_amount': self.total_paid_amount
            }
        }
        
        
    def action_cancel(self):
        # Cancel the appointment
        self.write({
            'state': 'cancelled'
        })
        # Find and cancel associated payment receipts
        payment_receipts = self.env['tcb.payment.receipt'].search([
            ('invoice_id', '=', self.id),
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
    
    def action_draft(self):
        self.write({
            'state': 'draft'
        })

    # Invoice Line Model
class TCBInvoiceLine(models.Model):
    _name = "tcb.invoice.line"
    _description = "Invoice Line"
    
    invoice_id = fields.Many2one(
        'tcb.invoice', 
        string="Invoice", 
        required=True, 
        ondelete='cascade'
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string="Currency", 
        default=lambda self: self.env.company.currency_id
    )
    
    product_id = fields.Many2one(
        'product.template',
        string="Product", 
    )
    
    quantity = fields.Float(
        string="Quantity", 
        default=1.0, 
        required=True
    )
    
    price_unit = fields.Float(
        string="Unit Price", 
        # related="product_id.list_price", 
        store=True
    )
    
    subtotal = fields.Float(
        string="Subtotal", 
        compute='_compute_subtotal', 
        store=True)
    
    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
            
