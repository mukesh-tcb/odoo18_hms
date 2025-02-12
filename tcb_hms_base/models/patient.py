# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError,ValidationError


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import format_datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF, format_datetime as tool_format_datetime
import pprint

class ResPartner(models.Model):
    _inherit= "res.partner"

    is_referring_doctor = fields.Boolean(string="Is Refereinng Physician")
    is_referering_patient = fields.Boolean(string="Is Referering Patient")

class HmsPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Patient Master'
    _inherit = ['mail.thread', 'mail.activity.mixin','image.mixin']
    _rec_name = 'name_display'
    _rec_names_search = 'name','patient_name'
    # _inherits = {
    #     'res.partner': 'partner_id',
    # }
    name = fields.Char(string='Patient Code',tracking=True,copy=False,readonly=True)
    # name_display = fields.Char(string="Display Name",store=True,copy=False,tracking=True)
    patient_name = fields.Char(string='Patient Name', tracking=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender', default="male",tracking=True)
    birthday = fields.Date(string='Date of Birth' , store=True, tracking=True)
    date_of_birth = fields.Date(string='Date of Birth',store=True, tracking=True)
    care_of = fields.Char(string='Care of',tracking=True)
    relation = fields.Many2one('tcb.family.relation', string='Relation', tracking=True)
    age = fields.Char(string='Age', compute='_compute_age', store=True, tracking=True,readonly=False)
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ], string='Blood Group',tracking=True)

    # ref_doctor_ids = fields.Many2many('res.partner', 'rel_doc_pat', 'doc_id', 
    #     'patient_id', 'Referring Doctors',domain=[('is_referring_doctor','=',True)])

    title = fields.Many2one('res.partner.title',tracking=True)

    gov_code = fields.Char(string='Government Identity', copy=False, tracking=True)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ], string='Marital Status', default="single",tracking=True)
    spouse_name = fields.Char("Spouse's Name",tracking=True)
    spouse_edu = fields.Char("Spouse's Education",tracking=True)
    spouse_business = fields.Char("Spouse's Business",tracking=True)
    education = fields.Char("Patient Education",tracking=True)
    occupation = fields.Char("Occupation",tracking=True)
    religion = fields.Char("Religion",tracking=True)
    date_of_death = fields.Date("Date of Death",tracking=True)
    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)
    zip = fields.Char(tracking=True)
    city = fields.Char(tracking=True)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict' , domain="[('country_id', '=', country_id)]",tracking=True)
    country_id = fields.Many2one('res.country', string="Country", default=lambda self: self.env['res.country'].search([('code', '=', 'IN')], limit=1)) 

    phone = fields.Char(string="Phone",tracking=True)
    mobile = fields.Char(string="Mobile",tracking=True)
    email = fields.Char(string="Email",tracking=True)
    aadhar = fields.Char(string="Aadhar Number",tracking=True)
    pan = fields.Char(string="PAN Number",tracking=True)
    
    primary_physician_id = fields.Many2one('hms.physician' , 'Primary Care Doctor', tracking=True)

    active = fields.Boolean(string="Active", default=True, tracking=True)
    
    # partner_id = fields.Many2one('res.partner', string='Res Partner')
    
    is_patient = fields.Boolean(string="Is Patient", default=True, tracking=True)
    
    patient_payment_line_ids = fields.One2many('tcb.payment.receipt', 'patient_id' , string="Payment Reciepts", tracking=True)
    # api.onchange('patient_name', 'mobile','name')
    # def compute_name_display(self):
    #     for record in self:
    #         if record.mobile==False:
    #             record.mobile = ''
    #         # if record.patient_name:
    #         record.name_display = f"{record.name}-{record.patient_name}-{record.mobile}"
    #         # else:
    #         #     record.name_display = record.name  # Fallback if patient_name is not set
    #     return self.name_display 
            
            
    name_display = fields.Char(string='Display Name', compute='_compute_name_display',store=True)
    hospitalize = fields.Boolean(string="Hospitalize", default=False, tracking=True)
    
    @api.depends('name', 'patient_name', 'phone')
    def _compute_name_display(self):
        for record in self:
            if not record.phone:
                record.name_display = f"{record.name}-{record.patient_name}"
            else:
                record.name_display = f"{record.name}-{record.patient_name}-{record.phone}"
                
    @api.onchange('age')
    def onchange_age(self):
        for record in self:
            if record.age:
                if int(record.age) > 200:
                    raise ValidationError("Seriously?! %s years old?" % record.age)
                elif int(record.age) < 0:   
                    raise ValidationError("Seriously?! %s years old?" % record.age)
    
    @api.onchange('aadhar')
    def onchange_aadhar(self):
        if self.aadhar:
            if len(self.aadhar) != 12:
                raise ValidationError("Aadhar number must be 12 digits")
    
    
    @api.onchange('mobile','phone')
    def onchange_mobile(self):
        if self.mobile:
            if len(self.mobile) != 10:
                raise ValidationError("Mobile number must be 10 digits")
        if self.phone:
            if len(self.phone) != 10:
                raise ValidationError("Phone number must be 10 digits")
    
    @api.onchange('pan')
    def onchange_pan(self):
        if self.pan:
            if len(self.pan) != 10:
                raise ValidationError("PAN number must be 10 digits")
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hms.patient') or '/'
        
        if not self.patient_name:
            if self.env['hms.appointment'].patient_id:
                vals['patient_name'] = self.env['hms.appointment'].patient_id
            else:
                vals['patient_name'] = vals.get('name_display')
                # print("---------------patient name---------------vals--",vals.get('name_display'),"-----values - -",vals)
        # if not vals.get['patient_na']
        if vals.get('name_display'):
            if not vals.get('phone'):
                vals['name_display'] = f"{vals['name']}-{vals['patient_name']}"
            else:
                vals['name_display'] = f"{vals['name']}-{vals['patient_name']}-{vals['phone']}"
        patient = super(HmsPatient, self).create(vals)
        return patient
    
    
    
    # @api.model
    # def write(self,vals):
    #     for record in self:
    #         if record.phone:
    #             record.name_display = f"{record.name}-{record.patient_name}-{record.phone}"
    #     return super(HmsPatient,self).write(vals)
    # @api.onchange('country_id')
    # def _onchange_address(self):
    #     print('-------------------yeaay',self.country_id).

    #     records = self.env['res.partner'].search([])
    #     for record in records:
    #         print(record.name, record.is_referering_patient)

    # def write(self, vals):
    #     res = super(HmsPatient, self).write(vals)
    #     print("---------------WRITE VALS",vals)
    #     # Update the partner name if the patient name has changed
    #     if 'name' in vals:
    #         for record in self:
    #             if record.partner_id:
    #                 record.partner_id.name = vals['name']
    #             else:
    #                 # Create a new partner if it doesn't exist
    #                 partner = self.env['res.partner'].create({
    #                     'name': vals['name'],
    #                     'is_referering_patient': True,
    #                 })
    #                 record.partner_id = partner.id
                    
        # print("---------------WRITE RES  /n ",self.partner_id.name,"---------------partnerid - ",self.partner_id)
        # return res
    
    
    # @api.onchange('street', 'street2', 'city', 'state_id', 'zip', 'country_id')
    # def _onchange_address(self):
    #     print('-------------------yeaay')

    #     records = self.env['res.partner'].search([])
    #     for record in records:
    #         print(record.name, record.is_referering_patient) 
            
    # @api.onchange('name','care_of','partner_id')
    # def get_partner_id (self):
    #     if self.name:
    #         self.partner_id.name = self.name
    #         print("============yessssssssss- ", self.partner_id.name)
    #     else :
    #         self.partner_id = ""
    #         print("============nooooooooooooo- ", self.partner_id)
            
    # @api.model
    # def write(self, vals):
    #     if vals.get('patient_id'):
    #         partner_vals = {
    #             'name': vals['patient_id'],
    #             'is_patient': True,
    #         }
    #         partner_id = self.env['res.partner'].write(partner_vals)
    #         vals['patient_id'] =self.partner_id.name
    #         vals['partner_id'] = partner_id.id
    #     return super(HmsPatient, self).write(vals)
    
    
    
# , compute='_compute_invoicing_stats',, compute='_compute_invoicing_stats',
    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                record.age = (datetime.now().date() - record.date_of_birth).days // 365
            else:
                record.age = 0
    

    # @api.model
    # def create(self, vals):
        
    #     return super(HmsPatient, self).create(vals)



    def view_invoices(self):
        pass
        # self.ensure_one()
        # action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        # action['domain'] = [('partner_id', '=', self.partner_id.id), ('move_type', '=', 'out_invoice')]
        # return action

    def action_view_attachments(self):
        # self.ensure_one()
        # action = self.env.ref('base.action_attachment').read()[0]
        # action['domain'] = [('res_model', '=', 'hms.patient'), ('res_id', '=', self.id)]
        # action['context'] = {'default_res_model': 'hms.patient', 'default_res_id': self.id}
        # return action
        pass

    @api.depends('birthday')
    def _compute_today_is_birthday(self):
        today = fields.Date.today()
        for patient in self:
            patient.today_is_birthday = patient.birthday and patient.birthday.day == today.day and patient.birthday.month == today.month

    today_is_birthday = fields.Boolean(string="Is Birthday Today" )
    
    
    # # THese are more fields from inherited moudels
    
