from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class HospitalWard(models.Model):
    _name = "hospital.ward"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = "This is the model for hospitalization ward and bed"
    
    @api.depends('bed_ids')
    def _rec_count(self):
        for rec in self:
            rec.bed_count = len(rec.bed_ids)
            rec.bed_available_count = len(rec.bed_ids.filtered(lambda r: r.state=='free' ))

    name = fields.Char(string='Name', required=True, 
        help='Ward / Room Number')
    floor = fields.Char(string='Floor Number')
    gender = fields.Selection([
        ('men', 'Men Ward'),
        ('women', 'Women Ward'),
        ('unisex', 'Unisex')], string='Gender', required=True, default="unisex")
    state = fields.Selection([
        ('available', 'Available'),
        ('full', 'Full')], string='Status', default="available")
    ward_room_type = fields.Selection([
        ('general', 'General'),
        ('semi_spaecial', 'Semi-Special'),
        ('deluxe', 'Deluxe'),
        ('super_deluxe', 'Super Deluxe'),
        ('suite', 'Suite'),
        ('sharing', 'Sharing'),
        ('icu', 'ICU'),
        ('dialysis', 'Dialysis'),
        ('recovery_room', 'Recovery Room'), ], 
        string='Wards/Room Type',required=True, default='general')
    
    description = fields.Text(string="Description")
    
    bed_ids = fields.One2many("hospital.bed",'ward_id',string="Beds")
    
    bed_count = fields.Integer(string="Bed Count", compute='_rec_count')
    bed_available_count = fields.Integer(string="Available Beds", compute='_rec_count')
    
    #Smart Button for showing the bed of that ward room
    def action_show_beds(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tcb_hospitalization_module.action_hospital_bed")
        action['domain'] = [('ward_id', '=', self.id)]
        action['context'] = {'default_ward_id': self.id}
        return action




class HospitalBed(models.Model):
    _name = "hospital.bed"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    def _get_patient(self):
        for rec in self:
            patient_id = False
            ac_hists = rec.accommodation_history_ids.filtered(lambda r: r.start_date and not r.end_date )
            if ac_hists:
                patient_id = ac_hists[0].patient_id.id
            rec.patient_id = patient_id


    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.state = 'occupied'
            
            
    READONLY_STATES = {'reserved': [('readonly', True)], 'occupied': [('readonly', True)], 'blocked': [('readonly', True)]}
    
    name = fields.Char(string='Name', required=1)
    product_id = fields.Many2one('product.template', ondelete='cascade',
        string='Bed Product', required=1, domain=[('hospital_product_type', '=', 'bed')],
        context={'default_hospital_product_type': 'bed'})
    list_price = fields.Float(related='product_id.list_price', string="Price", readonly=False)
    bed_type = fields.Selection([
        ('gatch', 'Gatch Bed'),
        ('electric', 'Electric'),
        ('stretcher', 'Stretcher'),
        ('low', 'Low Bed'),
        ('low_air_loss', 'Low Air Loss'),
        ('circo_electric', 'Circo Electric'),
        ('clinitron', 'Clinitron')], string='Type', default='gatch', required=True)
    telephone = fields.Char(string='Telephone')
    state = fields.Selection([
        ('free', 'Free'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
        ('blocked', 'Out of Use'),], string='Status', default="free")
    ward_id = fields.Many2one('hospital.ward', ondelete='restrict', string='Ward/Room')
    accommodation_history_ids = fields.One2many("patient.accommodation.history","bed_id",
        string="Accommodation History")
    notes = fields.Text(string='Notes')
    patient_id = fields.Many2one('hms.patient', ondelete="restrict", string="Patient")
    
    
    accommodation_count = fields.Integer(string="Accommodation Count",
        compute="_compute_accommodation_count"
    )

    @api.depends('accommodation_history_ids')
    def _compute_accommodation_count(self):
        for record in self:
            record.accommodation_count = self.env['patient.accommodation.history'].search_count([('bed_id', '=', record.id)])

    @api.onchange('product_id')
    def onchnage_product_id(self):
        if not self.name:
            self.name = self.product_id.name

    def action_accommodation_history(self):
        action = self.env.ref("tcb_hospitalization_module.action_patient_accommodation_history").read()[0]
        action['domain'] = [('bed_id', '=', self.id)]
        action['context'] = {'default_bed_id': self.id}
        return action

    def copy(self, default=None):
        self.ensure_one()
        chosen_name = default.get('name') if default else ''
        new_name = chosen_name or _('%s (copy)') % self.name
        default = dict(default or {}, name=new_name)
        return super(HospitalBed, self).copy(default)
    
    
    
