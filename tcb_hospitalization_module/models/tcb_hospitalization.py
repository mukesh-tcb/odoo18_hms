from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
from datetime import date,datetime,timedelta


class TCBHospitalization(models.Model):
    _name = "tcb.hospitalization"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "This is the custom Hospitalization model"
    
    
    name = fields.Char(string="Hospitalization Number" , copy=False,tracking=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hms.patient', string="Patient" ,tracking=True)
    admission_date = fields.Datetime(string="Admission Date",tracking=True,default=fields.Datetime.today())
    discharge_date = fields.Datetime(string="Discharge Date",tracking=True)
    physician_id = fields.Many2one('hms.physician', string="Primary Consultant",tracking=True,related='patient_id.primary_physician_id',readonly=False)
    attending_physician_ids = fields.Many2many('hms.physician', string="Attending Physicians",tracking=True)
    
    procedure_type_id = fields.Many2one('tcb.procedure.type', string="Procedure Type",tracking=True)    
    patient_category_id = fields.Many2one('tcb.patient.category', string="Patient Category",tracking=True)
    gender = fields.Selection(selection=[('male', 'Male'),
                                        ('female', 'Female'),
                                        ('other', 'Other')], string="Gender",tracking=True,related='patient_id.gender',readonly=False)
    
    date_of_birth = fields.Date(string="Date of Birth",tracking=True,related='patient_id.date_of_birth',readonly=False)
    age = fields.Char(string="Age",tracking=True,related='patient_id.age',readonly=False)
    phone = fields.Char(string="Phone",tracking=True,related='patient_id.phone',readonly=False)
    
    #Onchange of date of birth the age should be calculated
    @api.onchange('date_of_birth')
    def _onchange_date_of_birth(self):
        if self.date_of_birth:
            self.age = (datetime.now().date() - self.date_of_birth).days // 365
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('hospitalized','Hospitalized'), 
        ('discharge_requested', 'Discharge Requested'),
        ('discharged', 'Discharged'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),],
            string='Status', default='draft', tracking=True)
    
    street = fields.Char(tracking=True,related='patient_id.street',readonly=False)
    street2 = fields.Char(tracking=True,related='patient_id.street2',readonly=False)
    zip = fields.Char(tracking=True,related='patient_id.zip',readonly=False)
    city = fields.Char(tracking=True,related='patient_id.city',readonly=False)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict' , domain="[('country_id', '=', country_id)]",tracking=True,related='patient_id.state_id',readonly=False)
    # country_id = fields.Many2one('res.country', string='Country', ondelete='restrict' , default=91)
    country_id = fields.Many2one('res.country', string="Country", default=lambda self: self.env['res.country'].search([('code', '=', 'IN')], limit=1)) 

    mobile = fields.Char(string="Mobile",tracking=True,related='patient_id.mobile',readonly=False)
    email = fields.Char(string="Email",tracking=True,related='patient_id.email',readonly=False)
    aadhar = fields.Char(string="Aadhar Number",tracking=True,related='patient_id.aadhar',readonly=False)
    pan = fields.Char(string="PAN Number",tracking=True,related='patient_id.pan',readonly=False)
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ], string="Blood Group",tracking=True,related='patient_id.blood_group',readonly=False)
    patient_relative_name = fields.Char(string="Patient Relative Name",tracking=True)
    patient_relative_relation = fields.Many2one('tcb.family.relation', string="Patient Relative Relation",tracking=True)
    patient_relative_number = fields.Char(string="Patient Relative Number",tracking=True)
    
    referred_by = fields.Selection([
        ('self', 'Self'),
        ('other', 'Other'),
    ],default = 'self',tracking=True)
    
    doctor_notes = fields.Html(string="Doctor Notes",tracking=True)
    
    admission_type = fields.Selection([
        ('routine','Routine'),
        ('elective','Elective'),
        ('urgent','Urgent'),
        ('emergency','Emergency')], string='Admission type', default='routine',tracking=True)
    
    hms_services_line_ids = fields.One2many('tcb.hms.services.lines', 'hospitalization_id', string="Services",tracking=True)
    
    ward_id = fields.Many2one('hospital.ward', ondelete="restrict", string='Ward/Room',tracking=True)
    bed_id = fields.Many2one('hospital.bed', ondelete="restrict", string='Bed No.',tracking=True)
    accommodation_history_ids = fields.One2many("patient.accommodation.history", "hospitalization_id", 
        string="Accommodation History", copy=False,tracking=True)   
    
    ready_for_payment_bool = fields.Boolean(string="Ready for Payment",tracking=True)
    # Payment fields
    ipd_payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
        ('partially_reversed', 'Partially Reversed'),
        ('fully_reversed', 'Fully Reversed'),
    ], default='not_paid', string='Payment Status', compute='_compute_ipd_payment_status')
    
    total_ipd_amount = fields.Float(string="Total Hospitalization Amount",compute='_compute_total_hospitalization_amount')
    
    ipd_payment_line_ids = fields.One2many('tcb.payment.receipt', 'hospitalization_id', string='Payment Lines')
        
    ipd_amount_pending = fields.Float(string='Pending Amount', compute='_compute_ipd_pending_amount',store=True,tracking=True)
    
    ipd_discount_amount = fields.Float(string='Discount Amount',store=True,tracking=True)
    
    ipd_payable_amount = fields.Float(string='Payable Amount' , compute='_compute_ipd_payable_amount',store=True,tracking=True)      
    
    ipd_total_paid_amount = fields.Float(string='Paid Amount',compute='_compute_ipd_paid_amount',store=True,tracking=True)
    
    ipd_total_refunded_amount = fields.Float(string='Refunded Amount',store=True,tracking=True,compute='_compute_ipd_paid_amount')
    
    ipd_total_received_amount = fields.Float(string='Total Receivable Amount',store=True,tracking=True ,compute='_compute_ipd_received_amount')
    
    invoice_id = fields.Many2one('tcb.invoice', string='Invoice', copy=False,tracking=True)
    
    # This is for invoice viewing Smart button 
    invoice_count = fields.Integer(string="Invoice Count",
        compute="_compute_invoice_count")
    

    @api.depends('ipd_payment_line_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env['tcb.invoice'].search_count([('hospitalization_id', '=', record.id)])

    def action_show_invoices(self):
        return {
            'name': 'Invoices',
            'view_mode': 'form,list',
            'res_model': 'tcb.invoice',
            'res_id': self.invoice_id.id,
            'domain': [('patient_id', '=', self.patient_id.id),('hospitalization_id', '=', self.id)],
            'context':{'create':False},
            'type': 'ir.actions.act_window',
        }
    ###############################################################
    
    #Discharge Summary fields - 
    
    free_follow_up=fields.Date("Free Follow Up Upto")
    icd_code= fields.Char("ICD CODE")
    admission_reason=fields.Text('REASON FOR ADMISSION')
    past_history= fields.Text("PAST HISTORY AND ALLERGIES")
    diagnosis_right= fields.Text("RIGHT EYE")
    diagnosis_left= fields.Text("LEFT EYE")
    procedure_performed=fields.Text("PROCEDURE PERFORMED")
    investigation_result=fields.Text("INVESTIGATION RESULT FINDINGS")
    dos= fields.Date("DATE OF SURGERY")
    date_of_investigation = fields.Date("DATE OF INVESTIGATION")
    doc_notes=fields.Html("DOCTOR'S NOTES")

    diagnosis_details_re = fields.Many2one('tcb.diagnosis.details', string="Diagnosis Details RE")
    diagnosis_details_le = fields.Many2one('tcb.diagnosis.details', string="Diagnosis Details LE")

    prescription_lines_ids = fields.One2many('discharge.prescription.lines','hospitalization_id',string='Prescription Lines(Hospitalization)')

    # prescription_line_ids = fields.One2many('prescription.line', 'hospitalization_id', string="P")
    # new_line_ids = fields.One2many('prescription.line', 'hospitalization_id')

    follow_up_line_ids = fields.One2many('followup.line', 'hospitalization_id', string="Follow Up Lines")

    hbsag = fields.Selection([('reactive','Reactive'),('non_reactive','Non-Reactive')],string="HBsAg") 
    hiv = fields.Selection([('reactive','Reactive'),('non_reactive','Non-Reactive')],string="HIV")
    hcv = fields.Selection([('reactive','Reactive'),('non_reactive','Non-Reactive')],string="HCV")
    hb = fields.Char("HB")
    plt = fields.Char("PLT")
    bsr = fields.Char("BSR")
    sugar = fields.Char("SUGAR")
    albumin = fields.Char("ALBUMIN")
    pus_cells = fields.Char("PUS CELLS")
    @api.depends('ipd_payment_line_ids', 'ipd_payment_line_ids.payment_amount', 'ipd_payment_line_ids.state', 'ipd_payment_line_ids.payment_type')
    def _compute_ipd_paid_amount(self):
        for rec in self:
            rec.ipd_total_paid_amount = 0
            rec.ipd_total_refunded_amount = 0
            
            for payment in rec.ipd_payment_line_ids.filtered(lambda p : p.state =='posted'):
                if payment.payment_type == 'receive':
                    rec.ipd_total_paid_amount += payment.payment_amount 
                    
                elif payment.payment_type == 'send': #refund amount
                    rec.ipd_total_refunded_amount += payment.payment_amount
                
    
    # payable amount
    @api.depends('total_ipd_amount', 'ipd_discount_amount','ipd_payable_amount')
    def _compute_ipd_payable_amount(self):
        for rec in self:
            rec.ipd_payable_amount = rec.total_ipd_amount - rec.ipd_discount_amount 
            
            
    # pending amount
    @api.depends('ipd_payable_amount', 'ipd_total_paid_amount','ipd_amount_pending')
    def _compute_ipd_pending_amount(self):
        for rec in self:
            rec.ipd_amount_pending = rec.ipd_payable_amount - rec.ipd_total_paid_amount
    
    
    # total received amount
    @api.depends('ipd_payable_amount', 'ipd_total_paid_amount','ipd_total_refunded_amount','ipd_total_received_amount')
    def _compute_ipd_received_amount(self):
        for rec in self:
            rec.ipd_total_received_amount = rec.ipd_total_paid_amount - rec.ipd_total_refunded_amount
    # partner_id = fields.Many2one('res.partner', string='Partner', related = "patient_id.partner_id")
    
    @api.depends('ipd_payable_amount', 'ipd_total_paid_amount','ipd_total_refunded_amount','ipd_total_received_amount')
    def _compute_ipd_payment_status(self):
        for rec in self:
            if rec.ipd_total_paid_amount == 0:
                rec.ipd_payment_state = 'not_paid'
            elif rec.ipd_total_paid_amount < rec.ipd_payable_amount:
                rec.ipd_payment_state = 'partially_paid'
            elif rec.ipd_total_refunded_amount == rec.ipd_payable_amount:
                rec.ipd_payment_state = 'fully_reversed'
            elif rec.ipd_total_refunded_amount < rec.ipd_payable_amount and rec.ipd_total_refunded_amount > 0:
                rec.ipd_payment_state = 'partially_reversed'
            else:
                rec.ipd_payment_state = 'fully_paid'
                
    
    @api.depends('hms_services_line_ids')
    def _compute_total_hospitalization_amount(self):
        for rec in self:
            rec.total_ipd_amount = sum(rec.hms_services_line_ids.filtered(lambda obj: obj.add_in_bill).mapped('price'))            
            

    @api.constrains('hms_services_line_ids')
    def constraints_for_not_saving_more_line_than_max_limit(self):
        for rec in self.hms_services_line_ids:
            service_ids = self.hms_services_line_ids.filtered(
                lambda obj: obj.service_id.id == rec.service_id.id)
            if service_ids and len(service_ids) > rec.max_limit:
                raise ValidationError("%s exceeds the max limit!" % rec.service_id.name)
            
            
    def action_cancel_hospitalization(self):
        self.state = 'cancel'
        
        
    def action_confirm_hospitalization(self):
        self.state = 'confirmed'
        
        
        
    def action_hospitalize(self):
        if self.patient_id.hospitalize:
            raise ValidationError("Patient already hospitalized")
        else:
            acc_history = self.env['patient.accommodation.history']
            if self.ward_id and self.bed_id:
                for rec in self:
                    acc_history.sudo().create({
                        'hospitalization_id': rec.id,
                        'patient_id' : rec.patient_id.id,
                        'ward_id' : rec.ward_id.id,
                        'bed_id' : rec.bed_id.id,
                        'start_date': fields.Datetime.now(),
                        'end_date': False
                    })
                    rec.state = 'hospitalized'
                    rec.bed_id.patient_id = self.patient_id.id
                    rec.bed_id.sudo().write({'state' : 'occupied'})
                    rec.patient_id.hospitalize = True
                    rec.admission_date = fields.Datetime.now()
            else:
                raise ValidationError("Ward and Bed are required to hospitalize the patient.")
            
    
    @api.model
    def create(self, values):
        if not values.get('name') or values.get('name') == _('New'):
            sequence = self.env['ir.sequence'].next_by_code('tcb.hospitalization') or 'New'
            today = datetime.now()
            
            if today.month < 4:
                fy = f"{str(today.year-1)[2:]}-{str(today.year)[2:]}"
            else:
                fy = f"{str(today.year)[2:]}-{str(today.year+1)[2:]}"
            
            values['name'] = f"IPD/{fy}/{sequence.zfill(5)}"
        
        vals={}
        
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
        if 'blood_group' in values and not self.patient_id.blood_group:
            vals['blood_group'] = values['blood_group']
        if 'date_of_birth' in values and not self.patient_id.date_of_birth:
            vals['date_of_birth'] = values['date_of_birth']
        if 'aadhar' in values and not self.patient_id.aadhar:
            vals['aadhar'] = values['aadhar']
        if 'pan' in values and not self.patient_id.pan:
            vals['pan'] = values['pan']
        if vals:
            patient_id = self.env['hms.patient'].browse(values['patient_id'])
            patient_id.write(vals)
        return super(TCBHospitalization, self).create(values)
            
            
            
    def write(self, values):
        hospitalization = super(TCBHospitalization, self).write(values)
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
        if 'blood_group' in values and not self.patient_id.blood_group:
            vals['blood_group'] = values['blood_group']
        if 'date_of_birth' in values and not self.patient_id.date_of_birth:
            vals['date_of_birth'] = values['date_of_birth']
        if 'aadhar' in values and not self.patient_id.aadhar:
            vals['aadhar'] = values['aadhar']
        if 'pan' in values and not self.patient_id.pan:
            vals['pan'] = values['pan']
        if vals:
            self.patient_id.write(vals)
        return hospitalization
    def action_show_accommodation(self):
        action = self.env.ref('tcb_hospitalization_module.action_patient_accommodation_history').read()[0]
        action['domain'] = [('hospitalization_id', '=', self.id)]
        action['context'] = {'default_hospitalization_id': self.id}
        return action
    
    def action_request_discharge(self):
        self.state = 'discharge_requested'
        res_model = self.env['ir.model'].sudo().search([('model', '=', self._name)])
        activity_vals = {
            'res_id': self.id,
            'res_model_id': res_model.id,
            'summary': _(f'Dear {self.physician_id.name}, Please give the approval for discharge.'),
            'automated': True,
            'user_id': self.physician_id.user_id.id
        }
        activity = self.env['mail.activity'].with_context(mail_activity_quick_update=True).create(activity_vals)
    
    
    def action_discharge(self):
        for rec in self:
            rec.state = 'discharged'
            rec.bed_id.sudo().write({'state': 'free'})
            rec.discharge_date = datetime.now()
            for history in rec.accommodation_history_ids:
                if rec.bed_id == history.bed_id:
                    history.sudo().end_date = datetime.now()
            rec.patient_id.hospitalize = False
            rec.bed_id.sudo().write({'patient_id': False})
        
        
        
        
    def action_refund_ipd_payment(self):
        return {
            'name': 'Refund Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id':self.patient_id.id,
                'default_hospitalization_id': self.id,
                'default_invoice_id': self.invoice_id.id,
                'default_payment_type': 'send',
                'default_payment_mode': 'cash',
                'default_payment_amount': self.ipd_total_paid_amount
            }
        }
        
    def action_ready_for_payment(self):
        self.ready_for_payment_bool = True
        
    def action_create_ipd_payment(self):
        self.ensure_one()
        
        if self.invoice_id:
            invoice = self.invoice_id
        else:
            invoice_lines = []
            for service_line in self.hms_services_line_ids:
                line_vals = {
                    'product_id': service_line.product_id.id,
                    'quantity': service_line.quantity,
                    'price_unit': service_line.price,
                }
                invoice_lines.append((0, 0, line_vals))
            
            invoice_vals = {
                'patient_id': self.patient_id.id,
                'invoice_line_ids': invoice_lines, 
                'hospitalization_id': self.id,
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
                'default_patient_id':self.patient_id.id,
                'default_hospitalization_id': self.id,
                'default_invoice_id': self.invoice_id.id,
                'default_payment_type': 'receive',
                'default_payment_mode': 'cash',
                'default_payment_amount': self.ipd_amount_pending
            }
        }
    def action_done(self):
        self.state = 'done'
        
        
    def _get_previous_state(self, current_state):
        """
        Define the previous state for each current state
        """
        state_sequence = [
            'draft', 
            'confirmed', 
            'hospitalized', 
            'discharge_requested', 
            'discharged', 
            'done', 
            'cancel'
        ]
        
        try:
            current_index = state_sequence.index(current_state)
            if current_index > 0:
                return state_sequence[current_index - 1]
            return current_state
        except ValueError:
            return current_state


    
    def action_previous_state(self):
        """
        Button method to move to the previous state
        """
        for record in self:
            # Get the previous state
            previous_state = self._get_previous_state(record.state)
            
            # Additional validation or business logic can be added here
            if previous_state == record.state:
                raise UserError(_("Cannot move to a previous state."))
            
            # Optional: Add specific logic for certain state transitions
            if record.state == 'discharged':
                # Example: Check if discharge can be reverted
                if record.discharge_date:
                    record.discharge_date = False
            
            # Log the state change
            record.message_post(
                body=_("State changed from %s to %s") % (record.state, previous_state)
            )
            
            # Update the state
            record.state = previous_state
            
            
    def action_reset_to_draft(self):
        self.state = 'draft'
    
