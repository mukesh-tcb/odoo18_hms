from odoo import fields,models,api,_
from odoo.exceptions import ValidationError


class TcbFrequency(models.Model):
    _name = "tcb.prescription.frequency"
    _description = "Frequency"
    
    name = fields.Char(string="Name")
    
    frequency = fields.Float(string="Frequency" , required=True)
    
    # If no frequency is less than 0 then give error
    # If frequency is less than or equal to 0, raise an error

    # @api.constrains('frequency')
    # def check_frequency(self):
    #     for record in self:
    #         if record.frequency <= 0.0:
    #             raise ValidationError(_("Frequency must be greater than 0"))
    
class TcbDuration(models.Model):
    _name = "tcb.prescription.duration"
    _description = "Duration"
    
    name = fields.Char(string="Name")
    days = fields.Float(string="Days" , required=True) 
    
    # If no duration is less than 0 then give error
    # If duration is less than or equal to 0, raise an error
    # @api.constrains('days')
    # def check_duration(self):
    #     for record in self:
    #         if record.days <= 0.0:
    #             raise ValidationError(_("Days must be greater than 0"))
    
class TcbPrescriptionLine(models.Model):
    _name = "tcb.prescription.line"
    _description = "Prescription Line"
    
    
    name=fields.Char(string="Name")
    
    prescription_order_id = fields.Many2one('tcb.prescription.order', string="Prescription Order Id")
    
    appointment_id = fields.Many2one('hms.appointment', string="Appointment Id")
    product_id = fields.Many2one('product.template', string="Medicine Name" ,context={'default_is_medicament_product':True})
    quantity = fields.Float(string="Quantity" , compute="compute_total_quantity" , store=True,readonly=False)
    
    price_unit = fields.Float(string="Unit Price")
    
    price_subtotal = fields.Float(string="Total" , compute="calculate_subtotal", store=True) 
    dosage = fields.Char(string="Dosage")
    
    add_in_bill_bool = fields.Boolean(string="Add in Bill" , default=True)
    
    note = fields.Text(string="Note")
    
    route_name=fields.Selection([
        ('topical','TOPICAL'),
        ('oral','ORAL'),
        ('intravitreal','INTRAVITREAL'),
    ],default="topical")
    
    frequency_id = fields.Many2one('tcb.prescription.frequency', string="Frequency")
    
    duration_id = fields.Many2one('tcb.prescription.duration', string="Duration")

    prescription_days = fields.Float(string="Days" , default=1 , store=True,related='duration_id.days')

    #Calculate Subtotal
    @api.depends('quantity', 'price_unit')
    def calculate_subtotal(self):
        for record in self:
            record.price_subtotal = record.quantity * record.price_unit


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.price_unit = self.product_id.list_price
    
    @api.onchange('duration_id')
    def onchange_duration_id(self):
        if self.duration_id:
            self.prescription_days = self.duration_id.days
            
    
    @api.depends('quantity','prescription_days', 'frequency_id', 'frequency_id.frequency', 'duration_id')
    def compute_total_quantity(self):
            # round off it complete value of quantity
        total_quantity = 0
        for line in self:
            line.quantity = line.prescription_days * line.frequency_id.frequency 
            line.quantity = round(line.quantity)
    
    # @api.model
    # def create(self, vals):
    #     if 'product_id' in vals:
    #         product_vals = {
    #             'name': vals.get('name'),
    #             'is_medicament_product': True,
    #         }
    #         product = self.env['product.template'].create(product_vals)
    #         vals['product_id'] = product.id 
    #     return super(TcbPrescriptionLine, self).create(vals)
    
    @api.model

    def create(self, vals):
        # Check if product_id is already provided
        if not vals.get('product_id'):
            # Search for an existing product with the same name
            existing_product = self.env['product.template'].search([
                ('name', '=', vals.get('name')),
                ('is_medicament_product', '=', True)
            ], limit=1)
            # If no existing product found, create a new on
            if not existing_product:
                product_vals = {
                    'name': vals.get('name', 'New Medicament'),
                    'is_medicament_product': True,
                    'type': 'product',  # Ensure it's a storable product
                }
                product = self.env['product.template'].create(product_vals)
                vals['product_id'] = product.product_variant_id.id
            else:
                vals['product_id'] = existing_product.product_variant_id.id


        # Create the prescription line

        return super(TcbPrescriptionLine, self).create(vals)