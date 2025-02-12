
from odoo import api, fields, models ,_
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime,date,time,timedelta
from odoo.exceptions import UserError, ValidationError



class TCBOphthalmologyEvaluation(models.Model):
    _name = "tcb.ophthalmology.evaluation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    _description = "Ophthalmology Evaluation"

    STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    name = fields.Char(string='Name', default='New', copy=False, tracking=True)
    patient_id = fields.Many2one('hms.patient', 'Patient', required=True, tracking=True)
    date = fields.Datetime('Date', default=fields.Datetime.now, help="Date of Consultation",tracking=True)
    age = fields.Char(string='Age', store=True,related = "patient_id.age",help="Computed patient age at the moment of the evaluation")
    gender=fields.Selection([('male', 'Male'), ('female', 'Female'),('other','Other')],related='patient_id.gender', string='Gender')
    physician_id = fields.Many2one('hms.physician', ondelete='restrict', string='Physician', 
        index=True, help='Physician\'s Name', tracking=True)
    appointment_id = fields.Many2one('hms.appointment', ondelete="restrict", 
        string='Appointment', tracking=True)
    
    # diseases_ids = fields.Many2many("hms.diseases", 'hms_diseases_ophthalmology_rel', 'evaluation_id', 'diseases_id', "Disease", states=STATES)

    follow_up_date = fields.Date(string="Follow Up")
    refer_to = fields.Many2one('hms.physician',string="Refer To", ondelete="restrict")

    follow_up_reason = fields.Text(string="Follow Up Reason")
    eye_drawing_le_re = fields.Binary(string="Eye Drawing")
    state = fields.Selection([('draft', 'Draft'), 
                            ('in_progress', 'In Progress'),
                            ('submitted', 'Submitted'),
                            ('done', 'Done'),
                            ('cancel', 'Cancel'),
                            ], default='draft', string="State",tracking=True)
    
    dilation_start_time = fields.Datetime(
        string='Dilation Start Time', 
        tracking=True
    )
    dilation_end_time = fields.Datetime(
        string='Dilation End Time', 
        readonly=True, 
        tracking=True
    )
    dilation_total_time = fields.Float(
        string='Total Dilation Time (Minutes)', 
        compute='_compute_dilation_total_time', 
        store=True
    )
    dilation_total_duration = fields.Char(
        string='Total Dilation Duration', 
        compute='update_dilation_durations',
        store=True
    )
    is_dilation_running = fields.Boolean(
        string='Is Dilation Running', 
        compute='_compute_is_dilation_running', 
        store=True
    )


    #Generating Sequence
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('tcb.ophthalmology.evaluation') or 'New'
        return super(TCBOphthalmologyEvaluation, self).create(vals)
    
    # compute='_compute_dilation_duration',   
    def action_start_dilation(self):
        """
        Start the dilation process
        """
        for record in self:
            # Check if dilation is already running
            if record.is_dilation_running:
                raise UserError(_("Dilation is already in progress."))
            
            # Set start time and reset end time
            record.dilation_start_time = fields.Datetime.now()
            record.dilation_end_time = False
            record.is_dilation_running = True

    def action_end_dilation(self):
        """
        End the dilation process
        """
        for record in self:
            # Check if dilation has started
            if not record.is_dilation_running:
                raise UserError(_("No active dilation process to end."))
            
            # Set end time
            record.dilation_end_time = fields.Datetime.now()
            record.is_dilation_running = False

    @api.depends('dilation_start_time', 'dilation_end_time')
    def _compute_dilation_total_time(self):
        """
        Compute total dilation time in minutes
        """
        for record in self:
            if record.dilation_start_time and record.dilation_end_time:
                # Calculate total time in minutes
                duration = record.dilation_end_time - record.dilation_start_time
                record.dilation_total_time = duration.total_seconds() / 60  # Convert to minutes
            else:
                record.dilation_total_time = 0.0

    @api.model
    def update_dilation_durations(self):
        evaluations = self.search([('is_dilation_running', '=', True)])
        for record in evaluations:
            if record.dilation_start_time:
                current_time = fields.Datetime.now()
                duration = current_time - record.dilation_start_time
                record.dilation_total_time = duration.total_seconds() / 60  # Update total time in minutes
    # @api.depends('dilation_start_time', 'dilation_end_time')
    # def _compute_dilation_duration(self):
    #     """
    #     Compute and format dilation duration as a readable string
    #     """
    #     for record in self:
    #         if record.dilation_start_time and record.dilation_end_time:
    #             duration = record.dilation_end_time - record.dilation_start_time
                
    #             # Convert duration to hours, minutes, seconds
    #             hours, remainder = divmod(duration.total_seconds(), 3600)
    #             minutes, seconds = divmod(remainder, 60)
                
    #             # Format the duration string
    #             record.dilation_total_duration = _(
    #                 "{hours} hours {minutes} minutes {seconds} seconds"
    #             ).format(
    #                 hours=int(hours), 
    #                 minutes=int(minutes), 
    #                 seconds=int(seconds)
    #             )
    #         else:
    #             record.dilation_total_duration = _("No duration")

    @api.depends('dilation_start_time', 'dilation_end_time')
    def _compute_is_dilation_running(self):
        """
        Compute if dilation is currently running
        """
        for record in self:
            record.is_dilation_running = (
                record.dilation_start_time and 
                not record.dilation_end_time
            )

    def reset_dilation_process(self):
        """
        Reset dilation process
        """
        self.write({
            'dilation_start_time': False,
            'dilation_end_time': False,
            'dilation_total_time': 0.0,
            'dilation_total_duration': False,
            'is_dilation_running': False
        })
        

    def tcb_open_websitefrom_appointment_url(self):
        self.ensure_one()
        if self.patient_id:
            return {
                'type': 'ir.actions.act_url',
                'url': '/tcb/webcam/' + self._name + '/' + str(self.id),
                'target': 'self',
                'context': {'from_appointment': True}
            }
        else:
            raise ValidationError(_("Please Save the appointment and then take a picture."))
    
    def action_draft_evaluation(self):
        self.write({'state': 'draft'})  # Ensure the state is set to draft
    
    def action_start_evaluation(self):
        self.write({'state': 'in_progress'})
        
    def action_submit_evaluation(self):
        self.write({'state': 'submitted'})
        
    def action_done_evaluation(self):
        # Change the state to 'done'
        self.write({'state': 'done'})
        print("started-----------------")
        # Check if there are prescription lines associated with this evaluation
        if self.oph_prescription_line_ids:
            print("_____entered Ifff-----------")
            # Create a prescription order
            prescription_order = self.env['tcb.prescription.order'].create({
                
                # 'ophthalmology_id':self.id,
                'patient_id': self.patient_id.id, # Assuming you have a patient_id field
                'physician_id': self.physician_id.id,  # Assuming you have a physician_id field
                'date': fields.Datetime.now(),  # Set the current date
                'appointment_id': self.appointment_id.id,
                'state': 'prescribed',  # Set prscribed
            })
            print("Created presccfiotion ofderrr ------------")
            # Loop through each prescription line and link it to the prescription order
            for line in self.oph_prescription_line_ids:
                # Create a prescription line for each line in the evaluation
                self.env['tcb.prescription.line'].create({
                    'ophthalmology_id':self.id,
                    'oph_eye':line.oph_eye,
                    'prescription_order_id': prescription_order.id,
                    'product_id':line.product_id.id,
                    'price_unit':line.price_unit,
                    'name':line.name,
                    'route_name':line.route_name,
                    'frequency_id':line.frequency_id.id,
                    'duration_id':line.duration_id.id,
                    'prescription_days':line.prescription_days,
                    'appointment_id' : line.appointment_id.id,
                    'dosage': line.dosage, 
                    'quantity': line.quantity, 
                })

        return True  # Return True to indicate success
        
    def action_cancel_evaluation(self):
        self.write({'state': 'cancel'})
        
    FOLLOW_UP_PERIODS = [
        ('one_day', '1 Day', 1),
        ('two_day', '2 Days', 2),
        ('three_day', '3 Days', 3),
        ('four_day', '4 Days', 4),
        ('five_day', '5 Days', 5),
        ('six_day', '6 Days', 6),
        ('one_week', '1 Week', 7),
        ('two_week', '2 Weeks', 14),
        ('one_month', '1 Month', 30),
        ('forty_five_day', '45 Days', 45),
        ('two_month', '2 Months', 60),
        ('three_month', '3 Months', 90),
        ('four_month', '4 Months', 120),
        ('six_month', '6 Months', 180),
        ('one_year', '1 Year', 365),
        ('two_year', '2 Years', 730)
    ]

    follow_up_day = fields.Selection(
        selection=[(code, label) for code, label, _ in FOLLOW_UP_PERIODS],
        string="Follow Up Time")


    @api.onchange('follow_up_day')
    def _onchange_follow_up_day(self):
        if self.follow_up_day:
            days = next(days for code, _, days in self.FOLLOW_UP_PERIODS if code == self.follow_up_day)
            self.follow_up_date = fields.Date.today() + timedelta(days=days)
        else:
            self.follow_up_date = False

    # Refraction Readings
    re_sph = fields.Float(string="Right Eye SPH")
    re_cyl = fields.Float(string="Right Eye CYL")
    re_axis = fields.Integer(string="Right Eye AXIS")
    re_add = fields.Float(string="Right Eye ADD")
    le_sph = fields.Float(string="Left Eye SPH")
    le_cyl = fields.Float(string="Left Eye CYL")
    le_axis = fields.Integer(string="Left Eye AXIS")
    le_add = fields.Float(string="Left Eye ADD")

    # Tonometer Readings
    nct_od = fields.Float(string="NCT OD")
    nct_os = fields.Float(string="NCT OS")
    gat_od = fields.Float(string="GAT OD")
    gat_os = fields.Float(string="GAT OS")
    cct_od = fields.Float(string="CCT OD")
    cct_os = fields.Float(string="CCT OS")

    # AR Readings - Dry and Wet
    ar_dry_re_sph = fields.Float(string="Dry SPH RE")
    ar_dry_re_cyl = fields.Float(string="Dry CYL RE")
    ar_dry_re_axis = fields.Integer(string="Dry AXIS RE")
    ar_dry_le_sph = fields.Float(string="Dry SPH LE")
    ar_dry_le_cyl = fields.Float(string="Dry CYL LE")
    ar_dry_le_axis = fields.Integer(string="Dry AXIS LE")

    # Examination
    color_vision = fields.Char(string="Color Vision")
    vision_od = fields.Float(string="Vision OD")
    vision_os = fields.Float(string="Vision OS")
    keratometry = fields.Char(string="Keratometry")

    # Additional Information Checkboxes
    workup_done = fields.Boolean(string="Workup Done")
    dilatation_needed = fields.Boolean(string="Dilatation Please")
    atropine_refraction = fields.Boolean(string="Atropine Refraction Please")
    cyclo_refraction = fields.Boolean(string="Cyclo Refraction Please")
    refraction_next_visit = fields.Boolean(string="Refraction Next Visit Please")

    # Notes
    optometrist_notes = fields.Text(string="Optometrist Notes")
    refraction_remarks = fields.Text(string="Refraction Remarks")
    
    
    
    
    
    #new fields for opthalmology
    eye_image = fields.Binary("Eye Image")
    unaided_re_dist_sph = fields.Float("RE Dist SPH")
    unaided_re_dist_cyl = fields.Float("RE Dist CYL")
    unaided_re_dist_axis = fields.Integer("RE Dist AXIS")
    unaided_re_dist_add = fields.Float("RE Dist ADD")
    unaided_re_near_sph = fields.Float("RE Near SPH")
    unaided_re_near_cyl = fields.Float("RE Near CYL")
    unaided_re_near_axis = fields.Integer("RE Near AXIS")
    unaided_re_near_add = fields.Float("RE Near ADD")
    
    unaided_le_dist_sph = fields.Float("LE Dist SPH")
    unaided_le_dist_cyl = fields.Float("LE Dist CYL")
    unaided_le_dist_axis = fields.Integer("LE Dist AXIS")
    unaided_le_dist_add = fields.Float("LE Dist ADD")
    unaided_le_near_sph = fields.Float("LE Near SPH")
    unaided_le_near_cyl = fields.Float("LE Near CYL")
    unaided_le_near_axis = fields.Integer("LE Near AXIS")
    unaided_le_near_add = fields.Float("LE Near ADD")
    
    # WITH PH fields
    ph_re_sph = fields.Float("PH RE SPH")
    ph_re_cyl = fields.Float("PH RE CYL")
    ph_re_axis = fields.Integer("PH RE AXIS")
    ph_re_add = fields.Float("PH RE ADD")
    ph_le_sph = fields.Float("PH LE SPH")
    ph_le_cyl = fields.Float("PH LE CYL")
    ph_le_axis = fields.Integer("PH LE AXIS")
    ph_le_add = fields.Float("PH LE ADD")
    
    # WITH EXISTING GLASS fields
    existing_re_dist_sph = fields.Float("Existing RE Dist SPH")
    existing_re_dist_cyl = fields.Float("Existing RE Dist CYL")
    existing_re_dist_axis = fields.Integer("Existing RE Dist AXIS")
    existing_re_dist_add = fields.Float("Existing RE Dist ADD")
    existing_re_near_sph = fields.Float("Existing RE Near SPH")
    existing_re_near_cyl = fields.Float("Existing RE Near CYL")
    existing_re_near_axis = fields.Integer("Existing RE Near AXIS")
    existing_re_near_add = fields.Float("Existing RE Near ADD")
    
    existing_le_dist_sph = fields.Float("Existing LE Dist SPH")
    existing_le_dist_cyl = fields.Float("Existing LE Dist CYL")
    existing_le_dist_axis = fields.Integer("Existing LE Dist AXIS")
    existing_le_dist_add = fields.Float("Existing LE Dist ADD")
    existing_le_near_sph = fields.Float("Existing LE Near SPH")
    existing_le_near_cyl = fields.Float("Existing LE Near CYL")
    existing_le_near_axis = fields.Integer("Existing LE Near AXIS")
    existing_le_near_add = fields.Float("Existing LE Near ADD")
    
    # AR Reading Status fields
    ar_dry_re_status = fields.Selection([
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal')
    ], string="AR Dry RE Status")
    ar_dry_le_status = fields.Selection([
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal')
    ], string="AR Dry LE Status")
    ar_wet_re_status = fields.Selection([
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal')
    ], string="AR Wet RE Status")
    
    
    #bb ai 
    #keratometry fields
    
    keratometry_od_k1 = fields.Char(string="Keratometry OD K1")
    keratometry_od_k2 = fields.Char(string="Keratometry OD K2")
    keratometry_os_k1 = fields.Char(string="Keratometry OS K1")
    keratometry_os_k2 = fields.Char(string="Keratometry OS K2")
    
    #axis
    keratometry_od_k1_r1_axis = fields.Char(string="Keratometry OD K1 R1 Axis")
    keratometry_od_k2_r2_axis = fields.Char(string="Keratometry OD K2 R2 Axis")
    
    keratometry_os_k1_r1_axis = fields.Char(string="Keratometry OS K1 R1 Axis")
    keratometry_os_k2_r2_axis = fields.Char(string="Keratometry OS K2 R2 Axis")
    
    #AXL
    keratometry_od_k1_r1_axl = fields.Char(string="Keratometry OD K1 R1 Axl")
    keratometry_od_k2_r2_axl = fields.Char(string="Keratometry OD K2 R2 Axl")
    
    keratometry_os_k1_r1_axl = fields.Char(string="Keratometry OS K1 R1 Axl")
    keratometry_os_k2_r2_axl = fields.Char(string="Keratometry OS K2 R2 Axl")
    
    #PCIOL
    
    keratometry_od_k1_r1_pciol = fields.Char(string="Keratometry OD K1 R1 PCIOL")
    keratometry_od_k2_r2_pciol = fields.Char(string="Keratometry OD K2 R2 PCIOL")
    
    keratometry_os_k1_r1_pciol = fields.Char(string="Keratometry OS K1 R1 PCIOL")
    keratometry_os_k2_r2_pciol = fields.Char(string="Keratometry OS K2 R2 PCIOL")
    
    #R1 R2
    keratometry_od_k1_r1 = fields.Char(string="Keratometry OD K1 R1")
    keratometry_od_k2_r2 = fields.Char(string="Keratometry OD K2 R2")
    

    keratometry_os_k1_r1 = fields.Char(string="Keratometry OS K1 R1")
    keratometry_os_k2_r2 = fields.Char(string="Keratometry OS K2 R2")

    
    
    
    color_vision_od = fields.Float(string="Color Vision OD")
    color_vision_os = fields.Float(string="Color Vision OS")
    
    tonometry_od_nct = fields.Float(string="Tonometry NCT OD")    
    tonometry_os_nct = fields.Float(string="Tonometry NCT OS")
    
    tonometry_od_gat = fields.Float(string="Tonometry GAT OD")    
    tonometry_os_gat = fields.Float(string="Tonometry GAT OS")
    
    tonometry_od_cct = fields.Float(string="Tonometry CCT OD")    
    tonometry_os_cct = fields.Float(string="Tonometry CCT OS")

    nct_machine_od = fields.Float(string="Net Machine OD")
    nct_machine_os = fields.Float(string="Net Machine OS")

    prism_value_re = fields.Float(string="Prism Value RE")
    prism_value_le = fields.Float(string="Prism Value LE")
    
    pachy_re = fields.Char(string='Pachy RE')
    pachy_le = fields.Char(string='Pachy LE')
    
    
    
    # DRY AR READINGS
    ar_dry_sph_right = fields.Many2one("eye.sph", string="AR DRY SPH Right")
    ar_dry_cyl_right = fields.Many2one("eye.cyl", string="AR DRY CYL Right")
    ar_dry_axis_right = fields.Many2one("eye.axis", string="AR DRY AXIS Right")
    ar_dry_status_right = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
        ('e', 'E')], string="AR DRY STATUS Right")
    ar_dry_sph_left = fields.Many2one("eye.sph", string="AR DRY SPH Left")
    ar_dry_cyl_left = fields.Many2one("eye.cyl", string="AR DRY CYL Left")
    ar_dry_axis_left = fields.Many2one("eye.axis", string="AR DRY AXIS Left")
    ar_dry_status_left = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
        ('e', 'E')], string="AR DRY STATUS Left")
    
    ar_wet_sph_right = fields.Many2one("eye.sph", string="AR WET SPH Right")
    ar_wet_cyl_right = fields.Many2one("eye.cyl", string="AR WET CYL Right")
    ar_wet_axis_right = fields.Many2one("eye.axis", string="AR WET AXIS Right")
    ar_wet_status_right = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
        ('e', 'E')], string="AR WET STATUS Right")
    ar_wet_sph_left = fields.Many2one("eye.sph", string="AR WET SPH Left")
    ar_wet_cyl_left = fields.Many2one("eye.cyl", string="AR WET CYL Left")
    ar_wet_axis_left = fields.Many2one("eye.axis", string="AR WET AXIS Left")
    ar_wet_status_left = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
        ('e', 'E')], string="AR WET STATUS Left")


# POG1 for refrection readings page 
    pog1_ref_sph_re = fields.Many2one("eye.sph", string="SPH POG1 RE")
    pog1_ref_cyl_re = fields.Many2one("eye.cyl", string="CYL POG1 RE")
    pog1_ref_axis_re = fields.Many2one("eye.axis", string="AXIS POG1 RE")
    pog1_ref_add_re = fields.Many2one("eye.add", string="ADD POG1 RE")

    pog1_ref_sph_le = fields.Many2one("eye.sph", string="SPH POG1 LE")
    pog1_ref_cyl_le = fields.Many2one("eye.cyl", string="CYL POG1 LE")
    pog1_ref_axis_le = fields.Many2one("eye.axis", string="AXIS POG1 LE")
    pog1_ref_add_le = fields.Many2one("eye.add", string="ADD POG1 LE")
    pog1_ref_type = fields.Selection([('normal', 'Normal'), ('abnormal', 'Abnormal')], string="POG1 Type")
    pog1_ref_how_old_value = fields.Char(string="How Old")
    pog1_ref_how_old_select = fields.Selection([('year', 'Year'), ('years', 'Years'), ('month', 'Month'),
                                                    ('months', 'Months'), ('week', 'Week'), ('weeks', 'Weeks'),
                                                    ('day', 'Day'),
                                                    ('days', 'Days')], string="How Old Type")
    pog1_ref_done_by = fields.Char(string="Done By")

    # POG2 for refrection readings page 
    pog2_ref_sph_re = fields.Many2one("eye.sph", string="SPH RE")
    pog2_ref_cyl_re = fields.Many2one("eye.cyl", string="CYL RE")
    pog2_ref_axis_re = fields.Many2one("eye.axis", string="AXIS RE")
    pog2_ref_add_re = fields.Many2one("eye.add", string="ADD RE")

    pog2_ref_sph_le = fields.Many2one("eye.sph", string="SPH LE")
    pog2_ref_cyl_le = fields.Many2one("eye.cyl", string="CYL LE")
    pog2_ref_axis_le = fields.Many2one("eye.axis", string="AXIS LE")
    pog2_ref_add_le = fields.Many2one("eye.add", string="ADD LE")
    pog2_ref_type = fields.Selection([('normal', 'Normal'), ('abnormal', 'Abnormal')], string="POG Type")
    pog2_ref_how_old_value = fields.Char(string="How Old")
    pog2_ref_how_old_select = fields.Selection([('year', 'Year'), ('years', 'Years'), ('month', 'Month'),
                                                    ('months', 'Months'), ('week', 'Week'), ('weeks', 'Weeks'),
                                                    ('day', 'Day'),
                                                    ('days', 'Days')], string="How Old Type")
    pog2_ref_done_by = fields.Char(string="Done By")

    # Refraction
    refraction_ipd = fields.Char(string="IPD")
    # Dist
    re_dist_va = fields.Many2one("unaided.dist.eye", "RE Dist. VA")
    refraction_dist_sph_re = fields.Many2one("eye.sph", string="SPH RE")
    refraction_dist_cyl_re = fields.Many2one("eye.cyl", string="CYL RE")
    refraction_dist_axis_re = fields.Many2one("eye.axis", string="AXIS RE")

    refraction_dist_sph_le = fields.Many2one("eye.sph", string="SPH LE")
    refraction_dist_cyl_le = fields.Many2one("eye.cyl", string="CYL LE")
    refraction_dist_axis_le = fields.Many2one("eye.axis", string="AXIS LE")
    le_dist_va = fields.Many2one("unaided.dist.eye", "LE Dist. VA")

    # Near
    re_near_va = fields.Many2one("unaided.near.eye", "RE Dist. VA")
    refraction_near_sph_re = fields.Many2one("eye.sph", string="SPH RE")
    refraction_near_cyl_re = fields.Many2one("eye.cyl", string="CYL RE")
    refraction_near_axis_re = fields.Many2one("eye.axis", string="AXIS RE")

    refraction_near_sph_le = fields.Many2one("eye.sph", string="SPH LE")
    refraction_near_cyl_le = fields.Many2one("eye.cyl", string="CYL LE")
    refraction_near_axis_le = fields.Many2one("eye.axis", string="AXIS LE")
    le_near_va = fields.Many2one("unaided.near.eye", "LE Dist. VA")


    # Last
    # Dist
    re_dist_va_last = fields.Many2one("unaided.dist.eye", "RE Dist. VA")
    refraction_dist_sph_re_last = fields.Many2one("eye.sph", string="SPH RE")
    refraction_dist_cyl_re_last = fields.Many2one("eye.cyl", string="CYL RE")
    refraction_dist_axis_re_last = fields.Many2one("eye.axis", string="AXIS RE")

    refraction_dist_sph_le_last = fields.Many2one("eye.sph", string="SPH LE")
    refraction_dist_cyl_le_last = fields.Many2one("eye.cyl", string="CYL LE")
    refraction_dist_axis_le_last = fields.Many2one("eye.axis", string="AXIS LE")
    le_dist_va_last = fields.Many2one("unaided.dist.eye", "LE Dist. VA")

    # Near
    re_near_va_last = fields.Many2one("unaided.near.eye", "RE Dist. VA")
    refraction_near_sph_re_last = fields.Many2one("eye.sph", string="SPH RE")
    refraction_near_cyl_re_last = fields.Many2one("eye.cyl", string="CYL RE")
    refraction_near_axis_re_last = fields.Many2one("eye.axis", string="AXIS RE")

    refraction_near_sph_le_last = fields.Many2one("eye.sph", string="SPH LE")
    refraction_near_cyl_le_last = fields.Many2one("eye.cyl", string="CYL LE")
    refraction_near_axis_le_last = fields.Many2one("eye.axis", string="AXIS LE")
    le_near_va_last = fields.Many2one("unaided.near.eye", "LE Dist. VA")

    # Prism Values
    prism_value_re = fields.Char(string="Prism Value RE")
    prism_value_le = fields.Char(string="Prism Value LE")

    # Notes
    
    
    ref_workup_done = fields.Boolean(string="Workup Done")
    ref_wet_ar_please = fields.Boolean(string="Wet AR Please")
    ref_dilation_please = fields.Boolean(string="Dilation Please")
    ref_pmt_please = fields.Boolean(string="PMT Please")
    cyclo_refraction_please = fields.Boolean(string="Cyclo Refraction Please")
    atropine_refraction_please = fields.Boolean(string="Atropine Refraction Please")
    refraction_next_visit_please = fields.Boolean(string="Refraction Next Visit Please")

##for presenting comlaints -- 
    presenting_complaints_values = fields.Integer(string="Values")
    
    DURATION_SELECTION = [
        ('d', 'Days'),
        ('m', 'Months'),
        ('y', 'Years'),
        ('h', 'Hours'),
        ('min', 'Minutes')
    ]

    EYE_SELECTION = [
        ('re', 'RE'),
        ('le', 'LE'),
        ('be', 'BE')
    ]

    # Symptoms fields
    watering = fields.Boolean(string="Watering in")
    watering_eye = fields.Selection(EYE_SELECTION, string="Watering Eye")
    watering_since = fields.Char(string="Watering Since" )
    watering_duration_type = fields.Selection(DURATION_SELECTION, string="Watering Duration Type")

    redness = fields.Boolean(string="Redness in")
    redness_eye = fields.Selection(EYE_SELECTION, string="Redness Eye")
    redness_since = fields.Char(string="Redness Since")
    redness_duration_type = fields.Selection(DURATION_SELECTION, string="Redness Duration Type")

    decreased_vision = fields.Boolean(string="Decreased vision")
    decreased_vision_eye = fields.Selection(EYE_SELECTION, string="Decreased Vision Eye")
    decreased_vision_since = fields.Char(string="Decreased Vision Since")
    decreased_vision_duration_type = fields.Selection(DURATION_SELECTION, string="Decreased Vision Duration Type")

    pain = fields.Boolean(string="Pain")
    pain_eye = fields.Selection(EYE_SELECTION, string="Pain Eye")
    pain_since = fields.Char(string="Pain Since")
    pain_duration_type = fields.Selection(DURATION_SELECTION, string="Pain Duration Type")

    discharge = fields.Boolean(string="Discharge")
    discharge_eye = fields.Selection(EYE_SELECTION, string="Discharge Eye")
    discharge_since = fields.Char(string="Discharge Since")
    discharge_duration_type = fields.Selection(DURATION_SELECTION, string="Discharge Duration Type")

    itching = fields.Boolean(string="Itching")
    itching_eye = fields.Selection(EYE_SELECTION, string="Itching Eye")
    itching_since = fields.Char(string="Itching Since")
    itching_duration_type = fields.Selection(DURATION_SELECTION, string="Itching Duration Type")

    burning = fields.Boolean(string="Burning")
    burning_eye = fields.Selection(EYE_SELECTION, string="Burning Eye")
    burning_since = fields.Char(string="Burning Since")
    burning_duration_type = fields.Selection(DURATION_SELECTION, string="Burning Duration Type")

    swelling = fields.Boolean(string="Swelling")
    swelling_eye = fields.Selection(EYE_SELECTION, string="Swelling Eye")
    swelling_since = fields.Char(string="Swelling Since")
    swelling_duration_type = fields.Selection(DURATION_SELECTION, string="Swelling Duration Type")

    irritation = fields.Boolean(string="Irritation")
    irritation_eye = fields.Selection(EYE_SELECTION, string="Irritation Eye")
    irritation_since = fields.Char(string="Irritation Since")
    irritation_duration_type = fields.Selection(DURATION_SELECTION, string="Irritation Duration Type")

    foreign_body = fields.Boolean(string="Foreign body")
    foreign_body_eye = fields.Selection(EYE_SELECTION, string="Foreign Body Eye")
    foreign_body_since = fields.Char(string="Foreign Body Since")
    foreign_body_duration_type = fields.Selection(DURATION_SELECTION, string="Foreign Body Duration Type")

    other = fields.Boolean(string="Other")
    other_eye = fields.Selection(EYE_SELECTION, string="Other Eye")
    other_since = fields.Char(string="Other Since")
    other_duration_type = fields.Selection(DURATION_SELECTION, string="Other Duration Type")
    other_description = fields.Char(string="Other Description")
    
    
    # Systemic Illness fields
    diabetes = fields.Boolean(string="Diabetes")
    diabetes_since = fields.Char(string="Diabetes Since")
    diabetes_duration = fields.Selection([
        ('d', 'D'),
        ('m', 'M'),
        ('y', 'Y'),
        ('h', 'H'),
        ('min', 'Min')
    ], string="Diabetes Duration")

    hypertension = fields.Boolean(string="Hypertension")
    hypertension_since = fields.Char(string="Hypertension Since")
    hypertension_duration = fields.Selection([
        ('d', 'D'),
        ('m', 'M'),
        ('y', 'Y'),
        ('h', 'H'),
        ('min', 'Min')
    ], string="Hypertension Duration")

    heart_disease = fields.Boolean(string="Heart Disease")
    heart_disease_since = fields.Char(string="Heart Disease Since")
    heart_disease_duration = fields.Selection([
        ('d', 'D'),
        ('m', 'M'),
        ('y', 'Y'),
        ('h', 'H'),
        ('min', 'Min')
    ], string="Heart Disease Duration")

    br_asthma = fields.Boolean(string="Br. asthma")
    br_asthma_since = fields.Char(string="Br. asthma Since")
    br_asthma_duration = fields.Selection([
        ('d', 'D'),
        ('m', 'M'),
        ('y', 'Y'),
        ('h', 'H'),
        ('min', 'Min')
    ], string="Br. asthma Duration")

    allergy = fields.Boolean(string="Allergy")
    allergy_since = fields.Char(string="Allergy Since")
    allergy_duration = fields.Selection([
        ('d', 'D'),
        ('m', 'M'),
        ('y', 'Y'),
        ('h', 'H'),
        ('min', 'Min')
    ], string="Allergy Duration")

    allergy_remarks = fields.Text(string="Allergy Remarks")
    presenting_complaint = fields.Text(string="Presenting Complaint")
    
    
    #Examination fields
    # Orbit
    orbit_le = fields.Many2one('tcb.ophthalmology.orbit', string='Orbit (LE)')
    orbit_re = fields.Many2one('tcb.ophthalmology.orbit', string='Orbit (RE)')

    # Lids and Adnexa
    lids_and_adnexa_le = fields.Many2one('tcb.ophthalmology.lids.and.adnexa', string='Lids and Adnexa (LE)')
    lids_and_adnexa_re = fields.Many2one('tcb.ophthalmology.lids.and.adnexa', string='Lids and Adnexa (RE)')

    # Conjunctiva
    conjunctiva_le = fields.Many2one('tcb.ophthalmology.conjunctiva', string='Conjunctiva (LE)')
    conjunctiva_re = fields.Many2one('tcb.ophthalmology.conjunctiva', string='Conjunctiva (RE)')

    # Sclera
    sclera_le = fields.Many2one('tcb.ophthalmology.sclera', string='Sclera (LE)')
    sclera_re = fields.Many2one('tcb.ophthalmology.sclera', string='Sclera (RE)')

    # Cornea
    cornea_le = fields.Many2one('tcb.ophthalmology.cornea', string='Cornea (LE)')
    cornea_re = fields.Many2one('tcb.ophthalmology.cornea', string='Cornea (RE)')

    # Anterior Chamber
    anterior_chamber_le = fields.Many2one('tcb.ophthalmology.anterior.chamber', string='Anterior Chamber (LE)')
    anterior_chamber_re = fields.Many2one('tcb.ophthalmology.anterior.chamber', string='Anterior Chamber (RE)')

    # Pupil
    pupil_le = fields.Many2one('tcb.ophthalmology.pupil', string='Pupil (LE)')
    pupil_re = fields.Many2one('tcb.ophthalmology.pupil', string='Pupil (RE)')

    # Iris
    iris_le = fields.Many2one('tcb.ophthalmology.iris', string='Iris (LE)')
    iris_re = fields.Many2one('tcb.ophthalmology.iris', string='Iris (RE)')

    # Lens
    lens_le = fields.Many2one('tcb.ophthalmology.lens', string='Lens (LE)')
    lens_re = fields.Many2one('tcb.ophthalmology.lens', string='Lens (RE)')

    # IOP
    iop_le = fields.Many2one('tcb.ophthalmology.iop', string='IOP (LE)')
    iop_re = fields.Many2one('tcb.ophthalmology.iop', string='IOP (RE)')

    # Fundus
    fundus_le = fields.Many2one('tcb.ophthalmology.fundus', string='Fundus (LE)')
    fundus_re = fields.Many2one('tcb.ophthalmology.fundus', string='Fundus (RE)')

    # EDM
    edm_le = fields.Many2one('tcb.ophthalmology.edm', string='EDM (LE)')
    edm_re = fields.Many2one('tcb.ophthalmology.edm', string='EDM (RE)')

    # DUCT
    duct_le = fields.Many2one('tcb.ophthalmology.duct', string='DUCT (LE)')
    duct_re = fields.Many2one('tcb.ophthalmology.duct', string='DUCT (RE)')

    # BP
    bp = fields.Char(string="BP")
    fbs = fields.Char(string="FBS")
    ppbs = fields.Char(string="PPBS")
    hba1c = fields.Char(string="HBA1C")
    rbs = fields.Char(string="RBS")
    
    # Nutrition Growth
    nutrition_growth_height = fields.Float('Height')
    nutrition_growth_weight = fields.Float('Weight')
    
    
    retinoscopy_axis_1_re = fields.Char(string="Axis 1 RE")
    retinoscopy_axis_2_re = fields.Char(string="Axis 2 RE")
    retinoscopy_axis_3_re = fields.Char(string="Axis 3 RE")
    retinoscopy_axis_4_re = fields.Char(string="Axis 4 RE")
    
    retinoscopy_axis_1_le = fields.Char(string="Axis 1 LE")
    retinoscopy_axis_2_le = fields.Char(string="Axis 2 LE")
    retinoscopy_axis_3_le = fields.Char(string="Axis 3 LE")
    retinoscopy_axis_4_le = fields.Char(string="Axis 4 LE")
    # Dilated Retinoscopy fields
    dilated_retinoscopy_axis_1_re = fields.Char(string="Dilated Axis 1 RE")
    dilated_retinoscopy_axis_2_re = fields.Char(string="Dilated Axis 2 RE")
    dilated_retinoscopy_axis_3_re = fields.Char(string="Dilated Axis 3 RE")
    dilated_retinoscopy_axis_4_re = fields.Char(string="Dilated Axis 4 RE")

    dilated_retinoscopy_axis_1_le = fields.Char(string="Dilated Axis 1 LE")
    dilated_retinoscopy_axis_2_le = fields.Char(string="Dilated Axis 2 LE")
    dilated_retinoscopy_axis_3_le = fields.Char(string="Dilated Axis 3 LE")
    dilated_retinoscopy_axis_4_le = fields.Char(string="Dilated Axis 4 LE")

    dilated_retinoscopy_remarks = fields.Text(string="Dialated Retinoscopy Remarks")
    medication_history = fields.Text(string="Medication History")



    # Gonioscopy fields
    #Gonioscopy
    re_gon_top_val = fields.Char(string="RE Top")
    re_gon_left_val = fields.Char(string="RE Left")
    re_gon_right_val = fields.Char(string="RE Right")
    re_gon_bottom_val = fields.Char(string="RE Bottom")
    
    le_gon_top_val = fields.Char(string="LE Top")
    le_gon_left_val = fields.Char(string="LE Left")
    le_gon_right_val = fields.Char(string="LE Right")
    le_gon_bottom_val = fields.Char(string="LE Bottom")
    
    tm_pigmentation = fields.Char(string="TM-Pigmentation")
    iris_configuration = fields.Char(string="IRIS Configuration")
    impression = fields.Char(string="Impression")
    
    #Contact lens page fields
    #for CL History table fields
    using_contact_lens_since = fields.Char(string="Using Contact Lens Since")
    using_contact_lens_since_duration = fields.Selection([
        ('d', 'D'),
        ('m', 'M'),
        ('y', 'Y'),
        ('h', 'H'),
        ('min', 'Min')
    ], string="Duration")
    
    times2 = fields.Selection([('d', 'D'), ('m', 'M'), ('y', 'Y'), ('h', 'H'), ('min', 'Min')])

    type_of_contact_lens = fields.Many2one('tcb.ophthalmology.typesofcontactlens', string="Types Of Contact Lens")
    name_of_the_solution = fields.Many2one('tcb.ophthalmology.nameofthesolution', string="Name Of The Solution")

    cleaning_contact_lens_cl = fields.Char(string="Cleaning Contact Lens Cl")
    cleaning_contact_lens_case = fields.Char(string="Case")

    usage_a_day = fields.Char(string='Usage A Day')

    power_of_contact_lens = fields.Selection([('sph', 'SPH'), ('cyl', 'CYL'), ('axis', 'AXIS')],
                                            string="Power Of Contact Lens")
    
    pcl_sph_re = fields.Many2one("eye.sph", string="SPH")
    pcl_cyl_re = fields.Many2one("eye.cyl", string="CYL")
    pcl_axis_re = fields.Many2one("eye.axis", string="Axis")
    pcl_sph_le = fields.Many2one("eye.sph", string="SPH")
    pcl_cyl_le = fields.Many2one("eye.cyl", string="CYL")
    pcl_axis_le = fields.Many2one("eye.axis", string="Axis")

    ppcl = fields.Char(string='P P C L')
    ppcl_select = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="P P C L")

    sleeping_with_contact_lens = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="Sleeping With Contact Lens")
    sleeping_with_contact_lens_duration = fields.Char(string="Sleeping With Contact Lens Duration")

    cl_last_used = fields.Char(string='CL Last Used')
    cl_last_usage_a_day = fields.Selection([('yes', 'YES'), ('no', 'NO')])

    any_problem_with_cl_re = fields.Many2one('tcb.ophthalmology.any_problem_with_cl', string="Types Of Contact Lens")
    any_problem_with_cl_le = fields.Many2one('tcb.ophthalmology.any_problem_with_cl', string="Types Of Contact Lens")

    machine_type = fields.Selection([('auto', 'Auto'), ('manual', 'Manual')], string="Machine Type")
    
    # AR WITH CL fields
    ar_with_cl_sph_re = fields.Many2one("eye.sph", string="SPH")
    ar_with_cl_cyl_re = fields.Many2one("eye.cyl", string="CYL")
    ar_with_cl_axis_re = fields.Many2one("eye.axis", string="AXIS")
    ar_with_cl_status_re = fields.Selection([('draft', 'DRAFT'), ('done', 'DONE')], string="Status")

    ar_with_cl_sph_le = fields.Many2one("eye.sph", string="SPH")
    ar_with_cl_cyl_le = fields.Many2one("eye.cyl", string="CYL")
    ar_with_cl_axis_le = fields.Many2one("eye.axis", string="AXIS")
    ar_with_cl_status_le = fields.Selection([('draft', 'DRAFT'), ('done', 'DONE')], string="Status")

    # AR WITHOUT CL fields
    ar_without_cl_sph_re = fields.Many2one("eye.sph", string="SPH")
    ar_without_cl_cyl_re = fields.Many2one("eye.cyl", string="CYL")
    ar_without_cl_axis_re = fields.Many2one("eye.axis", string="AXIS")
    ar_without_cl_status_re = fields.Selection([('draft', 'DRAFT'), ('done', 'DONE')], string="Status")

    ar_without_cl_sph_le = fields.Many2one("eye.sph", string="SPH")
    ar_without_cl_cyl_le = fields.Many2one("eye.cyl", string="CYL")
    ar_without_cl_axis_le = fields.Many2one("eye.axis", string="AXIS")
    ar_without_cl_status_le = fields.Selection([('draft', 'DRAFT'), ('done', 'DONE')], string="Status")

    # VA WITH CL fields
    va_with_cl_sph_re = fields.Many2one("eye.sph", string="SPH")
    va_with_cl_cyl_re = fields.Many2one("eye.cyl", string="CYL")
    va_with_cl_axis_re = fields.Many2one("eye.axis", string="AXIS")
    va_with_cl_va_re = fields.Selection([('draft', 'DRAFT'), ('done', 'DONE')], string="VA")

    va_with_cl_sph_le = fields.Many2one("eye.sph", string="SPH")
    va_with_cl_cyl_le = fields.Many2one("eye.cyl", string="CYL")
    va_with_cl_axis_le = fields.Many2one("eye.axis", string="AXIS")
    va_with_cl_va_le = fields.Selection([('draft', 'DRAFT'), ('done', 'DONE')], string="VA")    
    
    #over the Refraction
    va_with_cl_re = fields.Char(string="VA With CL RE")
    va_with_cl_le = fields.Char(string="VA With CL LE")
    
    
    #CL Prescription
    cl_prescription_sphere_re = fields.Char(string="CL Prescription Sphere RE")
    cl_prescription_sph_re = fields.Many2one("eye.sph", string='CL Prescription Sph RE')
    cl_prescription_cyl_re = fields.Many2one("eye.cyl", string='CL Prescription Cyl RE')
    cl_prescription_axis_re = fields.Many2one("eye.axis", string='CL Prescription Axis RE')
    cl_prescription_base_curve_re = fields.Char(string='CL Prescription Base Curve RE')
    cl_prescription_diameter_re = fields.Char(string='CL Prescription Diameter RE')
    cl_prescription_lenstype_re = fields.Many2one('tcb.ophthalmology.lenstype', string="CL Prescription Lens Type RE")
    cl_prescription_brand_re = fields.Many2one('tcb.ophthalmology.brand', string="CL Prescription Brand RE")
    cl_prescription_colour_re = fields.Many2one('tcb.ophthalmology.colour', string="CL Prescription Colour RE")
    
    cl_prescription_sphere_le = fields.Char(string="CL Prescription Sphere LE")
    cl_prescription_sph_le = fields.Many2one("eye.sph", string='CL Prescription Sph LE')
    cl_prescription_cyl_le = fields.Many2one("eye.cyl", string='CL Prescription Cyl LE')
    cl_prescription_axis_le = fields.Many2one("eye.axis", string='CL Prescription Axis LE')
    cl_prescription_base_curve_le = fields.Char(string='CL Prescription Base Curve LE')
    cl_prescription_diameter_le = fields.Char(string='CL Prescription Diameter LE')
    cl_prescription_lenstype_le = fields.Many2one('tcb.ophthalmology.lenstype', string="CL Prescription Lens Type LE")
    cl_prescription_brand_le = fields.Many2one('tcb.ophthalmology.brand', string="CL Prescription Brand LE")
    cl_prescription_colour_le = fields.Many2one('tcb.ophthalmology.colour', string="CL Prescription Colour LE")

    cl_prescription_done_by = fields.Char(string='CL Prescribed By')

    cl_prescription_remarks = fields.Text(string="REMARKS")
    
    
    #Contact Lens Keratomatery fields 
    #keratometry fields
    
    contact_lens_keratometry_machine_type = fields.Selection([('auto', 'Auto'), ('manual', 'Manual')], string="Machine Type")
    contact_lens_keratometry_od_k1 = fields.Char(string="Contact Lens Keratometry OD K1")
    contact_lens_keratometry_od_k2 = fields.Char(string="Contact Lens Keratometry OD K2")
    contact_lens_keratometry_os_k1 = fields.Char(string="Contact Lens Keratometry OS K1")
    contact_lens_keratometry_os_k2 = fields.Char(string="Contact Lens Keratometry OS K2")
    
    #axis
    contact_lens_keratometry_od_k1_axis = fields.Char(string="Contact Lens Keratometry OD K1 R1 Axis")
    contact_lens_keratometry_od_k2_axis = fields.Char(string="Contact Lens Keratometry OD K2 R2 Axis")
    
    contact_lens_keratometry_os_k1_axis = fields.Char(string="Contact Lens Keratometry OS K1 R1 Axis")
    contact_lens_keratometry_os_k2_axis = fields.Char(string="Contact Lens Keratometry OS K2 R2 Axis")
    

    
    
    # patients_complaints page fields
    ophthalmic_complaints = fields.Char(string="OPHTHALMIC COMPLAINTS")

    ophthalmic_complaints_ids = fields.One2many('tcb.ophthalmology.ophthalmalic_complaints', 'tcb_ophthalmology_id',
                                string='Ophthalmic Complaints ids')
    # Past History

    past_history_ids = fields.One2many('tcb.ophthalmology.past_history', 'tcb_ophthalmology_past_history_id',
        string='Past History ids')

    # Systematic Illness
    systematic_illness_ids = fields.One2many('tcb.ophthalmology.systematic_illness', 'tcb_ophthalmology_systematic_illness_id',
        string='Systematic Illness ids')

    #doctor screen 
    optometry_nct_machine = fields.Many2one('tcb.ophthalmology.nct.machine',string="Optometry NCT Machine")

class TcbEyeSph(models.Model):
    _name = "tcb.ophthalmology.orbit"
    name = fields.Char(string="Name")

class TcbEyeAxis(models.Model):
    _name = "tcb.ophthalmology.lids.and.adnexa"
    name = fields.Char(string="Name")

class TcbEyeCyl(models.Model):
    _name = "tcb.ophthalmology.conjunctiva"
    name = fields.Char(string="Name")

class TcbEyeAdd(models.Model):
    _name = "tcb.ophthalmology.sclera"
    name = fields.Char(string="Name")

class UnaidedDistEye(models.Model):
    _name = "tcb.ophthalmology.cornea"
    name = fields.Char(string="Name")

class UnaidedNearEye(models.Model):
    _name = "tcb.ophthalmology.anterior.chamber"
    name = fields.Char(string="Name")

class RefractionNctMachine(models.Model):
    _name = "tcb.ophthalmology.pupil"
    name = fields.Char(string="Name")

class TcbOphthalmologyIris(models.Model):
    _name = "tcb.ophthalmology.iris"
    name = fields.Char(string="Name")

class TcbOphthalmologyLens(models.Model):
    _name = "tcb.ophthalmology.lens"
    name = fields.Char(string="Name")

class TcbOphthalmologyIop(models.Model):
    _name = "tcb.ophthalmology.iop"
    name = fields.Char(string="Name")

class TcbOphthalmologyFundus(models.Model):
    _name = "tcb.ophthalmology.fundus"
    name = fields.Char(string="Name")

class TcbOphthalmologyEdm(models.Model):
    _name = "tcb.ophthalmology.edm"
    name = fields.Char(string="Name")

class TcbOphthalmologyDuct(models.Model):
    _name = "tcb.ophthalmology.duct"
    name = fields.Char(string="Name")



class TcbOphthalmologyTypesOfContactLens(models.Model):
    _name = "tcb.ophthalmology.typesofcontactlens"
    name = fields.Char(string="Name")

class TcbOphthalmologyNameOfTheSolution(models.Model):
    _name = "tcb.ophthalmology.nameofthesolution"
    name = fields.Char(string="Name")

class TcbOphthalmologyAnyProblemWithCl(models.Model):
    _name = "tcb.ophthalmology.any_problem_with_cl"
    name = fields.Char(string="Name")


class TcbLENSTYPE(models.Model):
    _name = 'tcb.ophthalmology.lenstype'

    name = fields.Char(string="LENS TYPE")


class TcbBRAND(models.Model):
    _name = 'tcb.ophthalmology.brand'

    name = fields.Char(string="BRAND")


class TcbCOLOUR(models.Model):
    _name = 'tcb.ophthalmology.colour'
    name = fields.Char(string="COLOUR")
    

