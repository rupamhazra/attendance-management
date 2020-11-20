from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from hrms.models import *
from users.models import UserDetail
from django.contrib.auth.models import *
from datetime import datetime
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction, IntegrityError
import global_function as gf


class HrmsMachineMasterSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    company_details = serializers.SerializerMethodField()

    class Meta:
        model = HrmsMachineMaster
        fields = ('__all__')

    def create(self, validated_data):
        with transaction.atomic():
            validated_data.pop('updated_by')
            validated_data.pop('updated_at')
            validated_data['created_by'] = self.context['request'].user
            instance = HrmsMachineMaster.objects.create(**validated_data)
            return instance

    def get_company_details(self, instance):
        return {
            'company_id': instance.company.id,
            'company_code': instance.company.code,
            'company_name': instance.company.name
        }


class HrmsShiftMasterSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    total_users = serializers.SerializerMethodField()
    company_details = serializers.SerializerMethodField()

    class Meta:
        model = HrmsShiftMaster
        fields = ('__all__')

    def get_total_users(self, instance):
        return UserDetail.objects.filter(shift=instance).count()

    def create(self, validated_data):
        with transaction.atomic():
            validated_data.pop('updated_by')
            validated_data.pop('updated_at')
            validated_data['created_by'] = self.context['request'].user
            instance = HrmsShiftMaster.objects.create(**validated_data)
            return instance

    def get_company_details(self, instance):
        return {
            'company_id': instance.company.id,
            'company_code': instance.company.code,
            'company_name': instance.company.name
        }


class HrmsBusRouteMasterSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    total_vehicles = serializers.SerializerMethodField()

    class Meta:
        model = HrmsBusRouteMaster
        fields = ('__all__')

    def get_total_vehicles(self, instance):
        return HrmsVehicleMaster.objects.filter(bus_route=instance).count()

    def create(self, validated_data):
        with transaction.atomic():
            validated_data.pop('updated_by')
            validated_data.pop('updated_at')
            validated_data['created_by'] = self.context['request'].user
            instance = HrmsBusRouteMaster.objects.create(**validated_data)
            return instance


class HrmsVehicleMasterSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    total_users = serializers.SerializerMethodField()
    bus_route_name = serializers.SerializerMethodField()
    bus_route_no = serializers.SerializerMethodField()
    # additional fields needed for creating an entry
    # list of user id - if empty pass [None]
    user_list = serializers.ListField(required=False, allow_empty=True)

    # --

    class Meta:
        model = HrmsVehicleMaster
        fields = ('__all__')

    def get_total_users(self, instance):
        return UserDetail.objects.filter(vehicle=instance).count()

    def get_bus_route_name(self, instance):
        return instance.bus_route.route_name

    def get_bus_route_no(self, instance):
        return instance.bus_route.route_no

    def create(self, validated_data):
        with transaction.atomic():
            validated_data.pop('updated_by')
            validated_data.pop('updated_at')
            validated_data['created_by'] = self.context['request'].user
            user_list = validated_data.pop('user_list')
            instance = HrmsVehicleMaster.objects.create(**validated_data)
            if user_list:
                for user_id in user_list:
                    if user_id is not None:
                        UserDetail.objects.filter(
                            pk=user_id).update(vehicle=instance)

            return instance


class HrmsVehicleMasterUpdateUserListSerializer(HrmsVehicleMasterSerializer):
    class Meta:
        model = HrmsVehicleMaster
        fields = ('user_list',)

    def update(self, instance, validated_data):
        with transaction.atomic():
            user_list = validated_data.pop('user_list')
            if user_list:
                UserDetail.objects.filter(
                    vehicle=instance).update(vehicle=instance)
                for user_id in user_list:
                    if user_id is not None:
                        UserDetail.objects.filter(
                            pk=user_id).update(vehicle=instance)
            return instance

# region - Leave


class HrmsHolidayMasterSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    company_details = serializers.SerializerMethodField()

    class Meta:
        model = HrmsHolidayMaster
        fields = ('__all__')

    def create(self, validated_data):
        with transaction.atomic():
            validated_data.pop('updated_by')
            validated_data.pop('updated_at')
            validated_data['created_by'] = self.context['request'].user
            instance = HrmsHolidayMaster.objects.create(**validated_data)
            return instance

    def get_company_details(self, instance):
        return {
            'company_id': instance.company.id,
            'company_code': instance.company.code,
            'company_name': instance.company.name
        }


class HrmsLeaveMasterSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())

    class Meta:
        model = HrmsLeaveMaster
        fields = ('__all__')

    def create(self, validated_data):
        with transaction.atomic():
            validated_data.pop('updated_by')
            validated_data.pop('updated_at')
            validated_data['created_by'] = self.context['request'].user
            instance = HrmsLeaveMaster.objects.create(**validated_data)
            return instance


class HrmsGradeLeaveMappingSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    leave_mapping = serializers.DictField(allow_null=True, allow_empty=True)

    grade_details = serializers.SerializerMethodField()

    class Meta:
        model = HrmsGradeLeaveMapping
        fields = ('grade', 'grade_details', 'year', 'leave_mapping', 'updated_by', 'updated_at')

    def create(self, validated_data):
        with transaction.atomic():
            leave_mapping = validated_data.pop("leave_mapping", None)
            if leave_mapping:
                grade = validated_data.get('grade')
                year = validated_data.get('year')
                for leave_id in leave_mapping.keys():
                    quantitiy = leave_mapping[leave_id]
                    leave_id = int(leave_id)
                    validated_data['leave_master_id'] = leave_id
                    validated_data['quantity'] = quantitiy
                    existing_entry = HrmsGradeLeaveMapping.objects.filter(grade=grade, year=year, leave_master=leave_id)
                    if not existing_entry:
                        if validated_data.get('updated_by'):
                            validated_data.pop('updated_by')
                        if validated_data.get('updated_at'):
                            validated_data.pop('updated_at')
                        validated_data['created_by'] = self.context['request'].user
                        instance = HrmsGradeLeaveMapping.objects.create(**validated_data)
                    else:
                        HrmsGradeLeaveMapping.objects.filter(pk=existing_entry[0].id).update(**validated_data)
                        instance = HrmsGradeLeaveMapping.objects.get(pk=existing_entry[0].id)

            # to do - add leave to all existing users of the same grade?

            return instance

    def get_grade_details(self, instance):
        return {
            'grade_id': instance.grade.id,
            'grade_code': instance.grade.code,
            'grade_name': instance.grade.name
        }


class HrmsGradeLeaveMappingListSerializer(HrmsGradeLeaveMappingSerializer):
    leave_details = serializers.SerializerMethodField()

    class Meta:
        model = HrmsGradeLeaveMapping
        fields = ('grade', 'grade_details', 'year', 'quantity', 'leave_master', 'leave_details')

    def get_leave_details(self, instance):
        return {
            'leave_id': instance.leave_master.id,
            'leave_code': instance.leave_master.leave_code,
            'description': instance.leave_master.description
        }

class LeaveHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HrmsApprovalRequest
        fields = ('__all__')

# endregion

# Start Approval #
# Attendance
class AttendanceListSerializer(serializers.ModelSerializer):
    employee_details = serializers.SerializerMethodField()
    approval_request_details = serializers.SerializerMethodField()
    class Meta:
        model = HrmsAttendance
        fields = ('__all__')

    def get_employee_details(self,instance):
        #details = dict()
        details = UserDetail.objects.filter(pk=instance.employee.id).values('name','department','company','is_active','shift')[0]
        if details['shift']:
            details['shift_details'] = HrmsShiftMaster.objects.filter(pk=details['shift']).values()[0]
        return details

    def get_approval_request_details(self,instance):
        hrmsApprovalRequest = HrmsApprovalRequest.objects.filter(attendance_id=instance.id,is_deleted=False).values()
        return hrmsApprovalRequest
        
    
# Start Approval #

class ApprovalRequestAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrmsApprovalRequest
        fields = ('__all__')

    def create(self, validated_data):
        with transaction.atomic():
            validated_data['created_by'] = self.context['request'].user
            hrmsApprovalConfiguration = HrmsApprovalConfiguration.objects.filter(
                approval_section=validated_data['approval_section'], is_deleted=False
            )
            validated_data['current_approval_configuration'] = hrmsApprovalConfiguration.get(level=1)
            instance = HrmsApprovalRequest.objects.create(**validated_data)
            if instance:
                # HrmsApproval insert
                for each in hrmsApprovalConfiguration:
                    HrmsApproval.objects.create(
                        approval_request=instance,
                        approval_configuration=each,
                        created_by = self.context['request'].user
                    )
            return instance

class ApprovalRequestDocumentAddSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HrmsApprovalRequestDocument
        fields = ('__all__')

class ApprovalRequestListSerializer(serializers.ModelSerializer):
    employee_details = serializers.SerializerMethodField()
    attendance_details = serializers.SerializerMethodField()
    approval_configurations = serializers.SerializerMethodField()
    doc_details = serializers.SerializerMethodField()
    current_approval_configuration_details = serializers.SerializerMethodField()
    leave_details = serializers.SerializerMethodField()
    department_details = serializers.SerializerMethodField()
    
    class Meta:
        model = HrmsApprovalRequest
        fields = ('__all__')

    def get_employee_details(self,instance):
        return gf.modify_model_field_name(self,instance,model=UserDetail,fetch_columns=['username','card_no','name','is_active'])
    
    def get_department_details(self,instance):
        return gf.modify_model_field_name(self,instance,model=Department,fetch_columns=['name','code'])
    
    def get_approval_configurations(self,instance):
        hrmsApprovalConfiguration = HrmsApprovalConfiguration.objects.filter(
            approval_section=instance.approval_section,
            employee=instance.employee.id,
            is_deleted=False
            )
        if hrmsApprovalConfiguration:
            hrmsApprovalConfiguration_list = list()
            for each in hrmsApprovalConfiguration.values('id','level','type','approver','approver__name'):
                hrmsApproval = HrmsApproval.objects.filter(
                    approval_configuration_id=each['id'],
                    approval_request=instance,
                    is_deleted=False).values('status','updated_at')[0]
                hrmsApprovalConfiguration_list.append({
                    'id':each['id'],
                    'level':each['level'],
                    'type':each['type'],
                    'approvar':each['approver'],
                    'approvar_name':each['approver__name'],
                    'status':hrmsApproval['status'],
                    'approved_at':hrmsApproval['updated_at']
                })
            return hrmsApprovalConfiguration_list
             
    def get_attendance_details(self,instance):
        if instance.attendance:
            return HrmsAttendance.objects.filter(pk=instance.attendance.id).values()[0]

    def get_doc_details(self,instance):
        return gf.doc_details(self,instance,model=HrmsApprovalRequestDocument)

    def get_current_approval_configuration_details(self,instance):
        return UserDetail.objects.filter(pk=instance.current_approval_configuration.approver.id).values('name','is_active')[0]

    def get_leave_details(self,instance):
        if instance.leave_code:
            return HrmsLeaveMaster.objects.filter(pk=instance.leave_code.id).values(
            'leave_code','is_off_include','is_holiday_include','is_leave_accural','leave_type','present')

class ApprovalConfigListSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrmsApprovalConfiguration
        fields = ('__all__')
        depth = 2

class ApprovalStatusUpdateSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())

    class Meta:
        model = HrmsApprovalRequest
        fields = ('__all__')

    def update(self, instance, validated_data):
        err_msg = None
        with transaction.atomic():
            current_user, updated_at, status = validated_data['updated_by'], validated_data['updated_at'], validated_data['status']
            if not instance.super_admin and not current_user.is_superuser:
                approval_configuration = HrmsApprovalConfiguration.objects.filter(approval_section=instance.approval_section,
                                                                                  employee=instance.employee,
                                                                                  approver=current_user)

                if approval_configuration:
                    approval_configuration = approval_configuration[0]
                    all_approvals = HrmsApproval.objects.filter(approval_request=instance,
                                                                approval_configuration__type='approval'
                                                                ).order_by('-approval_configuration__level')
                    approvals = HrmsApproval.objects.filter(approval_request=instance,
                                                            approval_configuration=approval_configuration)
                    for approval in approvals:
                        if approval_configuration.type == "Post" and status == "Rejected":
                            status = approval.status
                        if status != approval.status:
                            approval.status = status
                            approval.updated_by = current_user
                            approval.updated_at = updated_at
                            approval.save()
                        if approval.id == all_approvals[0].id:
                            # print("Max approval level", approval.id)
                            instance.status = status
                            instance.updated_by = current_user
                            instance.updated_at = updated_at
                            instance.save()

            if current_user.is_superuser:
                # print("Super admin section")
                instance.status = status
                instance.super_admin = current_user
                instance.updated_by = current_user
                instance.updated_at = updated_at
                instance.save()
            return instance

# End Approval #
