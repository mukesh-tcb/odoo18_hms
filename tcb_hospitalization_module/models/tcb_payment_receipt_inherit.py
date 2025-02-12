from odoo import _, api, fields, models


class PaymentReceiptInherit(models.Model):
    _inherit = 'tcb.payment.receipt'


    hospitalization_id = fields.Many2one('tcb.hospitalization',string="Hospitalization")