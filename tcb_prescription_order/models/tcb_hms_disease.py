
from odoo import fields,models,api


class TcbHmsDisease(models.Model):
    _name = 'tcb.hms.disease'
    
    name = fields.Char(required=True)
    
    description = fields.Text()
    
    
