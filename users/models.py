from django.db import models
#from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from validators import validate_file_extension
from django.utils import timezone
import uuid
from datetime import datetime
from master.models import ModuleUser, Designation, Grade, Company, Category, Department
import collections
from hrms.models import HrmsShiftMaster, HrmsVehicleMaster, HrmsBusRouteMaster
from django.conf import settings

from django.contrib.auth.models import AbstractUser

class UserDetail(AbstractUser):

    GENDER_CHOICE = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        )
    RELATIONSHIP_WITH_PERSON_CHOICE = (
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Husband', 'Husband'),
        ('Wife', 'Wife'),
        ('Spouse', 'Spouse'),
        ('Other', 'Other'),
        )
    RELATIONSHIP_CHOICE = (
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Husband', 'Husband'),
        ('Wife', 'Wife'),
        ('Spouse', 'Spouse'),
        ('Other', 'Other'),
        )
    MARTIAL_STATUS_TYPE=(
        ('Married','Married'),
        ('Single','Single'),
        )
    BLOOD_GROUP_TYPE=(
        ('A+','A+'),
        ('A-','A-'),
        ('B+','B+'),
        ('B-','B-'),
        ('O+','O+'),
        ('O-','O-'),
        ('AB+','AB+'),
        ('AB-','AB-')
        )

    QALIFICATION_TYPE=(
        ('Secondary','Secondary'),
        ('H.S','H.S'),
        ('Graduate','Graduate'),
        ('Post Graduate','Post Graduate'),
        ('Other','Other'),
        )
    
    EXPERIENCE_TYPE=(
        ('0-1 year','0-1 year'),
        ('1-2 year','1-2 year'),
        ('2-3 year','2-3 year'),
        ('3-4 year','3-4 year'),
        ('4-5 year','4-5 year'),
        ('5-6 year','5-6 year'),
        ('6-7 year','6-7 year'),
        ('7-8 year','7-8 year'),
        ('8-9 year','8-9 year'),
        ('9-10 year','9-10 year'),
        ('10-11 year','10-11 year'),
        ('11-12 year','11-12 year'),
        ('12-13 year','12-13 year'),
        ('13-14 year','13-14 year'),
        ('14-15 year','14-15 year'),
        ('15-16 year','15-16 year'),
        ('16-17 year','16-17 year'),
        ('17-18 year','17-18 year'),
        ('18-19 year','19-19 year'),
        ('19-20 year','19-20 year'),
        ('20+ year','20+ year'),
        )

    NOTICE_PERIOD_TYPE=(
        ('1 month','1 month'),
        ('2 month','2 month'),
        ('3 month','3 month'),
        ('5 month','5 month'),
        ('6 month','6 month'),
        )
    
    PROBATION_PERIOD_TYPE=(
        ('1 month','1 month'),
        ('2 month','2 month'),
        ('3 month','3 month'),
        ('5 month','5 month'),
        ('6 month','6 month'),
        ('7 month','7 month'),
        ('8 month','8 month'),
        ('9 month','9 month'),
        ('10 month','10 month'),
        ('11 month','11 month'),
        ('12 month','12 month'),
        )
    
    PUNCHES_REQUIRED_IN_A_DAY_TYPE = (
        ('No Punch','No Punch'),
        ('Single Punch','Single Punch'),
        ('Two Punches','Two Punches'),
        ('Four Punches','5 Punches'),
        ('Multiple Punches','6 Punches'),
    )
    BOOLEAN_CHOICE = (
        (1,1),
        (0,0)
    )
    SHIFT_TYPE = (
        ('Rotational','Rotational'),
        ('Fixed','Fixed'),
    )
    name = models.CharField(max_length = 100, blank=True,null=True)                             
    # Offcial Details
    card_no  = models.CharField(max_length=50, blank=True, null=True)
    guardian_name =  models.CharField(max_length=50, blank=True, null=True)
    relationship = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_person_name_1 = models.CharField(max_length=50, blank=True, null=True)
    relationship_with_person_1 = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_person_contact_1 = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_person_name_2 = models.CharField(max_length=50, blank=True, null=True)
    relationship_with_person_2 = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_person_contact_2 = models.CharField(max_length=15, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_master',blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_master',blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_master',blank=True, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='grade',
                              blank=True, null=True)
    reporting_head = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_re_head',
                                   blank=True, null=True)
    profile_img = models.FileField(upload_to=get_directory_path, blank=True,null=True)
    signature = models.ImageField(upload_to=get_directory_path, blank=True,null=True)
    visitor_permission = models.BooleanField(choices=BOOLEAN_CHOICE,max_length=2, blank=True, null=True)
    esic_no = models.CharField(max_length = 25, blank=True,null=True) # default 'xxxxxxxxxx' 
    pf_no = models.CharField(max_length = 25, blank=True,null=True) # default 'XX/XXX/999999/999999'
    ctc = models.FloatField(blank=True,null=True)
    sap_personnel_no=models.CharField(max_length = 200, blank=True, null=True)

    # Personal Details
    dob = models.DateField(max_length=8, default=None, blank=True, null=True)
    joining_date = models.DateTimeField(blank=True, null=True)
    marital_status = models.CharField(choices =MARTIAL_STATUS_TYPE,max_length = 15,blank=True,null=True)
    blood_group=models.CharField(choices =BLOOD_GROUP_TYPE,max_length = 10,blank=True,null=True)
    highest_qualification_type = models.CharField(choices =QALIFICATION_TYPE,max_length = 15,blank=True,null=True)
    highest_qualification = models.CharField(max_length = 100,blank=True,null=True)
    experience = models.CharField(choices = EXPERIENCE_TYPE,max_length = 15,blank=True,null=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, related_name='designation',
                                    blank=True, null=True)
    gender = models.CharField(choices=GENDER_CHOICE,max_length=10, blank=True, null=True)
    official_email = models.EmailField(max_length=70, blank=True, null=True)
    bus_route = models.ForeignKey(HrmsBusRouteMaster, on_delete=models.CASCADE, related_name='bus_route_master',
                                blank=True, null=True)
    vehicle = models.ForeignKey(HrmsVehicleMaster, on_delete=models.CASCADE, related_name='vehicle_master',
                                blank=True, null=True)
    eid_no = models.CharField(max_length=30, blank=True, null=True)
    aadhar_no = models.CharField(max_length=12, blank=True, null=True)
    pan_no = models.CharField(max_length=12, blank=True, null=True)
    pan_card_pic = models.ImageField(upload_to=get_directory_path, blank=True,null=True)
    aadhar_card_pic = models.ImageField(upload_to=get_directory_path, blank=True,null=True)
    permanent_address = models.TextField(blank=True, null=True)
    permanent_pincode = models.CharField(max_length=10, blank=True, null=True)
    temporary_address = models.TextField(blank=True, null=True)
    temporary_pincode = models.CharField(max_length=10, blank=True, null=True)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    bank_account = models.CharField(max_length=15, blank=True, null=True)
    ifsc_code = models.CharField(max_length=15, blank=True, null=True)
    passbook_pic = models.ImageField(upload_to=get_directory_path, blank=True,null=True)

    # Time Office Policy
    permissible_late_arrival = models.TimeField(blank=True,null=True)
    permissible_early_departure = models.TimeField(blank=True,null=True)
    maximum_working_hours = models.TimeField(blank=True,null=True)
    outpass_duration = models.TimeField(blank=True,null=True)
    outpass_frequency = models.CharField(max_length=100, blank=True, null=True)
    round_the_clock_working = models.BooleanField(choices=BOOLEAN_CHOICE,max_length=2, blank=True, null=True)
    maximum_ot_allowed = models.TimeField(blank=True,null=True)
    consider_time_loss = models.BooleanField(choices=BOOLEAN_CHOICE,max_length=2, blank=True, null=True)
    half_day_marking = models.BooleanField(choices=BOOLEAN_CHOICE,max_length=2, blank=True, null=True)
    maximum_absent_hours_for_half_day = models.TimeField(blank=True,null=True)
    minimum_absent_hours_for_half_day = models.TimeField(blank=True,null=True)
    present_marking_duration = models.TimeField(blank=True,null=True)
    punches_required_in_a_day = models.CharField(choices=PUNCHES_REQUIRED_IN_A_DAY_TYPE,max_length=30, blank=True, null=True)
    overtime_applicable = models.BooleanField(choices=BOOLEAN_CHOICE,max_length=2, blank=True, null=True)
    half_day_on_late_early_field = models.BooleanField(choices=BOOLEAN_CHOICE,max_length=2, blank=True, null=True)
    limit_for_half_day_on_late = models.TimeField(blank=True,null=True)
    limit_for_half_day_on_early = models.TimeField(blank=True,null=True)

    # Shift Policy
    shift_type = models.CharField(choices=SHIFT_TYPE, max_length=20, blank=True,null=True)
    shift = models.ForeignKey(HrmsShiftMaster, on_delete=models.CASCADE, related_name='shift_master',blank=True, null=True)
    shift_pattern = models.TextField(blank=True,null=True)

    #Other information
    define_probation_period_of_the_employee = models.CharField(choices=PROBATION_PERIOD_TYPE,max_length=30, blank=True, null=True)
    define_notice_period_for_the_employee = models.CharField(choices=NOTICE_PERIOD_TYPE,max_length=30, blank=True, null=True)
    define_skill = models.TextField(blank=True, null=True)

    # Extra for our
    change_pass = models.BooleanField(default=True)
    password_to_know = models.CharField(max_length=200, blank=True, null=True)
    is_hod = models.BooleanField(choices=BOOLEAN_CHOICE,max_length=2, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='u_created_by',
                                   blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='u_updated_by',
                                   blank=True, null=True)

    def __str__(self):
        return str(self.id)

    # class Meta:
    #     db_table = 'user_details'

    def applications(self):
        app_list = []
        try:
            mmr_detalis = ModuleRoleUser.objects.filter(mmr_user_id=self.user_id)
            if mmr_detalis:
                for mmr_data in mmr_detalis:
                    mmr_odict = collections.OrderedDict()
                    #print("mmr_data: ", mmr_data.mmr_permissions)
                    if mmr_data.mmr_type:
                        mmr_odict['mmr_type'] = mmr_data.mmr_type
                    else:
                        mmr_odict['mmr_type'] = None

                    if mmr_data.mmr_module:
                        mmr_odict['mmr_module'] = {
                            "id": mmr_data.mmr_module.id,
                            "cm_name": mmr_data.mmr_module.cm_name
                        }
                    else:
                        mmr_odict['mmr_module'] = dict()

                    if mmr_data.mmr_role:
                        mmr_odict['mmr_role'] = {
                            "cr_name": mmr_data.mmr_role.cr_name,
                        }
                    else:
                        mmr_odict['mmr_role'] = dict()
                    app_list.append(mmr_odict)
            else:
                app_list = list()
            return app_list
        except Exception as e:
            raise e
      

class LoginLogoutLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(auto_now=False, blank=True, null=True)
    browser_name = models.CharField(max_length=255, blank=True, null=True)
    os_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'log_login_logout'


