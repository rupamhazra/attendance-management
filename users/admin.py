from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import *
from users.forms import CustomUserCreationForm

# Register your models here.
class CustomUserAdmin(UserAdmin):
	model = UserDetail
	add_form = CustomUserCreationForm

	fieldsets = (
		*UserAdmin.fieldsets,
		(
			'User Details',
			{
				'fields':(
					'name',
                    'card_no',
                    'guardian_name',
                    'relationship',
                    'emergency_contact_person_name_1',
                    'relationship_with_person_1',
                    'emergency_contact_person_contact_1',
                    'emergency_contact_person_name_2',
                    'relationship_with_person_2',
                    'emergency_contact_person_contact_2',
                    'company',
                    'department',
                    'category',
                    'grade',
                    'reporting_head',
                    'profile_img',
                    'signature',
                    'visitor_permission',
                    'esic_no',
                    'pf_no',
                    'ctc',
                    'sap_personnel_no',
                    'dob',
                    'joining_date',
                    'marital_status',
                    'blood_group',
                    'highest_qualification_type',
                    'highest_qualification',
                    'experience',
                    'designation',
                    'gender',
                    'official_email',
                    'bus_route',
                    'vehicle',
                    'eid_no',
                    'aadhar_no',
                    'pan_no',
                    'pan_card_pic',
                    'aadhar_card_pic',
                    'permanent_address',
                    'permanent_pincode',
                    'temporary_address',
                    'temporary_pincode',
                    'phone_no',
                    'bank_account',
                    'ifsc_code',
                    'passbook_pic',
                    'permissible_late_arrival',
                    'permissible_early_departure',
                    'maximum_working_hours',
                    'outpass_duration',
                    'outpass_frequency',
                    'round_the_clock_working',
                    'maximum_ot_allowed',
                    'consider_time_loss',
                    'half_day_marking',
                    'maximum_absent_hours_for_half_day',
                    'minimum_absent_hours_for_half_day',
                    'present_marking_duration',
                    'punches_required_in_a_day',
                    'overtime_applicable',
                    'half_day_on_late_early_field',
                    'limit_for_half_day_on_late',
                    'limit_for_half_day_on_early',
                    'shift',
                    'define_probation_period_of_the_employee',
                    'define_notice_period_for_the_employee',
                    'define_skill',
                    'change_pass',
                    'password_to_know',
                    'is_hod',
                    'created_by',
                    'created_at',
                    'updated_at',
                    'updated_by'
				)
			}
		)
	)

@admin.register(UserDetail)
class UserDetail(CustomUserAdmin):
    list_display = ['username','first_name','last_name','is_active']
    search_fields = ('username',)

@admin.register(LoginLogoutLog)
class LoginLogoutLog(admin.ModelAdmin):
    list_display = [field.name for field in LoginLogoutLog._meta.fields]
    search_fields = ('user__username', 'ip_address', 'browser_name', 'os_name')

#admin.site.register(User)