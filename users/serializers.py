from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from users.models import *
#from django.contrib.auth.models import *
from rest_framework.exceptions import APIException
from nameparser import HumanName
from mailsend.views import *
#from smssend.views import *
from django.db import transaction, IntegrityError
from django.conf import settings
from django.db.models import F
from datetime import datetime
import json
from django.contrib.auth import authenticate
import global_function as gf
from master.models import ModuleUser,OtherUser
import base64
from custom_exception_message import *
import os


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(
            username=data['username'], password=data['password'], active_check=True)
        if user is not None:
            if user.is_active:
                return user
            else:
                raise APIException(
                    {'request_status': 0, 'msg': 'The account has been disabled!'})
        else:
            raise APIException(
                {'request_status': 0, 'msg': 'Please check the username and password'})

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ('__all__')
        depth = 1

class UserDetailSomeFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ('id','email','first_name','last_name','name','is_active')



# It is used for approval application
class UserDetailForApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ('id','username','name','is_active','company','department','category','designation',)
        depth = 1

class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    section = serializers.CharField(required=False,allow_blank=True)
    email = serializers.CharField(required=False,allow_null=True,allow_blank=True)
    password = serializers.CharField(required=False,default="ssml@123")
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    password_to_know = serializers.CharField(default="ssml@123")
    change_pass = serializers.BooleanField(default=True)
    groups = serializers.ListField(required=False) # Avoid Groups
    user_permissions = serializers.ListField(required=False) # Avoid user_permissions
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = UserDetail
        fields = '__all__'

    def create(self, validated_data):
        try:
            logdin_user_id = self.context['request'].user.id
            section =  validated_data.pop('section')
            username = validated_data.get('username').strip()
            
            with transaction.atomic():
                username_encode = base64.b64encode(bytes('username', 'utf-8'))
                username_encode = username_encode.decode('utf-8')
                password = validated_data.pop('password')
                userdetail_save,__ = UserDetail.objects.get_or_create(**validated_data)
                userdetail_save.set_password(password)
                userdetail_save.save()
                validated_data['id'] = int(userdetail_save.id)

                if settings.ENV == 'staging' or settings.ENV == 'production': # Not For Local Only For Staging and Live
                        if userdetail_save:
                            # SEND MAIL
                            link = settings.WEB_LINK+username_encode
                            if userdetail_save.official_email:
                                mail_data = {
                                            "recipient_name": userdetail_save.user.get_full_name(),
                                            "username":userdetail_save.user.username,
                                            "link": link
                                            }
                                gf.send_mail('US-M-NU',userdetail_save.official_email,mail_data)
            
                return validated_data

        except Exception as e:
            raise e
    
    def update(self, instance, validated_data):
        try:
            validated_data.pop('password')
            validated_data.pop('password_to_know')
            validated_data.pop('change_pass')
            logdin_user_id = self.context['request'].user.id
            section =  validated_data.pop('section')
            #username = validated_data.pop('username').strip()
            #print('validated_data',validated_data)
            with transaction.atomic():
                if section == 'personal_details' or section == 'time_office_policy' or section == 'shift_policy' or section == 'other_information':
                    if section == 'personal_details':
                        #email = validated_data.pop('email') if 'email' in validated_data else ''
                        #User.objects.filter(pk=instance.user.id).update(email=email)
                        if 'pan_card_pic' in validated_data:
                            instance.pan_card_pic = validated_data.pop('pan_card_pic') 
                        if 'aadhar_card_pic' in validated_data:
                            instance.aadhar_card_pic = validated_data.pop('aadhar_card_pic')
                        if 'passbook_pic' in validated_data:
                            instance.passbook_pic = validated_data.pop('passbook_pic')
                        instance.save()
                    #userdetail_save = UserDetail.objects.filter(pk=instance.id).update(**validated_data)
                
                else:
                    if 'profile_img' in validated_data:
                        instance.profile_img = validated_data.pop('profile_img')
                    if 'signature' in validated_data:
                        instance.signature = validated_data.pop('signature')
                    instance.save()
                UserDetail_update = UserDetail.objects.filter(pk=instance.id)
                #print('UserDetail_update',UserDetail_update)
                userdetail_save= UserDetail_update.update(**validated_data)
                #print('userdetail_save',userdetail_save)
            
            return validated_data
        except Exception as e:
            raise e


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    phone_no = serializers.CharField(required=False)

class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = '__all__'
        depth = 2

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    is_superuser = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    class Meta:
        model = UserDetail
        fields = ('id','first_name', 'last_name', 'username','email', 'is_superuser', 'is_active')

class UserModuleSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = UserDetail
        fields = ('id', 'phone_no', 'alt_phone_no', 'dob', 'user', 'applications')

class RoleModuleAssignSerializer(serializers.ModelSerializer):
    role_module_details = serializers.ListField(required=False)
    mmr_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    mmr_created_at = serializers.DateTimeField(default=datetime.now())
    
    class Meta:
        model = ModuleUser
        fields = ('id', 'role_module_details', 'mmr_created_by','mmr_user','mmr_created_at')

    def create(self, validated_data):
        try:
            #print('validated_data',validated_data)
            #role_module_details = validated_data.pop('role_module_details')
            with transaction.atomic():
                user = validated_data.get('mmr_user')
                #role_module_details = json.loads(role_module_details[0])
                for e_role_module_details in validated_data.pop('role_module_details'):
                    role_id = e_role_module_details['role_id']
                    mmr_module_id = e_role_module_details['mmr_module_id']
                    mmr_type = e_role_module_details['mmr_type']
                    role_module_details = ModuleUser.objects.filter(
                        mmr_module_id=mmr_module_id,
                        mmr_role_id=role_id,
                        mmr_type = 3,
                        mmr_user = user,
                    )
                    if not role_module_details:
                        ModuleUser.objects.create(
                            mmr_module_id=mmr_module_id,
                            mmr_role_id=role_id,
                            mmr_type = 3,
                            mmr_user = user,
                            mmr_created_by = validated_data['mmr_created_by']
                        )
                        '''
                            Assign role objects permission to User 
                        '''
                        tMasterOtherRole = OtherRole.objects.filter(mor_role_id=role_id,mor_module_id = mmr_module_id)
                        for e_tMasterOtherRole in tMasterOtherRole:
                            OtherUser.objects.create(
                                mou_user = user,
                                mou_other = e_tMasterOtherRole.mor_other,
                                mou_permissions = e_tMasterOtherRole.mor_permissions,
                                mou_module_id = mmr_module_id,
                                mou_created_by = validated_data['mmr_created_by']
                            )
                    return validated_data

        except Exception as e:
            #raise e
            raise APIException({'request_status': 0, 'msg': e})

""" List of users under reporting head starts here
Created by : Bishal Goswami """

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class UserUnderReporingHeadDetailSomeFieldsSerializer(serializers.ModelSerializer):
    user_re_head=RecursiveSerializer(many=True,read_only=True)

    class Meta:
        model = UserDetail
        fields = ('id','email','first_name','last_name','name','dob','highest_qualification',
            'experience','date_joined','is_active','user_re_head','company','department','category','designation')

# ends here