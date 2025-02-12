
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class AppointmentPurpose(models.Model):
    _name = 'appointment.purpose'
    _description = "Appointment Purpose"

    name = fields.Char(string='Appointment Purpose', required=True, translate=True)


class AppointmentCabin(models.Model):
    _name = 'appointment.cabin'
    _description = "Appointment Cabin"

    name = fields.Char(string='Appointment Cabin', required=True, translate=True)


class TcbCancelReason(models.Model):
    _name = 'tcb.cancel.reason'
    _description = "Cancel Reason"

    name = fields.Char('Reason')

    
class Appointment(models.Model):
    _name = 'hms.appointment'
    _description = "Appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    
    name = fields.Char(string='Appointment Id', readonly=True, copy=False, tracking=True)
    patient_id = fields.Many2one('hms.patient', ondelete='restrict', string='Patient',
        required=True, index=True, help='Patient Name', tracking=True)
    department_id = fields.Many2one('tcb.department', ondelete='restrict', string='Department', tracking=True , default=lambda self: self.env['tcb.department'].search([('name', '=', 'Ophthalmology')], limit=1))
    physician_id = fields.Many2one('hms.physician', ondelete='restrict', string='Physician',related='patient_id.primary_physician_id',readonly=False,
        index=True, help='Physician\'s Name', tracking=True)
    
    care_of = fields.Char(string='Care of', tracking=True, related = "patient_id.care_of")
    relation = fields.Many2one('tcb.family.relation', string='Relation', tracking=True, related = "patient_id.relation")
    date_of_birth = fields.Date(string='Date of Birth', tracking=True, related = "patient_id.date_of_birth")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender', related = "patient_id.gender")
    age = fields.Char(string='Age', related = "patient_id.age")
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ], string='Blood Group', related = "patient_id.blood_group")
    mobile = fields.Char(string='Mobile', tracking=True, related = "patient_id.mobile")
    phone = fields.Char(string='Phone', tracking=True, related = "patient_id.phone")
    email = fields.Char(string='Email', tracking=True, related = "patient_id.email")
    city = fields.Char(string='City', tracking=True, related = "patient_id.city")
    street = fields.Char(string='Address line1', tracking=True, related = "patient_id.street")
    street2 = fields.Char(string='Address line2', tracking=True, related = "patient_id.street2")
    state_id = fields.Many2one('res.country.state', string='State', tracking=True, related = "patient_id.state_id" , domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', tracking=True, related = "patient_id.country_id")
    zip = fields.Char(string='Zip', tracking=True, related = "patient_id.zip")
    
    aadhar = fields.Char(string='Aadhar', tracking=True, related = "patient_id.aadhar")
    pan = fields.Char(string='PAN', tracking=True, related = "patient_id.pan")
    occupation = fields.Char(string='Occupation', tracking=True, related = "patient_id.occupation")
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ], string='Marital Status', default="single", tracking=True, related = "patient_id.marital_status")
    education = fields.Char("Patient Education", related = "patient_id.education")
    occupation = fields.Char("Occupation", related = "patient_id.occupation")   
    
    referred_by = fields.Selection([('self', 'Self'), ('other', 'Other')], string='Referred By', default='self')
    
    other_physician_id = fields.Many2one('other.physician', string='Referring Physician')
    
    
    duration = fields.Float(string='Duration (Minutes)', default=15.0)
    notes = fields.Text(string='Notes')
    datetime = fields.Datetime(string='Date', default=fields.Datetime.now, tracking=True)
    date = fields.Date(string='Date', default=fields.Date.today, tracking=True)
    
    differ_charges_id = fields.Many2one('physician.differ_charges', string='Different Charges' , domain="[('physician_id', '=', physician_id)]")
    # company = fields.Char("Company")
    # company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    validity_till = fields.Date(string="Follow up")
    valid_till = fields.Integer(string="Valid Till")

    def get_valid_till_date(self):
        till_date = ""
        if self.date and self.valid_till:
            valid_till_date = self.date + timedelta(days=self.valid_till+1)
            till_date = valid_till_date.strftime('%d/%m/%Y')
        return till_date
    
    # Payment fields
    appointment_payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
        ('partially_reversed', 'Partially Reversed'),
        ('fully_reversed', 'Fully Reversed'),
    ], default='not_paid', string='Payment Status', compute='_compute_payment_status')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                print("if dob function -------")
                record.age = (datetime.now().date() - record.date_of_birth).days // 365
            else:
                record.age = 0
                
    # ,domain=lambda self: self._domain_payment_lines()
    payment_line_ids = fields.One2many('tcb.payment.receipt', 'appointment_id', string='Payment Lines')
    
    amount_total = fields.Float(string='Total Amount',store=True,tracking=True , related = 'differ_charges_id.charges')
    
    amount_pending = fields.Float(string='Pending Amount', compute='_compute_pending_amount',store=True,tracking=True)
    
    discount_amount = fields.Float(string='Discount Amount',store=True,tracking=True)
    
    payable_amount = fields.Float(string='Payable Amount' , compute='_compute_payable_amount',store=True,tracking=True)      
    
    total_paid_amount = fields.Float(string='Paid Amount',compute='_compute_paid_amount',store=True,tracking=True)
    
    total_refunded_amount = fields.Float(string='Refunded Amount',store=True,tracking=True,compute='_compute_paid_amount')
    
    total_received_amount = fields.Float(string='Total Receivable Amount',store=True,tracking=True ,compute='_compute_received_amount')
    
    invoice_id = fields.Many2one('tcb.invoice', string='Invoice')
    invoice_count = fields.Integer(string="Invoice Count",
        compute="_compute_invoice_count")
    

    @api.depends('payment_line_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env['tcb.invoice'].search_count([('appointment_id', '=', record.id)])

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
    # partner_id = fields.Many2one('res.partner', string='Partner', related = "patient_id.partner_id")
    
    @api.depends('payable_amount', 'total_paid_amount','total_refunded_amount','total_received_amount')
    def _compute_payment_status(self):
        for rec in self:
            if rec.total_paid_amount == 0:
                rec.appointment_payment_state = 'not_paid'
            elif rec.total_paid_amount < rec.payable_amount:
                rec.appointment_payment_state = 'partially_paid'
            elif rec.total_refunded_amount == rec.payable_amount:
                rec.appointment_payment_state = 'fully_reversed'
            elif rec.total_refunded_amount < rec.payable_amount and rec.total_refunded_amount > 0:
                rec.appointment_payment_state = 'partially_reversed'
            else:
                rec.appointment_payment_state = 'fully_paid'
                
                
    def action_cancel(self):
        # Cancel the appointment
        self.state = 'cancelled'
        # Find and cancel associated payment receipts
        payment_receipts = self.env['tcb.payment.receipt'].search([
            ('appointment_id', '=', self.id),
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
    
    
    def action_refund_appointment(self):
        return {
            'name': 'Refund Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_appointment_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_invoice_id':self.invoice_id.id,
                'default_payment_type': 'send',
                'default_payment_mode': 'cash',
                'default_payment_amount': self.total_paid_amount
            }
        }
        
        
    def action_confirm_with_payment(self):
        self.state = 'confirmed'
        self.ensure_one()
        # Here we can first make the invoice then we can easily move the payment to the invoice
        
        # Create invoice
        
        if self.invoice_id:
            invoice = self.invoice_id
        else:
            invoice = self.env['tcb.invoice'].create({
                'patient_id': self.patient_id.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': self.env['product.product'].search([('name', '=', 'Consultation Service')], limit=1).id,
                    'quantity': 1,
                    'price_unit':self.physician_id.differ_charges_ids.charges,})],
                'appointment_id': self.id,
                'state':'posted',
                'physician_id': self.physician_id.id
                })
            print("else - ----",invoice)
            self.invoice_id = invoice.id
            
            
        return {
            'name': 'Confirm Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_appointment_id':self.id,
                'default_invoice_id': invoice.id,
                'default_appointment_id': self.id,
                'default_payment_type': 'receive',
                'default_payment_mode': 'cash',
                'default_payment_amount': self.amount_pending
            }
        }
        
    # def action_confirm_with_payment(self):
    #     self.state = 'confirmed'
    #     self.ensure_one()
    #     # Create invoice
    #     invoice = self.env['tcb.invoice'].create({
    #         'patient_id': self.patient_id.id,
    #         'invoice_line_ids': [(0, 0, {
    #             'product_id': self.env['product.template'].search([('name', '=', 'Consultation Service')], limit=1).id,
    #             'quantity': 1,
    #             'price_unit': self.amount_total,
    #         })],
    #     })
    #     # Create payment
    #     payment = self.env['tcb.payment.receipt'].create({
    #         'appointment_id': self.id,
    #         'patient_id': self.patient_id.id,
    #         'physician_id': self.physician_id.id,
    #         'payment_amount': self.amount_total,
    #         'payment_date': fields.Date.today(),
    #         'payment_mode': 'cash',
    #         'payment_type': 'receive',
    #         'invoice_id': invoice.id,
    #     })
    #     # Update invoice payment status
    #     invoice.payment_state = 'paid'
    #     # Update appointment payment status
    #     self.appointment_payment_state = 'fully_paid'
        
    def action_show_invoices(self):
        return {
            'name': 'Invoices',
            'view_mode': 'form,list',
            'res_model': 'tcb.invoice',
            'res_id': self.invoice_id.id,  # Specific invoice ID
            'domain': [('patient_id', '=', self.patient_id.id),('appointment_id', '=', self.id)],
            'context':{'create':False},
            'type': 'ir.actions.act_window',
        }
        
    # def action_confirm_with_payment(self):
    #     self.state = 'confirmed'
    #     self.ensure_one()
    #     payment_receipt = self.env['tcb.payment.receipt'].create({
    #         'appointment_id': self.id,
    #         'patient_id': self.patient_id.id,
    #         'physician_id': self.physician_id.id,
    #         'payment_amount': self.amount_pending,
    #         'payment_date': fields.Date.today(),
    #         'payment_mode': 'cash',
    #         'payment_type': 'receive',
    #     })

    #     return {
    #         'name': 'Payment Receipt',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'payment.wizard',
    #         'view_mode': 'form',
    #         'res_id': payment_receipt.id,
    #         'target': 'current',
    #     }

    # def action_create_payment(self):
    #     """
    #     Open payment wizard for the current appointment
    #     """
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'payment.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'default_appointment_id': self.id,
    #             'default_patient_id': self.patient_id.id,
    #         }
    #     }
    
    def action_confirm_without_payment(self):
        self.state = 'confirmed'
        # self.action_create_payment()
    
    # def action_cancel(self):
    #     self.state = 'cancelled'
    
    def action_reset_to_draft(self):
        self.state = 'draft'
    
    def action_create_invoice(self):
        pass
        # if self.invoice_id:
        #     raise UserError(_("Invoice already created for this appointment."))
        
        # invoice_vals = {
        #     'partner_id': self.patient_id.partner_id.id,
        #     'move_type': 'out_invoice',
        #     'invoice_line_ids': [(0, 0, {
        #         'name': f"Appointment - {self.name}",
        #         'quantity': 1,
        #         'price_unit': self.amount_total,
        #     })],
        # }
        # invoice = self.env['account.move'].create(invoice_vals)
        # self.invoice_id = invoice.id
        # return {
        #     'name': _('Invoice'),
        #     'view_mode': 'form',
        #     'res_model': 'account.move',
        #     'res_id': invoice.id,
        #     'type': 'ir.actions.act_window',
        # }
        
    # def action_refer_opthmatology(self):
    #     return {
    #         'name': _('Refer to Ophthalmology'),
    #         'view_mode': 'form',
    #         'res_model': 'hms.opthmology',
    #         'type': 'ir.actions.act_window',
    #     }
        
        
    @api.model
    def create(self, values):
        if not values.get('name'):
            sequence = self.env['ir.sequence'].next_by_code('hms.appointment') or '/'
            today = datetime.now().strftime("%d/%m/%Y")
            values['name'] = f"AP-{today}-{sequence}"

        vals = {}

            
        if 'care_of' in values and not self.patient_id.care_of:
            vals['care_of'] = values['care_of']
        if 'relation' in values and not self.patient_id.relation:
            vals['relation'] = values['relation']
        if 'phone' in values and not self.patient_id.phone:
            vals['phone'] = values['phone']
        if 'mobile' in values and not self.patient_id.mobile:
            vals['mobile'] = values['mobile']
        if 'email' in values and not self.patient_id.email:
            vals['email'] = values['email']
        if 'street' in values and not self.patient_id.street:
            vals['street'] = values['street']
        if 'country_id' in values and not self.patient_id.country_id:
            vals['country_id'] = values['country_id']
        if 'state_id' in values and not self.patient_id.state_id:
            vals['state_id'] = values['state_id']
        if 'city' in values and not self.patient_id.city:
            vals['city'] = values['city']
        if 'zip' in values and not self.patient_id.zip:
            vals['zip'] = values['zip']
        if 'gender' in values and not self.patient_id.gender:
            vals['gender'] = values['gender']
        if 'age' in values and not self.patient_id.age:
            vals['age'] = values['age']
        if 'marital_status' in values and not self.patient_id.marital_status:
            vals['marital_status'] = values['marital_status']
        if 'blood_group' in values and not self.patient_id.blood_group:
            vals['blood_group'] = values['blood_group']
        if 'occupation' in values and not self.patient_id.occupation:
            vals['occupation'] = values['occupation']
        if 'religion' in values and not self.patient_id.religion:
            vals['religion'] = values['religion']
        if 'date_of_birth' in values and not self.patient_id.date_of_birth:
            vals['date_of_birth'] = values['date_of_birth']
        if 'aadhar' in values and not self.patient_id.aadhar:
            vals['aadhar'] = values['aadhar']
        if 'pan' in values and not self.patient_id.pan:
            vals['pan'] = values['pan']
            
        if vals:
            patient_id = self.env['hms.patient'].browse(values['patient_id'])
            patient_id.write(vals)
        return super(Appointment, self).create(values)
    
    
    def write(self, values):
        appointment = super(Appointment, self).write(values)
        vals = {}
        if 'care_of' in values and not self.patient_id.care_of:
            vals['care_of'] = values['care_of']
        if 'relation' in values and not self.patient_id.relation:
            vals['relation'] = values['relation']
        if 'phone' in values and not self.patient_id.phone:
            vals['phone'] = values['phone']
        if 'mobile' in values and not self.patient_id.mobile:
            vals['mobile'] = values['mobile']
        if 'email' in values and not self.patient_id.email:
            vals['email'] = values['email']
        if 'street' in values and not self.patient_id.street:
            vals['street'] = values['street']
        if 'country_id' in values and not self.patient_id.country_id:
            vals['country_id'] = values['country_id']
        if 'state_id' in values and not self.patient_id.state_id:
            vals['state_id'] = values['state_id']
        if 'city' in values and not self.patient_id.city:
            vals['city'] = values['city']
        if 'zip' in values and not self.patient_id.zip:
            vals['zip'] = values['zip']
        if 'gender' in values and not self.patient_id.gender:
            vals['gender'] = values['gender']
        if 'age' in values and not self.patient_id.age:
            vals['age'] = values['age']
        if 'marital_status' in values and not self.patient_id.marital_status:
            vals['marital_status'] = values['marital_status']
        if 'blood_group' in values and not self.patient_id.blood_group:
            vals['blood_group'] = values['blood_group']
        if 'occupation' in values and not self.patient_id.occupation:
            vals['occupation'] = values['occupation']
        if 'religion' in values and not self.patient_id.religion:
            vals['religion'] = values['religion']
        if 'date_of_birth' in values and not self.patient_id.date_of_birth:
            vals['date_of_birth'] = values['date_of_birth']
        if 'aadhar' in values and not self.patient_id.aadhar:
            vals['aadhar'] = values['aadhar']
        if 'pan' in values and not self.patient_id.pan:
            vals['pan'] = values['pan']
        if vals:
            self.patient_id.write(vals)
        return appointment
    
    
                
    

    def action_report_hms_appointment(self):
        return self.env.ref('tcb_hms_base.action_report_hms_appointment').report_action(self)
    
