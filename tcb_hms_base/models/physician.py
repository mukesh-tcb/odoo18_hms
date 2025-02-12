# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OtherPhysician(models.Model):
    _name = 'other.physician'
    _description = "Other Physicians Records and names"

    name = fields.Char(string='Other Physician', required=True)


class PhysicianSpecialty(models.Model):
    _name = 'physician.specialty'
    _description = "Physician Specialty"

    code = fields.Char(string='Code')
    name = fields.Char(string='Specialty', required=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]


class PhysicianDegree(models.Model):
    _name = 'physician.degree'
    _description = "Physician Degree"

    name = fields.Char(string='Degree')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]


class Physician(models.Model):
    _name = 'hms.physician'
    _description = "Physician"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.users': 'user_id'}

    user_id = fields.Many2one('res.users',string='Related User', required=True,
        ondelete='cascade', help='User-related data of the physician')
    code = fields.Char(string='Physician Code', default='/', tracking=True)
    degree_ids = fields.Many2many('physician.degree', 'physician_rel_education', 'physician_ids','degree_ids', string='Degree')
    specialty_id = fields.Many2one('physician.specialty', ondelete='set null', string='Specialty', help='Specialty Code', tracking=True)
    medical_license = fields.Char(string='Medical License', tracking=True)
    registration_number = fields.Char(string='Registration Number', tracking=True)
    physician_department_id = fields.Many2one('tcb.department', ondelete='set null', string='Department', help='Physician\'s Department', tracking=True)
    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('code','/') == '/':
                values['code'] = self.env['ir.sequence'].next_by_code('hms.physician')
            if values.get('email'):
                values['login'] = values.get('email')

            #TCB: It creates issue in physican creation
            if values.get('user_ids'):
                values.pop('user_ids')

        return super(Physician, self).create(vals_list)

    differ_charges_ids = fields.One2many('physician.differ_charges', 'physician_id', string="Differ Charges")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
