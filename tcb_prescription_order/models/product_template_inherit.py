from odoo import fields, models,api


class TcbDrugFrom(models.Model):    
    _name = "tcb.drug.from"
    _description = "Drug From"
    name = fields.Char(string="Name")
    
class TcbActiveComponent(models.Model):
    _name = "tcb.active.component"
    _description = "Active Component"
    name = fields.Char(string="Name")
    

class TcbDrugCompany(models.Model):
    _name = "tcb.drug.company"
    _description = "Drug Company"
    name = fields.Char(string="Name")
    

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_medicament_product = fields.Boolean('Is Medicament Product')
    
    route_name=fields.Selection([
        ('topical','TOPICAL'),
        ('oral','ORAL'),
        ('intravitreal','INTRAVITREAL'),
    ],default="topical")
    
    drug_from_id = fields.Many2one('tcb.drug.from', string="Drug From")
    
    active_component_ids = fields.Many2many('tcb.active.component', string="Active Component")
    
    frequency_id = fields.Many2one('tcb.prescription.frequency', string="Frequency")
    
    medic_product_code = fields.Char(string="Medicament Product Code")
    
    drug_company_id = fields.Many2one('tcb.drug.company', string="Drug Company")
    
    product_indication = fields.Text(string="Product Indication")
    
    medicament_notes = fields.Text(string="Medicament Notes")

    prescription_line_id = fields.Many2one('tcb.prescription.line', string="Prescription Line")
    
    
    #If Product is Created from Prescription Line then the Is medicament product should be True  So super the Create function 

    # @api.model
    # def create(self, vals):
    #     print("create method started")
        
    #     if self.env['tcb.prescription.line']:
    #         print("entered the if condition-----------")
    #         print("self.env['tcb.prescription.line'].id-----------",self.env['tcb.prescription.line'].id)
    #         vals['is_medicament_product'] = True
    #     else:
    #         print("self.env['tcb.prescription.line'].id-------Else condition----",self.env['tcb.prescription.line'])
    #         vals['name'] = vals.get('name')
    #     return super(ProductTemplate, self).create(vals)
