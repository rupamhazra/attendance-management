from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from master.models import *
from users.serializers import *
from django.contrib.auth.models import *
from rest_framework.exceptions import APIException
from django.conf import settings
import random
import string
from django.db.models import Q
from datetime import datetime

# region - grade and designation - added / updated by Shubhadeep


class DesignationAddSerializer(serializers.ModelSerializer):
    # mmr_module = serializers.SerializerMethodField()
    updated_by = serializers.CharField(
        default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    total_users = serializers.SerializerMethodField()

    class Meta:
        model = Designation
        fields = ('__all__')

    def get_total_users(self, instance):
        return UserDetail.objects.filter(designation=instance).count()

    def create(self, validated_data):
        validated_data.pop('updated_by')
        validated_data.pop('updated_at')
        validated_data['created_by'] = self.context['request'].user
        instance = Designation.objects.create(**validated_data)
        return instance


# endregion


class PermissionsSerializer(serializers.ModelSerializer):
    cp_created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Permission
        fields = ('id', 'name', 'cp_created_by')


class ModuleSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Module
        fields = ('id', 'name', 'icon', 'desc', 'url',
                  'created_by', 'is_editable')


class ModuleListSerializer(serializers.ModelSerializer):
    """docstring for ClassName"""
    # icon = Base64ImageField()

    class Meta:
        model = Module
        fields = ('id', 'name', 'icon', 'desc', 'url')


# class RoleSerializer(serializers.ModelSerializer):
#     """docstring for ClassName"""
#     cr_created_by = serializers.HiddenField(
#         default=serializers.CurrentUserDefault())

#     class Meta:
#         model = Role
#         fields = ('id', 'cr_name', 'cr_parent_id',
#                   'cr_created_by', 'cr_is_deleted')


# OBJECTS #

class OtherListSerializer(serializers.ModelSerializer):
    #parent_name = serializers.CharField(required=False)
    class Meta:
        model = ModuleOther
        fields = ('id', 'mmo_other', 'mmo_module', 'is_deleted')


class OtherListForRoleSerializer(serializers.ModelSerializer):
    permission = serializers.CharField(required=False)

    class Meta:
        model = ModuleOther
        fields = ('id', 'mmo_other', 'mmo_module', 'is_deleted', 'permission')


class OtherEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(
        default=serializers.CurrentUserDefault())
    parent_id = serializers.IntegerField(required=False)
    mmo_module = serializers.CharField(required=False)

    class Meta:
        model = Other
        fields = ('id', 'name', 'description',
                  'parent_id', 'updated_by', 'mmo_module')

    def update(self, instance, validated_data):
        try:
            updated_by = validated_data.get('updated_by')
            parent_id = validated_data.pop(
                'parent_id') if 'parent_id' in validated_data else 0
            with transaction.atomic():
                instance.name = validated_data.get('name')
                instance.description = validated_data.get('description')
                instance.parent_id = parent_id
                instance.updated_by = updated_by
                instance.updated_at = datetime.datetime.now()
                instance.save()

                tMasterModuleOther = ModuleOther.objects.filter(mmo_other=instance.id)
                
                if tMasterModuleOther:
                    tMasterModuleOther.delete()

                master_module = ModuleOther.objects.create(
                    mmo_other=instance,
                    mmo_module_id=validated_data.get('mmo_module'),
                )
                #print('master_module', master_module)
                response = {
                    'id': instance.id,
                    'name': instance.name,
                    'description': instance.description,
                    'mmo_module': master_module.mmo_module,
                    'parent_id': instance.parent_id
                }
                return response
        except Exception as e:
            raise e


class OtherAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(
        default=serializers.CurrentUserDefault())
    parent_id = serializers.IntegerField(required=False)
    mmo_module = serializers.CharField(required=False)

    class Meta:
        model = Other
        fields = ('id', 'name', 'description',
                  'parent_id', 'created_by', 'mmo_module')

    def create(self, validated_data):
        try:
            created_by = validated_data.get('created_by')
            parent_id = validated_data.pop(
                'parent_id') if 'parent_id' in validated_data else 0
            with transaction.atomic():
                save_id = Other.objects.create(
                    name=validated_data.get('name'),
                    description=validated_data.get('description'),
                    parent_id=parent_id,
                    created_by=created_by,
                )
                module_id = Module.objects.only('id').get(
                    name=validated_data.get('mmo_module')).id
                #print('module_id', module_id)
                master_module = ModuleOther.objects.create(
                    mmo_other=save_id,
                    mmo_module_id=module_id,

                )
                response = {
                    'id': save_id.id,
                    'name': save_id.name,
                    'description': save_id.description,
                    'mmo_module': master_module.mmo_module,
                    'parent_id': save_id.parent_id
                }
                return response
        except Exception as e:
            raise e


# class OtherListWithPermissionByRoleModuleNameSerializer(serializers.ModelSerializer):
#     mor_permissions_n = serializers.IntegerField(required=False)

#     class Meta:
#         model = OtherRole
#         fields = ('id', 'mor_other', 'mor_module', 'mor_role',
#                   'mor_permissions', 'mor_permissions_n')


class OtherEditNewSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(
        default=serializers.CurrentUserDefault())
    parent_id = serializers.IntegerField(required=False)

    class Meta:
        model = Other
        fields = ('id', 'name', 'description', 'parent_id', 'updated_by')

    def update(self, instance, validated_data):
        try:
            updated_by = validated_data.get('updated_by')
            with transaction.atomic():
                instance.name = validated_data.get('name')
                instance.description = validated_data.get('description')
                instance.updated_by = updated_by
                instance.save()
                response = {
                    'id': instance.id,
                    'name': instance.name,
                    'description': instance.description,
                    'parent_id': instance.parent_id
                }
                return response
        except Exception as e:
            raise e


class OtherListWithPermissionByUserModuleNameSerializer(serializers.ModelSerializer):
    mou_permissions_n = serializers.IntegerField(required=False)
    mor_other = serializers.IntegerField(required=False)
    mor_module = serializers.IntegerField(required=False)
    mor_permissions = serializers.IntegerField(required=False)
    mor_permissions_n = serializers.IntegerField(required=False)

    class Meta:
        model = OtherUser
        fields = ('id', 'mou_other', 'mou_module', 'mou_permissions',
                  'mou_permissions_n', 'mor_other', 'mor_module', 'mor_permissions', 'mor_permissions_n')


# COMPANY #
class CompanyAddSerializer(serializers.ModelSerializer):
    address = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    short_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    email_id_1 = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    email_id_2 = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    total_no_gate_pass = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    gate_pass_monthly_duration = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    updated_by = serializers.CharField(
        default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    total_category = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ('__all__')

    def get_total_category(self, instance):
        return Category.objects.filter(company=instance).count()

    def create(self, validated_data):
        validated_data.pop('updated_by')
        validated_data.pop('updated_at')
        validated_data['created_by'] = self.context['request'].user
        return Company.objects.create(**validated_data)

# CATEGORY #


class CategoryAddSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(
        default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    total_department = serializers.SerializerMethodField()
    company_details  = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('__all__')

    def get_total_department(self, instance):
        return Department.objects.filter(category=instance).count()



    def create(self, validated_data):
        validated_data.pop('updated_by')
        validated_data.pop('updated_at')
        validated_data['created_by'] = self.context['request'].user
        return Category.objects.create(**validated_data)
    
    def get_company_details(self,instance):
        if instance.company:
            company = Company.objects.filter(pk=instance.company.id,is_deleted=False)
            if company:
                return company.values()[0] 
    

# DEPARTMENT #


class DepartmentAddSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(
        default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    # total_hod = serializers.SerializerMethodField()
    parent_details = serializers.SerializerMethodField()
    category_details = serializers.SerializerMethodField()
    hod_details = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ('__all__')
        
    # def get_total_hod(self, instance):
    #     return UserDetail.objects.filter(pk=instance.hod, is_hod=True).count()
    

    def create(self, validated_data):
        print('validated_data',validated_data)
        validated_data.pop('updated_by')
        validated_data.pop('updated_at')
        validated_data['created_by'] = self.context['request'].user
        return Department.objects.create(**validated_data)
    
    def get_parent_details(self,instance):
        if instance.parent:
            department = Department.objects.filter(pk=str(instance.parent),is_deleted=False)
            if department:
                return department.values('id','code','name')[0]

    def get_category_details(self,instance):
        if instance.category:
            category = Category.objects.filter(pk=instance.category.id,is_deleted=False)
            if category:
                return category.values()[0] 
    
    def get_hod_details(self,instance):
        if instance.hod:
            user = {
                'id':instance.hod.id,
                'name': instance.hod.get_full_name(),
                }
            return user

# GRADE #

class GradeAddSerializer(serializers.ModelSerializer):
    parent_details = serializers.SerializerMethodField()
    updated_by = serializers.CharField(
        default=serializers.CurrentUserDefault())
    updated_at = serializers.DateTimeField(default=datetime.now())
    total_users = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = ('__all__')
    
    def get_parent_details(self,instance):
        if instance.parent:
            grade = Grade.objects.filter(pk=str(instance.parent),is_deleted=False)
            if grade:
                return grade.values('id','code','name')[0]

    def create(self, validated_data):
        #print('validated_data',validated_data)
        validated_data.pop('updated_by')
        validated_data.pop('updated_at')
        validated_data['created_by'] = self.context['request'].user
        return Grade.objects.create(**validated_data)

    def get_total_users(self, instance):
        return UserDetail.objects.filter(grade=instance).count()

class UserListSerializer(serializers.ModelSerializer):
    #mmr_role = RoleSerializer()
    mmr_module = ModuleSerializer()
    mmr_permissions = PermissionsSerializer()
    mmr_user = UserSerializer()
    # mmr_user = UserDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = ModuleUser
        # fields = ('id', 'mmr_module', 'mmr_permissions',
        #           'mmr_role', 'mmr_user')
        fields = ('id', 'mmr_module', 'mmr_permissions','mmr_user')


# class ModuleRoleSerializer(serializers.ModelSerializer):
#     mmro_role = RoleSerializer()
#     mmro_created_by = serializers.CharField(
#         default=serializers.CurrentUserDefault())
#     module_name = serializers.SerializerMethodField()

#     def get_module_name(self, ModuleRole):
#         return Module.objects.only('name').get(pk=ModuleRole.mmro_module.id).name

#     class Meta:
#         model = ModuleRole
#         fields = ('id', 'mmro_module', 'module_name',
#                   'mmro_created_by', 'mmro_role',)

#     def create(self, validated_data):
#         try:
#             data = {}
#             logdin_user_id = self.context['request'].user.id
#             role_dict = validated_data.pop('mmro_role')

#             print('validated_data: ', validated_data)
#             role = Role.objects.create(
#                 **role_dict, cr_created_by_id=logdin_user_id)
#             if role:
#                 module_role_data = ModuleRole.objects.create(
#                     mmro_module=validated_data['mmro_module'],
#                     mmro_role=role,
#                     mmro_created_by=validated_data['mmro_created_by'],
#                 )
#                 data['id'] = module_role_data.pk
#                 data['mmro_module'] = module_role_data.mmro_module
#                 data['mmro_role'] = module_role_data.mmro_role
#                 data['mmro_created_by'] = module_role_data.mmro_created_by

#             return data
#         except Exception as e:
#             # raise e
#             raise serializers.ValidationError(
#                 {'request_status': 0, 'msg': 'error', 'error': e})

# Manpower serializer #


class UserModuleWiseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleUser
        fields = ('id', 'mmr_module', 'mmr_role', 'mmr_user')


class UserModuleWiseUserListByDesignationIdSerializer(serializers.ModelSerializer):
    # user_details =serializers.ListField(required=True)
    class Meta:
        model = ModuleUser
        fields = ('id', 'mmr_module', 'mmr_role', 'mmr_user')


# class AssignPermissonToRoleAddNewSerializer(serializers.ModelSerializer):
#     #mor_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     mor_created_by = serializers.CharField(
#         default=serializers.CurrentUserDefault())
#     mor_other_permisson_details = serializers.ListField()
#     mor_module = serializers.CharField()
#     mor_role = serializers.CharField()

#     class Meta:
#         model = OtherRole
#         fields = ('id', 'mor_module', 'mor_other_permisson_details',
#                   'mor_role', 'mor_created_by')

#     def create(self, validated_data):
#         try:
#             # print('validated_data',validated_data)

#             mor_module = Module.objects.get(
#                 name=validated_data.get('mor_module'))
#             # print('mor_module',mor_module)
#             mor_role = Role.objects.get(cr_name=validated_data.get('mor_role'))
#             # print('mor_role',mor_role)

#             '''
#                 Insert Data to OtherRole
#             '''
#             mor_other_permisson_details = validated_data.get(
#                 'mor_other_permisson_details')
#             # print('mor_other_permisson_details',mor_other_permisson_details)

#             for e_mor_other_permisson_details in mor_other_permisson_details:
#                 tMasterOtherRole = OtherRole.objects.filter(
#                     mor_role=mor_role,
#                     mor_other=e_mor_other_permisson_details['mor_other'],
#                     mor_module=mor_module
#                 )
#                 # print(type(e_mor_other_permisson_details['mor_permisson']))
#                 # print('tMasterOtherRole',tMasterOtherRole)
#                 if tMasterOtherRole:
#                     #print('ModuleUser', tMasterOtherRole)
#                     if e_mor_other_permisson_details['mor_permisson'] == 0 or e_mor_other_permisson_details['mor_permisson'] == 4:
#                         mor_permisson_v = None
#                     else:
#                         mor_permisson_v = e_mor_other_permisson_details['mor_permisson']

#                     tMasterOtherRole.update(
#                         mor_role=mor_role,
#                         mor_other_id=e_mor_other_permisson_details['mor_other'],
#                         mor_permissions_id=mor_permisson_v,
#                         mor_module=mor_module,
#                         mor_created_by=validated_data.get('mor_created_by')
#                     )

#                     tMasterOtherUser = OtherUser.objects.filter(
#                         mou_other_id=e_mor_other_permisson_details['mor_other'],
#                         mou_module=mor_module
#                     ).update(mou_permissions_id=mor_permisson_v)
#                     print('tMasterOtherUser', tMasterOtherUser)

#                 else:
#                     # print('ddddddd',e_mor_other_permisson_details['mor_other'])
#                     if e_mor_other_permisson_details['mor_permisson'] == 0 or e_mor_other_permisson_details['mor_permisson'] == 4:
#                         mor_permisson_v = None
#                     else:
#                         mor_permisson_v = e_mor_other_permisson_details['mor_permisson']

#                     re = OtherRole.objects.create(
#                         mor_role=mor_role,
#                         mor_other_id=e_mor_other_permisson_details['mor_other'],
#                         mor_permissions_id=mor_permisson_v,
#                         mor_module=mor_module,
#                         mor_created_by=validated_data.get('mor_created_by')
#                     )

#                     tMasterOtherUser = OtherUser.objects.filter(
#                         mou_other_id=e_mor_other_permisson_details['mor_other'],
#                         mou_module=mor_module
#                     )

#                     if not tMasterOtherUser:
#                         print('else')
#                         users = ModuleUser.objects.filter(
#                             mmr_role=mor_role, mmr_module=mor_module,).values_list('mmr_user', flat=True)
#                         print('user', users)
#                         existing_user_tMasterOtherUser = OtherUser.objects.filter(
#                             mou_user__in=users).values_list('mou_user', flat=True).distinct()
#                         print('existing_user_tMasterOtherUser',
#                               existing_user_tMasterOtherUser)
#                         for user in existing_user_tMasterOtherUser:
#                             print('user', type(user))
#                             OtherUser.objects.create(
#                                 mou_user_id=user,
#                                 mou_other_id=e_mor_other_permisson_details['mor_other'],
#                                 mou_permissions_id=mor_permisson_v,
#                                 mou_module=mor_module,
#                                 mou_created_by=validated_data.get(
#                                     'mor_created_by')
#                             )
#                         # print('tMasterOtherUser',tMasterOtherUser)

#                     # print('re',re)

#             '''
#                 Insert Data to OtherUser
#             '''

#             return validated_data
#         except Exception as e:
#             # raise e
#             raise serializers.ValidationError(
#                 {'request_status': 0, 'msg': 'error', 'error': e})


# class ModuleRoleNewSerializer(serializers.ModelSerializer):
#     mmro_role = RoleSerializer()
#     mmro_created_by = serializers.CharField(
#         default=serializers.CurrentUserDefault())
#     mmro_module = serializers.CharField()

#     class Meta:
#         model = ModuleRole
#         fields = ('id', 'mmro_module', 'mmro_created_by', 'mmro_role',)

#     def create(self, validated_data):
#         try:
#             data = {}
#             logdin_user_id = self.context['request'].user.id
#             role_dict = validated_data.pop('mmro_role')
#             mmro_module = Module.objects.get(
#                 name=validated_data.get('mmro_module'))
#             #print('validated_data: ', validated_data)
#             role = Role.objects.create(
#                 **role_dict, cr_created_by_id=logdin_user_id)
#             if role:
#                 module_role_data = ModuleRole.objects.create(
#                     mmro_module=mmro_module,
#                     mmro_role=role,
#                     mmro_created_by=validated_data['mmro_created_by'],
#                 )
#             return module_role_data
#         except Exception as e:
#             # raise e
#             raise serializers.ValidationError(
#                 {'request_status': 0, 'msg': 'error', 'error': e})


class AssignPermissonToUserAddNewSerializer(serializers.ModelSerializer):
    mou_created_by = serializers.CharField(
        default=serializers.CurrentUserDefault())
    mou_other_permisson_details = serializers.ListField()

    class Meta:
        model = OtherUser
        fields = ('id', 'mou_other_permisson_details', 'mou_user', 'mou_created_by')

    def create(self, validated_data):
        try:
            # print('validated_data',validated_data)
            mou_module = Module.objects.get(name='HRMS')
            mou_user = validated_data.get('mou_user')
            #mou_role = validated_data.get('mou_role')
            # print('mou_role',mou_role)

            mou_other_permisson_details = validated_data.get(
                'mou_other_permisson_details')
            # print('mou_other_permisson_details',mou_other_permisson_details)

            for e_mou_other_permisson_details in mou_other_permisson_details:
                tMasterOtherUser = OtherUser.objects.filter(
                    mou_user=mou_user,
                    mou_other=e_mou_other_permisson_details['mou_other'],
                    mou_module=mou_module
                )
                # print(type(e_mou_other_permisson_details['mou_permisson']))
                print('tMasterOtherRole', tMasterOtherUser)
                if tMasterOtherUser:
                    #print('ModuleUser', tMasterOtherUser)
                    if e_mou_other_permisson_details['mou_permisson'] == 0 or e_mou_other_permisson_details['mou_permisson'] == 4:
                        mou_permisson_v = None
                    else:
                        mou_permisson_v = e_mou_other_permisson_details['mou_permisson']
                    tMasterOtherUser.update(
                        mou_user=mou_user,
                        mou_other_id=e_mou_other_permisson_details['mou_other'],
                        mou_permissions_id=mou_permisson_v,
                        mou_module=mou_module,
                        mou_created_by=validated_data.get('mou_created_by')
                    )
                else:
                    # print('ddddddd',e_mou_other_permisson_details['mou_other'])
                    if e_mou_other_permisson_details['mou_permisson'] == 0 or e_mou_other_permisson_details['mou_permisson'] == 4:
                        mou_permisson_v = None
                    else:
                        mou_permisson_v = e_mou_other_permisson_details['mou_permisson']

                    re = OtherUser.objects.create(
                        mou_user=mou_user,
                        mou_other_id=e_mou_other_permisson_details['mou_other'],
                        mou_permissions_id=mou_permisson_v,
                        mou_module=mou_module,
                        mou_created_by=validated_data.get('mou_created_by')
                    )
                    # print('re',re)
            return validated_data
        except Exception as e:
            # raise e
            raise serializers.ValidationError(
                {'request_status': 0, 'msg': 'error', 'error': e})

class TemplateMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateMaster
        fields = ('__all__')

    def create(self, validated_data):
        instance = TemplateMaster.objects.create(**validated_data)
        return instance
