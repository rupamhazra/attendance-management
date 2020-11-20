from django.contrib import admin

from hrms.models import *


@admin.register(HrmsMachineMaster)
class HrmsMachineMaster(admin.ModelAdmin):
    list_display = [field.name for field in HrmsMachineMaster._meta.fields]
    search_fields = ('machine_id',)


@admin.register(HrmsShiftMaster)
class HrmsShiftMaster(admin.ModelAdmin):
    list_display = [field.name for field in HrmsShiftMaster._meta.fields]
    search_fields = ('shift_code',)


@admin.register(HrmsBusRouteMaster)
class HrmsBusRouteMaster(admin.ModelAdmin):
    list_display = [field.name for field in HrmsBusRouteMaster._meta.fields]
    search_fields = ('route_name', 'route_no',)


@admin.register(HrmsVehicleMaster)
class HrmsVehicleMaster(admin.ModelAdmin):
    list_display = [field.name for field in HrmsVehicleMaster._meta.fields]
    search_fields = ('vehicle_no',)


@admin.register(HrmsHolidayMaster)
class HrmsHolidayMaster(admin.ModelAdmin):
    list_display = [field.name for field in HrmsHolidayMaster._meta.fields]
    search_fields = ('holiday',)


@admin.register(HrmsLeaveMaster)
class HrmsLeaveMaster(admin.ModelAdmin):
    list_display = [field.name for field in HrmsLeaveMaster._meta.fields]
    search_fields = ('leave_code', 'description',)


@admin.register(HrmsGradeLeaveMapping)
class HrmsGradeLeaveMapping(admin.ModelAdmin):
    list_display = [field.name for field in HrmsGradeLeaveMapping._meta.fields]


@admin.register(HrmsUserLeaveMapping)
class HrmsUserLeaveMapping(admin.ModelAdmin):
    list_display = [field.name for field in HrmsUserLeaveMapping._meta.fields]

@admin.register(HrmsAttendance)
class HrmsAttendance(admin.ModelAdmin):
    list_display = [field.name for field in HrmsAttendance._meta.fields]

@admin.register(HrmsApprovalConfiguration)
class HrmsApprovalConfiguration(admin.ModelAdmin):
    list_display = [field.name for field in HrmsApprovalConfiguration._meta.fields]

@admin.register(HrmsApprovalRequest)
class HrmsApprovalRequest(admin.ModelAdmin):
    list_display = [field.name for field in HrmsApprovalRequest._meta.fields]

@admin.register(HrmsApproval)
class HrmsApproval(admin.ModelAdmin):
    list_display = [field.name for field in HrmsApproval._meta.fields]

@admin.register(HrmsApprovalRequestDocument)
class HrmsApprovalRequestDocument(admin.ModelAdmin):
    list_display = [field.name for field in HrmsApprovalRequestDocument._meta.fields]


