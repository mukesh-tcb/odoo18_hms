from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class TcbEyeSph(models.Model):
    _name = "eye.sph"

    name = fields.Char(string="Name")


class TcbEyeAxis(models.Model):
    _name = "eye.axis"

    name = fields.Char(string="Name")


class TcbEyeCyl(models.Model):
    _name = "eye.cyl"

    name = fields.Char(string="Name")


class TcbEyeAdd(models.Model):
    _name = "eye.add"

    name = fields.Char(string="Name")


class UnaidedDistEye(models.Model):
    _name = "unaided.dist.eye"

    name = fields.Char(string="Name")


class UnaidedNearEye(models.Model):
    _name = "unaided.near.eye"

    name = fields.Char(string="Name")


class RefractionNctMachine(models.Model):
    _name = "tcb.ophthalmology.nct.machine"

    name = fields.Char(string="Name")


class RefractionPogType(models.Model):
    _name = "refraction.pog.type"

    name = fields.Char(string="Name")
