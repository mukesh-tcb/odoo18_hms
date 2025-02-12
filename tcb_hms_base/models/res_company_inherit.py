from odoo import models,fields,api





class ResCompanyInherit(models.Model):
    _inherit = 'res.company'


    nabh_logo = fields.Binary(string="NABH Logo")
    pm_jay_logo = fields.Binary(string="PM-JAY Logo")

    pain_level_diagram = fields.Binary(string="Pain Level Diagram")
    company_timing = fields.Char(string="Company Timing")
    
    