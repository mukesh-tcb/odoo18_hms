
from odoo import api, fields, models, _
from datetime import datetime
from random import randint
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime

import base64
from io import BytesIO

import odoo.modules as addons
loaded_modules = addons.module

class TcbFamilyRelation(models.Model):
    _name = 'tcb.family.relation'
    _description = "Family Relation"
    _order = "sequence"

    name = fields.Char(required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    inverse_relation_id = fields.Many2one("tcb.family.relation", string="Inverse Relation")


class ResPartnerInherit(models.Model):
    _inherit= "res.partner"

    is_referring_doctor = fields.Boolean(string="Is Refereinng Physician")


class HospitalDepartment(models.Model):
    _name = 'tcb.department'

    name = fields.Char('Name', required=True)
    note = fields.Text('Note')
    patient_department = fields.Boolean("Patient Department", default=True)
    appointment_ids = fields.One2many("hms.appointment", "department_id", "Appointments")
    department_type = fields.Selection([('general','General')], string="Hospital Department")
    # consultaion_service_id = fields.Many2one('product.product', ondelete='restrict', string='Consultation Service')
    # followup_service_id = fields.Many2one('product.product', ondelete='restrict', string='Followup Service')
    image = fields.Binary(string='Image')


class PhysicianDifferCharges(models.Model):
    _name = 'physician.differ_charges'
    # _rec_name = 'differ_category_id'


    name = fields.Char(string="Name")
    physician_id = fields.Many2one('hms.physician', string="Physician")
    # product_tmpl_id = fields.Many2one('product.template', string='Product')
    # product_id = fields.Many2one('product.product', string='Product Variant')
    # differ_category_id = fields.Many2one('physician.differ_category', string="Category")
    charges = fields.Float(string="Charges")

    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     if self.product_id:
    #         self.product_tmpl_id = self.product_id.product_tmpl_id.id
    #     else:
    #         self.product_tmpl_id = False


class PhysicianDifferCategory(models.Model):
    _name = 'physician.differ_category'

    name = fields.Char(string="Name")

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Category Name must be unique!'),
    ]


#This model is taken from opthalmology module because it is 
# also needed in the hospitalization module 
# so opthalmology module could not be the part of the depends of the hospitalization module.
class TcbDiagnosisDetails(models.Model):
    _name = "tcb.diagnosis.details"

    name = fields.Char(string="Name")
