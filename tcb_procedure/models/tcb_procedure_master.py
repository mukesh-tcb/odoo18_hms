from odoo import _, api, fields, models

from odoo.exceptions import UserError, ValidationError


class TCBProcedureMaster(models.Model):
    _name = "tcb.procedure.master"

    name = fields.Char(string="Name", required=True)
    procedure_price = fields.Float(string="Price", required=True)

