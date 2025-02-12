from odoo import api, fields, models


class TcbDoctorOptometry(models.Model):
    _inherit = "tcb.ophthalmology.evaluation"

    doc_presenting_complaints = fields.Text(string='Presenting Complaints')
    doc_past_history = fields.Text(string='Past History')
    doc_systemic_illness = fields.Text(string='Systemic Illness')
    doc_ophthalmic_complaints = fields.Text(string='Ophthalmic Complaints')

    # Color Vision
    doc_color_vision_re = fields.Text(string='Color Vision RE')
    doc_color_vision_le = fields.Text(string='Color Vision LE')

    # Pachy Values
    doc_pachy_re = fields.Text(string='Pachy RE')
    doc_pachy_le = fields.Text(string='Pachy LE')

    # keratometry
    # OD
    doc_ker_od_k1 = fields.Char(string="K1")
    doc_ker_od_k2 = fields.Char(string="K2")
    doc_ker_od_k1_axis = fields.Char(string="Axis")
    doc_ker_od_k2_axis = fields.Char(string="Axis")
    doc_ker_od_k1_axl = fields.Char(string="AXL")
    doc_ker_od_k2_axl = fields.Char(string="AXL")
    doc_ker_od_k1_pciol = fields.Char(string="PCIOL")
    doc_ker_od_k2_pciol = fields.Char(string="PCIOL")
    # OS
    doc_ker_os_k1 = fields.Char(string="K1")
    doc_ker_os_k2 = fields.Char(string="K2")
    doc_ker_os_k1_axis = fields.Char(string="Axis")
    doc_ker_os_k2_axis = fields.Char(string="Axis")
    doc_ker_os_k1_axl = fields.Char(string="AXL")
    doc_ker_os_k2_axl = fields.Char(string="AXL")
    doc_ker_os_k1_pciol = fields.Char(string="PCIOL")
    doc_ker_os_k2_pciol = fields.Char(string="PCIOL")

    # Doctor Optometry VISUAL ACUITY
    doc_unaided_dist_right_id = fields.Many2one("unaided.dist.eye", "Dist. Right Eye")
    doc_unaided_dist_left_id = fields.Many2one("unaided.dist.eye", "Dist. Left Eye")
    doc_unaided_near_right_id = fields.Many2one("unaided.near.eye", "Near Right Eye")
    doc_unaided_near_left_id = fields.Many2one("unaided.near.eye", "Near Left Eye")
    doc_with_ph_right_id = fields.Many2one("unaided.dist.eye", "With PH Right Eye")
    doc_with_ph_left_id = fields.Many2one("unaided.dist.eye", "With PH Left Eye")
    doc_dist_with_exist_glass_right_id = fields.Many2one("unaided.dist.eye", "With Exist Glass Right Eye")
    doc_dist_with_exist_glass_left_id = fields.Many2one("unaided.dist.eye", "With Exist Glass Left Eye")
    doc_near_with_exist_glass_right_id = fields.Many2one("unaided.near.eye", "With Exist Glass Right Eye")
    doc_near_with_exist_glass_left_id = fields.Many2one("unaided.near.eye", "With Exist Glass Left Eye")
    
    #Tonometry
    doc_nct_od = fields.Char(string="NCT OD")
    doc_nct_os = fields.Char(string="NCT OS")
    doc_nct_machine = fields.Many2one("tcb.ophthalmology.nct.machine", string="NCT MACHINE")

    # DRY AR READINGS
    doc_ar_dry_sph_right = fields.Many2one("eye.sph", string="AR DRY SPH")
    doc_ar_dry_cyl_right = fields.Many2one("eye.cyl", string="AR DRY CYL")
    doc_ar_dry_axis_right = fields.Many2one("eye.axis", string="AR DRY AXIS")
    doc_ar_dry_status_right = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
         ('e', 'E')], string="STATUS")
    doc_ar_dry_sph_left = fields.Many2one("eye.sph", string="AR DRY SPH")
    doc_ar_dry_cyl_left = fields.Many2one("eye.cyl", string="AR DRY CYL")
    doc_ar_dry_axis_left = fields.Many2one("eye.axis", string="AR DRY AXIS")
    doc_ar_dry_status_left = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
         ('e', 'E')], string="STATUS")

    doc_ar_wet_sph_right = fields.Many2one("eye.sph", string="AR WET SPH")
    doc_ar_wet_cyl_right = fields.Many2one("eye.cyl", string="AR WET CYL")
    doc_ar_wet_axis_right = fields.Many2one("eye.axis", string="AR WET AXIS")
    doc_ar_wet_status_right = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
         ('e', 'E')], string="STATUS")
    doc_ar_wet_sph_left = fields.Many2one("eye.sph", string="AR WET SPH")
    doc_ar_wet_cyl_left = fields.Many2one("eye.cyl", string="AR WET CYL")
    doc_ar_wet_axis_left = fields.Many2one("eye.axis", string="AR WET AXIS")
    doc_ar_wet_status_left = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
         ('e', 'E')], string="STATUS")

    # POG1
    doc_pog1_sph_re = fields.Many2one("eye.sph", string="SPH RE")
    doc_pog1_ref_cyl_re = fields.Many2one("eye.cyl", string="CYL RE")
    doc_pog1_ref_axis_re = fields.Many2one("eye.axis", string="AXIS RE")
    doc_pog1_ref_add_re = fields.Many2one("eye.add", string="ADD RE")

    doc_pog1_ref_sph_le = fields.Many2one("eye.sph", string="SPH LE")
    doc_pog1_ref_cyl_le = fields.Many2one("eye.cyl", string="CYL LE")
    doc_pog1_ref_axis_le = fields.Many2one("eye.axis", string="AXIS LE")
    doc_pog1_ref_add_le = fields.Many2one("eye.add", string="ADD LE")
    doc_pog1_type = fields.Selection([('normal', 'Normal'), ('abnormal', 'Abnormal')], string="POG Type")
    doc_pog1_ref_how_old_value = fields.Char(string="How Old")
    doc_pog1_ref_how_old_select = fields.Selection([('year', 'Year'), ('years', 'Years'), ('month', 'Month'),
                                                    ('months', 'Months'), ('week', 'Week'), ('weeks', 'Weeks'),
                                                    ('day', 'Day'),
                                                    ('days', 'Days')], string="How Old Type")
    doc_pog1_ref_done_by = fields.Char(string="Done By")

    # POG2
    doc_pog2_sph_re = fields.Many2one("eye.sph", string="SPH RE")
    doc_pog2_ref_cyl_re = fields.Many2one("eye.cyl", string="CYL RE")
    doc_pog2_ref_axis_re = fields.Many2one("eye.axis", string="AXIS RE")
    doc_pog2_ref_add_re = fields.Many2one("eye.add", string="ADD RE")

    doc_pog2_ref_sph_le = fields.Many2one("eye.sph", string="SPH LE")
    doc_pog2_ref_cyl_le = fields.Many2one("eye.cyl", string="CYL LE")
    doc_pog2_ref_axis_le = fields.Many2one("eye.axis", string="AXIS LE")
    doc_pog2_ref_add_le = fields.Many2one("eye.add", string="ADD LE")
    doc_pog2_type = fields.Selection([('normal', 'Normal'), ('abnormal', 'Abnormal')], string="POG Type")
    doc_pog2_ref_how_old_value = fields.Char(string="How Old")
    doc_pog2_ref_how_old_select = fields.Selection([('year', 'Year'), ('years', 'Years'), ('month', 'Month'),
                                                    ('months', 'Months'), ('week', 'Week'), ('weeks', 'Weeks'),
                                                    ('day', 'Day'),
                                                    ('days', 'Days')], string="How Old Type")
    doc_pog2_ref_done_by = fields.Char(string="Done By")

    # Refraction
    # Dist
    doc_re_dist_va = fields.Many2one("unaided.dist.eye", "RE Dist. VA")
    doc_refraction_dist_sph_re = fields.Many2one("eye.sph", string="SPH RE")
    doc_refraction_dist_cyl_re = fields.Many2one("eye.cyl", string="CYL RE")
    doc_refraction_dist_axis_re = fields.Many2one("eye.axis", string="AXIS RE")

    doc_refraction_dist_sph_le = fields.Many2one("eye.sph", string="SPH LE")
    doc_refraction_dist_cyl_le = fields.Many2one("eye.cyl", string="CYL LE")
    doc_refraction_dist_axis_le = fields.Many2one("eye.axis", string="AXIS LE")
    doc_le_dist_va = fields.Many2one("unaided.dist.eye", "LE Dist. VA")

    # Near
    doc_re_near_va = fields.Many2one("unaided.near.eye", "RE Dist. VA")
    doc_refraction_near_sph_re = fields.Char(string="SPH RE")
    doc_refraction_near_cyl_re = fields.Many2one("eye.cyl", string="CYL RE")
    doc_refraction_near_axis_re = fields.Many2one("eye.axis", string="AXIS RE")

    doc_refraction_near_sph_le = fields.Char(string="SPH LE")
    doc_refraction_near_cyl_le = fields.Many2one("eye.cyl", string="CYL LE")
    doc_refraction_near_axis_le = fields.Many2one("eye.axis", string="AXIS LE")
    doc_le_near_va = fields.Many2one("unaided.near.eye", "LE Dist. VA")

    # Prism Values
    doc_prism_value_re = fields.Char(string="Prism Value RE")
    doc_prism_value_le = fields.Char(string="Prism Value LE")

    # Notes
    doc_optometrist_notes = fields.Text(string="OPTOMETRIST NOTES")

    #These booleans are under Refraction table - 
    optometry_change_bool = fields.Boolean(string="Change")
    optometry_accept_bool = fields.Boolean(string="Accept")   
    optometry_print_bool = fields.Boolean(string="Print")
    optometry_gp_adviced_bool = fields.Boolean(string="GP Adviced")
    
    # upper row of examination boolean fiedls 
    doc_exam_re_bool = fields.Boolean(string="RE")
    doc_exam_le_bool = fields.Boolean(string="LE")
    doc_exam_be_bool = fields.Boolean(string="BE")
    doc_exam_normal_bool = fields.Boolean(string="Normal")
    
    doc_exam_re_bool_2 = fields.Boolean(string="RE")
    doc_exam_le_bool_2 = fields.Boolean(string="LE")
    doc_exam_be_bool_2 = fields.Boolean(string="BE")
    doc_exam_normal_bool_2 = fields.Boolean(string="Normal")
    
    doc_exam_other_findings_re  = fields.Text(string="Other Findings RE")
    doc_exam_other_findings_le  = fields.Text(string="Other Findings LE")
    # For Allergy in doctor screen of examination 
    doc_allergy_ids = fields.One2many("tcb.ophthalmology.allergy", "ophthalmology_id", string="Allergies")
    
    # def submit_refractive_readings_to_doctor_optometry(self):
    #     self.doc_ker_od_k1 = self.ker_od_k1
    #     self.doc_ker_od_k2 = self.ker_od_k2
    #     self.doc_ker_od_k1_axis = self.ker_od_k1_axis
    #     self.doc_ker_od_k2_axis = self.ker_od_k2_axis
    #     self.doc_ker_od_k1_axl = self.ker_od_k1_axl
    #     self.doc_ker_od_k2_axl = self.ker_od_k2_axl
    #     self.doc_ker_od_k1_pciol = self.ker_od_k1_pciol
    #     self.doc_ker_od_k2_pciol = self.ker_od_k2_pciol
    #     self.doc_ker_os_k1 = self.ker_os_k1
    #     self.doc_ker_os_k2 = self.ker_os_k2
    #     self.doc_ker_os_k1_axis = self.ker_os_k1_axis
    #     self.doc_ker_os_k2_axis = self.ker_os_k2_axis
    #     self.doc_ker_os_k1_axl = self.ker_os_k1_axl
    #     self.doc_ker_os_k2_axl = self.ker_os_k2_axl
    #     self.doc_ker_os_k1_pciol = self.ker_os_k1_pciol
    #     self.doc_ker_os_k2_pciol = self.ker_os_k2_pciol
    #     self.doc_unaided_dist_right_id = self.unaided_dist_right_id.id
    #     self.doc_unaided_dist_left_id = self.unaided_dist_left_id.id
    #     self.doc_unaided_near_right_id = self.unaided_near_right_id.id
    #     self.doc_unaided_near_left_id = self.unaided_near_left_id.id
    #     self.doc_with_ph_right_id = self.with_ph_right_id.id
    #     self.doc_with_ph_left_id = self.with_ph_left_id.id
    #     self.doc_dist_with_exist_glass_right_id = self.dist_with_exist_glass_right_id.id
    #     self.doc_dist_with_exist_glass_left_id = self.dist_with_exist_glass_left_id.id
    #     self.doc_near_with_exist_glass_right_id = self.near_with_exist_glass_right_id.id
    #     self.doc_near_with_exist_glass_left_id = self.near_with_exist_glass_left_id.id
    #     self.doc_nct_od = self.nct_od
    #     self.doc_nct_os = self.nct_os
    #     self.doc_nct_machine = self.nct_machine.id
    #     self.doc_ar_dry_sph_right = self.ar_dry_sph_right.id
    #     self.doc_ar_dry_cyl_right = self.ar_dry_cyl_right.id
    #     self.doc_ar_dry_axis_right = self.ar_dry_axis_right.id
    #     self.doc_ar_dry_status_right = self.ar_dry_status_right
    #     self.doc_ar_dry_sph_left = self.ar_dry_sph_left.id
    #     self.doc_ar_dry_cyl_left = self.ar_dry_cyl_left.id
    #     self.doc_ar_dry_axis_left = self.ar_dry_axis_left.id
    #     self.doc_ar_dry_status_left = self.ar_dry_status_left
    #     self.doc_ar_wet_sph_right = self.ar_wet_sph_right.id
    #     self.doc_ar_wet_cyl_right = self.ar_wet_cyl_right.id
    #     self.doc_ar_wet_axis_right = self.ar_wet_axis_right.id
    #     self.doc_ar_wet_status_right = self.ar_wet_status_right
    #     self.doc_ar_wet_sph_left = self.ar_wet_sph_left.id
    #     self.doc_ar_wet_cyl_left = self.ar_wet_cyl_left.id
    #     self.doc_ar_wet_axis_left = self.ar_wet_axis_left.id
    #     self.doc_ar_wet_status_left = self.ar_wet_status_left
    #     self.doc_pog1_sph_re = self.pog1_sph_re.id
    #     self.doc_pog1_ref_cyl_re = self.pog1_ref_cyl_re.id
    #     self.doc_pog1_ref_axis_re = self.pog1_ref_axis_re.id
    #     self.doc_pog1_ref_add_re = self.pog1_ref_add_re.id
    #     self.doc_pog1_ref_sph_le = self.pog1_ref_sph_le.id
    #     self.doc_pog1_ref_cyl_le = self.pog1_ref_cyl_le.id
    #     self.doc_pog1_ref_axis_le = self.pog1_ref_axis_le.id
    #     self.doc_pog1_ref_add_le = self.pog1_ref_add_le.id
    #     self.doc_pog1_type = self.pog1_type
    #     self.doc_pog1_ref_how_old_value = self.pog1_ref_how_old_value
    #     self.doc_pog1_ref_how_old_select = self.pog1_ref_how_old_select
    #     self.doc_pog1_ref_done_by = self.pog1_ref_done_by
    #     self.doc_pog2_sph_re = self.pog2_sph_re.id
    #     self.doc_pog2_ref_cyl_re = self.pog2_ref_cyl_re.id
    #     self.doc_pog2_ref_axis_re = self.pog2_ref_axis_re.id
    #     self.doc_pog2_ref_add_re = self.pog2_ref_add_re.id
    #     self.doc_pog2_ref_sph_le = self.pog2_ref_sph_le.id
    #     self.doc_pog2_ref_cyl_le = self.pog2_ref_cyl_le.id
    #     self.doc_pog2_ref_axis_le = self.pog2_ref_axis_le.id
    #     self.doc_pog2_ref_add_le = self.pog2_ref_add_le.id
    #     self.doc_pog2_type = self.pog2_type
    #     self.doc_pog2_ref_how_old_value = self.pog2_ref_how_old_value
    #     self.doc_pog2_ref_how_old_select = self.pog2_ref_how_old_select
    #     self.doc_pog2_ref_done_by = self.pog2_ref_done_by
    #     self.doc_re_dist_va = self.re_dist_va_last.id
    #     self.doc_refraction_dist_sph_re = self.refraction_dist_sph_re_last.id
    #     self.doc_refraction_dist_cyl_re = self.refraction_dist_cyl_re_last.id
    #     self.doc_refraction_dist_axis_re = self.refraction_dist_axis_re_last.id
    #     self.doc_refraction_dist_sph_le = self.refraction_dist_sph_le_last.id
    #     self.doc_refraction_dist_cyl_le = self.refraction_dist_cyl_le_last.id
    #     self.doc_refraction_dist_axis_le = self.refraction_dist_axis_le_last.id
    #     self.doc_le_dist_va = self.le_dist_va_last.id
    #     self.doc_re_near_va = self.re_near_va_last.id
    #     self.doc_refraction_near_sph_re = self.refraction_near_sph_re_last
    #     self.doc_refraction_near_cyl_re = self.refraction_near_cyl_re_last.id
    #     self.doc_refraction_near_axis_re = self.refraction_near_axis_re_last.id
    #     self.doc_refraction_near_sph_le = self.refraction_near_sph_le_last
    #     self.doc_refraction_near_cyl_le = self.refraction_near_cyl_le_last.id
    #     self.doc_refraction_near_axis_le = self.refraction_near_axis_le_last.id
    #     self.doc_le_near_va = self.le_near_va_last.id
    #     self.doc_prism_value_re = self.prism_value_re
    #     self.doc_prism_value_le = self.prism_value_le
    #     self.doc_presenting_complaints = self.presenting_complaint
    #     self.doc_past_history = self.get_eye_past_history()
    #     self.doc_ophthalmic_complaints = self.get_eye_ophthalmic_complaints()
    #     self.doc_systemic_illness = self.get_eye_systematic_illness()
        # self.state = 'submitted'

    # def get_eye_past_history(self):
    #     past_history_text = ""
    #     i = 0
    #     for past in self.past_history_ids:
    #         if i == 0:
    #             past_history_text += past.past_history.name + " - " + dict(past._fields['eye'].selection).get(
    #                 past.eye) + " - " + past.duration
    #         else:
    #             past_history_text += "\n" + past.past_history.name + " - " + dict(past._fields['eye'].selection).get(
    #                 past.eye) + " - " + past.duration
    #         i += 1
    #     return past_history_text

    # def get_eye_ophthalmic_complaints(self):
    #     ophthalmic_complaints_text = ""
    #     j = 0
    #     for lev in self.level_ids:
    #         if j == 0:
    #             ophthalmic_complaints_text += lev.complaints.name + " - " + dict(lev._fields['eye'].selection).get(
    #                 lev.eye) + " - " + lev.duration
    #         else:
    #             ophthalmic_complaints_text += "\n" + lev.complaints.name + " - " + dict(
    #                 lev._fields['eye'].selection).get(lev.eye) + " - " + lev.duration
    #         j += 1
    #     return ophthalmic_complaints_text

    # def get_eye_systematic_illness(self):
    #     systematic_illness_text = ""
    #     k = 0
    #     for sy in self.systematic_illness_ids:
    #         if k == 0:
    #             systematic_illness_text += sy.disease_id.name + " - " + sy.status_id.name + " - " + sy.duration
    #         else:
    #             systematic_illness_text += "\n" + sy.disease_id.name + " - " + sy.status_id.name + " - " + sy.duration
    #         k += 1
    #     return systematic_illness_text


class SltechEyeAdd(models.Model):
    _name = "tcb.ophthalmology.allergy"

    name = fields.Char(string="Name")
    ophthalmology_id = fields.Many2one('tcb.ophthalmology.evaluation', string="Ophthalmology Id")
