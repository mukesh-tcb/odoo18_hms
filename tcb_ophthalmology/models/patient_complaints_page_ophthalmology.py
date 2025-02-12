from odoo import api, fields, models, _
from odoo.exceptions import UserError



class TcbOphthalmologyOphthalmalicComplaints(models.Model):
    _name = "tcb.ophthalmology.ophthalmalic_complaints"

    eye = fields.Selection([
        ('none', 'NONE'),
        ('both_eyes', 'BOTH EYES'),
        ('left_eye', 'LEFT EYE'),
        ('right_eye', 'RIGHT EYE')
    ], default='none', required=True)
    complaints = fields.Many2one('tcb.complaints', string="COMPLAINTS")
    duration = fields.Char(string="Duration")
    duration_unit = fields.Many2one('tcb.durations.unit', string="Duration Unit")
    sl_no = fields.Integer(string="SL")
    tcb_ophthalmology_id = fields.Many2one('tcb.ophthalmology.evaluation', string="Ophthalmology Reference")


class TcbOphthalmologyPastHistory(models.Model):
    _name = "tcb.ophthalmology.past_history"

    eye = fields.Selection([
        ('none', 'NONE'),
        ('both_eyes', 'BOTH EYES'),
        ('left_eye', 'LEFT EYE'),
        ('right_eye', 'RIGHT EYE')
    ], default='none', required=True)
    past_history = fields.Many2one('tcb.history', string="PAST HISTORY")
    duration = fields.Char(string="Duration")
    duration_unit = fields.Many2one('tcb.durations.unit', string="Type")
    tcb_ophthalmology_past_history_id = fields.Many2one('tcb.ophthalmology.evaluation', string="Ophthalmology Id")


class TcbOphthalmologySystematicIllnessEye(models.Model):
    _name = "tcb.ophthalmology.systematic_illness"

    disease_id = fields.Many2one('tcb.eye.disease', string="Diseases")
    status_id = fields.Many2one('tcb.eye.disease.status', 'Status')
    duration = fields.Char(string="Duration")
    duration_unit = fields.Many2one('tcb.durations.unit', string="Type")
    tcb_ophthalmology_systematic_illness_id = fields.Many2one('tcb.ophthalmology.evaluation', string="Ophthalmology Id")




class TcbComplaints(models.Model):
    _name = "tcb.complaints"

    name = fields.Char(string="Name")


class TcbEyeDisease(models.Model):
    _name = "tcb.eye.disease"

    name = fields.Char(string="Name")
    disease_icd_code = fields.Char(string="ICD Code")


class TcbDurations(models.Model):
    _name = "tcb.durations"

    name = fields.Char(string="Name")


class TcbEYEStatusDisease(models.Model):
    _name = "tcb.eye.disease.status"

    name = fields.Char(string="Name")


class TcbDurationsUnit(models.Model):
    _name = "tcb.durations.unit"

    name = fields.Char(string="Name")


class TcbHistory(models.Model):
    _name = "tcb.history"

    name = fields.Char(string="Name")