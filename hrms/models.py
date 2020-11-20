from django.db import models
#from django.contrib.auth.models import settings.AUTH_USER_MODEL
#from users.models import UserDetails
from master.models import *
from datetime import datetime
from django.conf import settings
from dynamic_media import get_directory_path


class CustomManager(models.Manager):
    def get_queryset(self):
        return super(__class__, self).get_queryset().filter(is_deleted=False)

class DeleteBaseAbstractStructure(models.Model):
    is_deleted = models.BooleanField(default=False)

    objects = models.Manager()
    cmobjects = CustomManager()
    class Meta:
        abstract = True
    
class CreateBaseAbstractStructure(DeleteBaseAbstractStructure):
    created_at = models.DateTimeField(default=datetime.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    class Meta:
        abstract = True 

class UpdateBaseAbstractStructure(CreateBaseAbstractStructure):
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

class BaseAbstractStructure(UpdateBaseAbstractStructure):
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    # def save(self, *args, **kwargs):
    #     self.updated_at = datetime.now()
    #     super(__class__, self).save(*args, **kwargs)


class HrmsMachineMaster(BaseAbstractStructure):
    GATE_CHOICE = (
        ('entry_gate', 'entry_gate'),
        ('exit_gate', 'exit_gate')
    )
    USED_FOR_CHOICE = (
        ('attendance', 'attendance'),
        ('access', 'access')
    )
    machine_id = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='mac_company')
    gate = models.CharField(default='entry_gate', choices=GATE_CHOICE, max_length=100)
    used_for = models.CharField(default='attendance', choices=USED_FOR_CHOICE, max_length=100)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_machine_master'

class HrmsShiftMaster(BaseAbstractStructure):
    SHIFT_POSITION_CHOICE = (
        ('day', 'day'),
        ('night', 'night'),
        ('half', 'half')
    )
    shift_code = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='shift_company')
    start_time = models.TimeField()
    end_time = models.TimeField()
    min_working_hours = models.TimeField()
    lunch_start_time = models.TimeField(null=True)
    lunch_end_time = models.TimeField(null=True)
    lunch_deduction = models.BooleanField(default=False)
    is_flexible_lunch_hours = models.BooleanField(default=False)
    overtime_deduct_after = models.TimeField(null=True)
    overtime_start_after = models.TimeField(null=True)
    overtime_deduction = models.BooleanField(default=False)
    shift_position = models.CharField(default='day', choices=SHIFT_POSITION_CHOICE, max_length=100)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_shift_master'

class HrmsBusRouteMaster(BaseAbstractStructure):
    route_no = models.CharField(max_length=10)
    route_name = models.CharField(max_length=255)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_bus_route_master'

class HrmsVehicleMaster(BaseAbstractStructure):
    vehicle_no = models.CharField(max_length=10)
    bus_route = models.ForeignKey(HrmsBusRouteMaster, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_vehicle_master'

class HrmsLeaveMaster(BaseAbstractStructure):
    LEAVE_TYPE_CHOICE = (
        ('L', 'L'),
        ('A', 'A'),
        ('P', 'P')
    )
    ACC_TYPE_CHOICES = (
        ('M', 'M'),
        ('Y', 'Y')
    )
    leave_code = models.CharField(max_length=5)
    description = models.CharField(max_length=50)
    is_off_include = models.BooleanField(default=False)
    is_holiday_include = models.BooleanField(default=False)
    is_leave_accural = models.BooleanField(default=False)
    leave_type = models.CharField(choices=LEAVE_TYPE_CHOICE, default='L', max_length=2)
    smin = models.FloatField(null=True)
    smax = models.FloatField(null=True)
    present = models.FloatField(null=True)
    leave = models.FloatField(null=True)
    leave_limit = models.FloatField(null=True)
    fixed = models.BooleanField(default=False)
    leave_post = models.BooleanField(default=False)
    acc_type = models.CharField(choices=ACC_TYPE_CHOICES, default='Y', max_length=2)
    rate_pm = models.FloatField(null=True)
    eligibility = models.FloatField(null=True)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_leave_master'

class HrmsHolidayMaster(BaseAbstractStructure):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='holiday_company', blank=True, null=True)
    holiday_date = models.DateField()
    holiday = models.CharField(max_length=25)
    adjustment_date = models.DateField(null=True)
    ot_factor = models.FloatField(default=0)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_holiday_master'

class HrmsGradeLeaveMapping(BaseAbstractStructure):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='grade_leave_grade', blank=True, null=True)
    # designation = models.ForeignKey(Designation, on_delete=models.CASCADE, related_name='grade_leave_designation', blank=True, null=True)
    year = models.IntegerField()
    leave_master = models.ForeignKey(HrmsLeaveMaster, on_delete=models.CASCADE, related_name='grade_leave_leave_master', blank=True, null=True)
    quantity = models.FloatField()
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_grade_leave_mapping'

class HrmsUserLeaveMapping(DeleteBaseAbstractStructure):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_leave_grade', blank=True, null=True)
    year = models.IntegerField()
    leave_master = models.ForeignKey(HrmsLeaveMaster, on_delete=models.CASCADE, related_name='user_leave_leave_master', blank=True, null=True)
    quantity = models.FloatField()
    is_deleted = models.BooleanField(default=False, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_user_leave_mapping'


# Attendance #
class HrmsAttendance(CreateBaseAbstractStructure):
    employee=models.ForeignKey(settings.AUTH_USER_MODEL,related_name='user_att_employee_id',
                                   on_delete=models.CASCADE,blank=True,null=True)
    date = models.DateTimeField(auto_now_add=False,blank=True, null=True)
    login_time = models.DateTimeField(blank=True, null=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    is_present = models.BooleanField(default=False)
    day_remarks = models.CharField(max_length=100, blank=True, null=True)
    

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_attendance' 

# Start Approval #

class HrmsApprovalConfiguration(BaseAbstractStructure):
    SECTION_CHOICE = (
        ('Leave', 'Leave'),
        ('Tours', 'Tours'),
        ('Get Pass', 'Get Pass'),
        ('Over Time', 'Over Time'),
        ('Canteen Punch', 'Canteen Punch'),
        ('Miss Punch', 'Miss Punch'),
        ('Card Replacement', 'Card Replacement'),
        ('Uniform Change', 'Uniform Change'),
        ('W/O Change', 'W/O Change'),
        ('Shift Change', 'Shift Change'),
        ('C-off', 'C-off'),
    )
    APPROVAL_TYPE = (
        ('Approval', 'Approval'),
        ('Post', 'Post')
    )
    approval_section = models.CharField(choices=SECTION_CHOICE, default='Leave', max_length=30)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='section_employee', blank=True, null=True)
    level = models.IntegerField()
    type = models.CharField(choices=APPROVAL_TYPE, default='Approval', max_length=15)
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='section_approver', blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_approval_configuration'

class HrmsApprovalRequest(UpdateBaseAbstractStructure):
    SECTION_CHOICE = (
        ('Leave', 'Leave'),
        ('Tours', 'Tours'),
        ('Get Pass', 'Get Pass'),
        ('Over Time', 'Over Time'),
        ('Canteen Punch', 'Canteen Punch'),
        ('Miss Punch', 'Miss Punch'),
        ('Card Replacement', 'Card Replacement'),
        ('Uniform Change', 'Uniform Change'),
        ('W/O Change', 'W/O Change'),
        ('Shift Change', 'Shift Change'),
        ('C-off', 'C-off'),
    )
    STATUS_TYPE = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    )

    #For Gate Pass
    GATE_TYPE_CHOICE = (
        ('Entry gate', 'Entry gate'),
        ('Exit gate', 'Exit gate')
    )
    

    DAYS = (
        ('SUNDAY','SUNDAY'),
        ('MONDAY','MONDAY'),
        ('TUESDAY','TUESDAY'),
        ('WEDNESDAY','WEDNESDAY'),
        ('THURSDAY','THURSDAY'),
        ('SATURDAY','SATURDAY'),
    )

    SHIFT_TYPE = (
        ('Rotational','Rotational'),
        ('Fixed','Fixed'),
    )

    approval_section = models.CharField(choices=SECTION_CHOICE, max_length=30, blank=True,null=True)
    attendance = models.ForeignKey(HrmsAttendance, on_delete=models.CASCADE, related_name='request_attendance', blank=True, null=True)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='request_employee', blank=True, null=True)
    voucher_no = models.CharField(max_length=30,blank=True,null=True)
    reason = models.CharField(max_length=80,blank=True,null=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    leave_code = models.ForeignKey(HrmsLeaveMaster, related_name='approval_request_leave',on_delete=models.CASCADE, blank=True, null=True)
    # [Tour]
    total_amount = models.FloatField(blank=True,null=True)
    from_address = models.TextField(blank=True,null=True)
    to_address = models.TextField(blank=True,null=True)
    # [For Miss Punch and Canteen Punch]
    punch_time = models.DateTimeField(blank=True, null=True) 
    # [Over Time]
    applicable_over_time_duration = models.TimeField(blank=True,null=True) #For Over Time

    # [Gate Pass]
    request_time = models.DateTimeField(blank=True,null=True)
    gate_type = models.CharField(choices=GATE_TYPE_CHOICE, max_length=30,blank=True,null=True)

    # [W/O Change Application]
    current_weekly_off = models.CharField(choices=DAYS, max_length=15, null=True,blank=True)
    desired_weekly_off = models.CharField(choices=DAYS, max_length=15, null=True,blank=True)

    # [Shift change Application]
    current_shift_type = models.CharField(choices=SHIFT_TYPE, max_length=20, blank=True,null=True)
    current_shift_pattern = models.TextField(blank=True,null=True)
    shift_remaining_days = models.IntegerField(blank=True,null=True)
    current_shift_change_after_how_many_days = models.IntegerField(blank=True,null=True)
    current_shift_end_time =   models.DateTimeField(blank=True,null=True)
    current_shift_hrs = models.TimeField(blank=True,null=True)
    shift_change_from =  models.DateField(blank=True,null=True)

    desired_shift_type = models.CharField(choices=SHIFT_TYPE, max_length=20, blank=True,null=True)
    desired_shift_pattern = models.TextField(blank=True,null=True)
    desired_shift_change_after_how_many_days =  models.IntegerField(blank=True,null=True)
    desired_shift_start_time =  models.DateTimeField(blank=True,null=True)
    desired_shift_end_time = models.DateTimeField(blank=True,null=True)
    desired_shift_hrs = models.TimeField(blank=True,null=True)

    # [Approval]
    status = models.CharField(choices=STATUS_TYPE, default='Pending', max_length=15)
    current_level = models.IntegerField(default=1,blank=True,null=True)
    current_approval_configuration = models.ForeignKey(HrmsApprovalConfiguration, on_delete=models.CASCADE, related_name='request_approval_conf', blank=True, null=True)
    
    super_admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='request_super_admin', blank=True, null=True) 
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_approval_request'

class HrmsApproval(UpdateBaseAbstractStructure):
    approval_type = (
        ('Pending','Pending'),
        ('Rejected', 'Rejected'),
        ('Approved', 'Approved'),
        )
    approval_request = models.ForeignKey(HrmsApprovalRequest, related_name='approval_status_request',on_delete=models.CASCADE, blank=True, null=True)
    approval_configuration = models.ForeignKey(HrmsApprovalConfiguration, related_name='approval_status_approvals_user_level',on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=30,choices=approval_type, null=True, blank=True,default='Pending')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_approval'

class HrmsApprovalRequestDocument(DeleteBaseAbstractStructure):
    approval_request = models.ForeignKey(HrmsApprovalRequest, related_name='approval_doc',on_delete=models.CASCADE, blank=True, null=True)
    doc_name = models.CharField(max_length=200,null=True, blank=True)
    doc = models.FileField(upload_to=get_directory_path,blank=True,null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_approval_request_document'

# End Approval #