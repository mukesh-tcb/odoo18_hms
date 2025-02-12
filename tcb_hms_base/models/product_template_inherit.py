from odoo import fields,api,models,_



class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'
    
    hospital_product_type = fields.Selection([
        ('medicament','Medicament'),
        ('os', 'Other Service'),
        ('not_medical', 'Not Medical'),
        ('procedure', 'Procedure'),
        ('bed', 'Bed'),
        ('consultation', 'Consultation'),
        ], string="Hospital Product Type", default='medicament')
    
    