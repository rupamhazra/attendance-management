from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth.models import *
from users.serializers import *
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.exceptions import APIException
from django.conf import settings
from django.db.models import Q
from pagination import CSLimitOffestpagination, CSPageNumberPagination, OnOffPagination
from datetime import datetime
from custom_decorator import *
from knox.auth import TokenAuthentication
from rest_framework import permissions
from knox.models import AuthToken
from knox_views.views import LoginView as KnoxLoginView
from django.contrib.auth import login
from knox.settings import CONSTANTS, knox_settings
import global_function as gf
#from master.models import ModuleUser,OtherUser
#from master.models import Other
#from smssend.views import *
from threading import Thread


class LoginView(KnoxLoginView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        #print('fdfdfdfdfdfdfd')
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        update_last_login(None, user)

        login_data = login(request, user)
        #print('login_data', login_data)
        if user:
            odict = self.getUserDetails(user, request)
            return Response(odict)

    def getUserDetails(self, user, request):
        applications = self.getApplications(request, user)
        user_details = user
        profile_pic = request.build_absolute_uri(user_details.profile_img.url) if user_details.profile_img else ''
        odict = collections.OrderedDict()
        odict['user_id'] = user.pk
        odict['token'] = AuthToken.objects.create(user)[1]
        odict['username'] = user.username
        odict['first_name'] = user.first_name
        odict['last_name'] = user.last_name
        odict['email'] = user.email
        odict['official_email'] = user_details.official_email if user_details.official_email else None
        odict['is_superuser'] = user.is_superuser
        odict['phone_no'] = user_details.phone_no
        odict['profile_img'] = profile_pic
        odict['change_pass'] = user_details.change_pass
        odict['module_access'] = applications
        odict['request_status'] = 1
        odict['msg'] = "Log in successfully .."

        browser, ip, os = self.detectBrowser()
        log = LoginLogoutLog.objects.create(
            user=user, token=odict['token'], ip_address=ip, browser_name=browser, os_name=os)

        #print('log',log)
        return odict

    def getApplications(self, request, user):
        mmr_details = ModuleUser.objects.filter(mmr_user=user)
        applications = list()
        for mmr_data in mmr_details:
            module_dict = collections.OrderedDict()
            module_dict["id"] = mmr_data.id
            if mmr_data.mmr_type:
                module_dict["user_type_details"] = collections.OrderedDict({
                    "id": mmr_data.mmr_type,
                    "name": 'Module Admin' if mmr_data.mmr_type == 2 else 'Module User' if mmr_data.mmr_type == 3 else 'Demo User' if mmr_data.mmr_type == 6 else 'Super User'
                })
            else:
                module_dict["user_type_details"] = collections.OrderedDict({})

            module_dict["module"] = collections.OrderedDict({
                "id": mmr_data.mmr_module.id,
                "name": mmr_data.mmr_module.name,
                "url": mmr_data.mmr_module.url,
                "icon": request.build_absolute_uri(mmr_data.mmr_module.icon.url),
            })

            tMasterOtherUser = OtherUser.objects.filter(
                mou_user=user,
                mou_is_deleted=False,
                mou_other__parent_id=0
                # mor_other_id=e_tMasterModuleOther['mmo_other__id']
            )
            # print('tMasterOtherUser', tMasterOtherUser)
            if tMasterOtherUser:
                tMasterModuleOther_list = list()
                for e_tMasterOtherUser in tMasterOtherUser:
                    tMasterModuleOther_e_dict = dict()
                    tMasterModuleOther_e_dict['id'] = e_tMasterOtherUser.mou_other.id
                    tMasterModuleOther_e_dict['name'] = e_tMasterOtherUser.mou_other.name
                    tMasterModuleOther_e_dict['parent'] = e_tMasterOtherUser.mou_other.parent_id
                    tMasterModuleOther_e_dict[
                        'permission'] = e_tMasterOtherUser.mou_permissions.id if e_tMasterOtherUser.mou_permissions else 0
                    # print('mmr_data.mmr_role.id',mmr_data.mmr_role.id)
                    tMasterModuleOther_e_dict['child_details'] = self.getChildOtherListForLogin(
                        #role_id=mmr_data.mmr_role.id,
                        parent_other_id=e_tMasterOtherUser.mou_other.id, user_id=user.id)
                    tMasterModuleOther_list.append(tMasterModuleOther_e_dict)
                
            else:
                tMasterModuleOther_list = list()
            
            module_dict["object_details"] = tMasterModuleOther_list
            applications.append(module_dict)

        return applications

    def detectBrowser(self):
        #print('self.request',dir(self.request.META))
        import httpagentparser
        user_ip = self.request.META.get('REMOTE_ADDR')
        agent = self.request.META.get('HTTP_USER_AGENT')
        browser = httpagentparser.detect(agent)
        browser_name = agent.split('/')[0] if not "browser" in browser.keys() else browser['browser']['name']
        os = "" if not "os" in browser.keys() else browser['os']['name']
        return browser_name, user_ip, os

    def getChildOtherListForLogin(self, parent_other_id: int = 0, user_id: int = 0) -> list:
        try:
            # print('role_id',role_id)
            # permissionList = Permissions.objects.all().values('id', 'name')
            childlist = []
            childlist_data = Other.objects.filter(parent_id=parent_other_id)
            # print('childlist_data',childlist_data)
            for child in childlist_data:
                data_dict = collections.OrderedDict()
                # print('child::',child)
                data_dict['id'] = child.id
                data_dict['name'] = child.name
                data_dict['description'] = child.description
                data_dict['is_deleted'] = child.is_deleted
                data_dict['parent_id'] = child.parent_id
                # print('child.id',type(child.id))
                tMasterOtherRole = OtherUser.objects.filter(
                    # mou_role_id=role_id,
                    mou_other_id=child.id,
                    mou_user_id=user_id
                )
                data_dict['parent_permission'] = 0
                # Checking only child Permisson
                if tMasterOtherRole:
                    # print('tMasterOtherRole', tMasterOtherRole)
                    for e_tMasterOtherRole in tMasterOtherRole:
                        data_dict[
                            'permission'] = e_tMasterOtherRole.mou_permissions.id if e_tMasterOtherRole.mou_permissions else 0
                else:
                    data_dict['permission'] = 0
                data_dict['child_details'] = self.getChildOtherListForLogin(
                    #role_id=role_id,
                    parent_other_id=child.id,
                    user_id=user_id
                )
                # print('data_dict:: ', data_dict)
                childlist.append(data_dict)
            return childlist
        except Exception as e:
            raise e

    def getChildOtherListForRoleLogin(self, role_id: int, parent_other_id: int = 0) -> list:
        try:
            # print('role_id',role_id)
            # permissionList = Permissions.objects.all().values('id', 'name')
            childlist = []
            childlist_data = Other.objects.filter(cot_parent_id=parent_other_id)
            # print('childlist_data',childlist_data)
            for child in childlist_data:
                data_dict = collections.OrderedDict()
                # print('child::',child)
                data_dict['id'] = child.id
                data_dict['cot_name'] = child.cot_name
                data_dict['description'] = child.description
                data_dict['cot_is_deleted'] = child.cot_is_deleted
                data_dict['cot_parent_id'] = child.cot_parent_id
                # print('child.id',type(child.id))
                tMasterOtherRole = OtherRole.objects.filter(
                    mor_role_id=role_id,
                    mor_other_id=child.id
                )
                data_dict['parent_permission'] = 0
                # Checking only child Permisson
                if tMasterOtherRole:
                    # print('tMasterOtherRole', tMasterOtherRole)
                    for e_tMasterOtherRole in tMasterOtherRole:
                        data_dict[
                            'permission'] = e_tMasterOtherRole.mor_permissions.id if e_tMasterOtherRole.mor_permissions else 0
                else:
                    data_dict['permission'] = 0
                data_dict['child_details'] = self.getChildOtherListForRoleLogin(
                    role_id=role_id,
                    parent_other_id=child.id,
                )
                # print('data_dict:: ', data_dict)
                childlist.append(data_dict)
            return childlist
        except Exception as e:
            raise e

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = UserDetail
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user_data = self.request.user
            mail_id = user_data.email
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({'request_status': 1, 'msg': "Wrong password..."}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            UserDetail.objects.filter(user=self.request.user, change_pass=True).update(
                change_pass=False, password_to_know=serializer.data.get("new_password"))
            # ============= Mail Send ==============#
            if mail_id:
                mail_data = {
                    "name": user_data.first_name + '' + user_data.last_name,
                    "password": serializer.data.get("new_password")
                }
                gf.send_mail('CHP', mail_id, mail_data)
            # else:
                # ============= SMS Send ==============#
                # phone_no = UserDetail.objects.only(
                #     'phone_no').get(user=user_data).phone_no
                # if phone_no:
                #     message_data = {
                #         "password": serializer.data.get("new_password")
                #     }
                #     sms_class = GlobleSmsSendTxtLocal('FP100', [phone_no])
                #     sms_thread = Thread(
                #         target=sms_class.sendSMS, args=(message_data, 'sms'))
                #     sms_thread.start()

            return Response({'request_status': 0, 'msg': "New Password Save Success..."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordWithUsernameView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = UserDetail
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]

    def update(self, request, *args, **kwargs):
        username = self.request.data['username']
        user_data = UserDetail.objects.get(username__iexact=username)

        new_password = self.request.data['new_password']
        user_data.set_password(new_password)
        user_data.save()

        UserDetail.objects.filter(
            user=user_data).update(
            change_pass=False, password_to_know=new_password)
        return Response({'request_status': 0, 'msg': "New Password Save Success..."}, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    model = UserDetail
    permission_classes = []
    authentication_classes = []

    def post(self, request, format=None):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            mail_id = serializer.data.get("email")
            phone_no = serializer.data.get("phone_no")
            password = 'Shyam@123'  # default password
            if mail_id:
                user_details_exiest = UserDetail.objects.filter(
                    user__email=mail_id)
            if phone_no:
                user_details_exiest = UserDetail.objects.filter(
                    phone_no=phone_no)
            if user_details_exiest:
                for user_data in user_details_exiest:
                    user_data.change_pass = True
                    user_data.password_to_know = password
                    user_data.user.set_password(password)  # set password...
                    user_data.user.save()
                    user_data.save()
                # ============= Mail Send ==============#
                if mail_id:
                    mail_data = {
                        "name": user_data.user.first_name + '' + user_data.user.last_name,
                        "password": password
                    }
                    gf.send_mail('FP100', mail_id, mail_data)
                # ============= SMS Send ==============#
                # if phone_no:
                #     message_data = {
                #         "password": password
                #     }
                #     sms_class = GlobleSmsSendTxtLocal('FP100', [phone_no])
                #     sms_thread = Thread(
                #         target=sms_class.sendSMS, args=(message_data, 'sms'))
                #     sms_thread.start()

                return Response({'request_status': 1, 'msg': "New Password Save Success..."}, status=status.HTTP_200_OK)
            else:
                raise APIException(
                    {'request_status': 1, 'msg': "User does not exist."})

        return Response({'request_status': 0, 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CreateUserView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserDetail.objects.all()
    serializer_class = UserCreateSerializer

    def get_queryset(self):
        filter = {
            'id':self.request.user.id
        }
        return self.queryset.filter(**filter)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserDetailForApplicationSerializer
        return UserCreateSerializer
    
    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        if not gf.check_unique(UserDetail, request.data, 'username'):
            custom_exception_message(self, 'Paycode')
        return super().post(request, *args, **kwargs)

    @response_modify_decorator_get_single
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class EditUserView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserDetail.objects.all()
    serializer_class = UserEditSerializer
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UserCreateSerializer
        return UserEditSerializer

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        # if not gf.check_unique(UserDetail, request.data, 'username', skip_id=kwargs['pk']):
        #     custom_exception_message(self, 'Paycode')
        return super().update(request, *args, **kwargs)

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # def perform_destroy(self, instance):
    #     user_details = UserDetail.objects.filter(user=instance)
    #     if user_details:
    #         instance.is_active = False
    #         instance.save()
    #         user_detail = user_details[0]
    #         user_detail.is_deleted = True
    #         user_detail.deleted_at = datetime.datetime.now()
    #         user_detail.deleted_by = self.request.user
    #         user_detail.save()

class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserDetail.objects.filter(is_superuser=False)
    serializer_class = UserDetailSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'
        hod = self.request.query_params.get('hod', None)
        inactive = self.request.query_params.get('inactive', None)
        active = self.request.query_params.get('active', None)
        company = self.request.query_params.get('company', None)
        department = self.request.query_params.get('department', None)
        grade = self.request.query_params.get('grade', None)
        category = self.request.query_params.get('category', None)
        designation = self.request.query_params.get('designation', None)
        vehicle = self.request.query_params.get('vehicle', None)
        shift = self.request.query_params.get('shift', None)
        official_email = self.request.query_params.get('official_email', None)
        name = self.request.query_params.get('name', None)
        phone_no = self.request.query_params.get('phone_no', None)
        dob = self.request.query_params.get('dob', None)
        # [ For Team members ]
        team = self.request.query_params.get('team', None)

        if team:
            filter['reporting_head'] = self.request.user

        if hod:
            filter['is_hod'] = 1
        if inactive:
            filter['user__is_active'] = False
        if active:
            filter['user__is_active'] = True

        if official_email:
            filter['official_email__in'] = official_email.split(',')
        if name:
            filter['name__in'] = name.split(',')
        if phone_no:
            filter['phone_no__in'] = phone_no.split(',')
        if dob:
            filter['dob__in'] = dob.split(',')     

        # Search by Name
        if company:
            filter['company__name__in'] = company.split(',')
        if department:
            filter['department__name__in'] = department.split(',')
        if grade:
            filter['grade__name__in'] = grade.split(',')
        if category:
            filter['category__name__in'] = category.split(',')
        if designation:
            filter['designation__name__in'] = designation.split(',')
        if vehicle:
            filter['vehicle__name__in'] = vehicle.split(',')
        if shift:
            filter['shift__name__in'] = shift.split(',')
        

        # Search By Ids
        # if company:
        #     filter['company_id__in'] = company.split(',')
        # if department:
        #     filter['department_id__in'] = department.split(',')
        # if grade:
        #     filter['grade_id__in'] = grade.split(',')
        # if category:
        #     filter['category_id__in'] = category.split(',')
        # if designation:
        #     filter['designation_id__in'] = designation.split(',')
        # if vehicle:
        #     filter['vehicle_id__in'] = vehicle.split(',')
        # if shift:
        #     filter['shift_id__in'] = shift.split(',')

        # Sorting
        field_name = self.request.query_params.get('field_name', None)
        if field_name == 'name':
            field_name = 'user__username'

        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)
        
        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)


    def get_serializer_class(self):
        some_fields = self.request.query_params.get('some_fields', None)
        hod = self.request.query_params.get('some_fields', None)
        if some_fields == '1':
            return UserDetailSomeFieldsSerializer
        
        return UserDetailSerializer
    
    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

class UserListDownloadView(UserListView):
    pagination_class = None

    def get(self, request, *args, **kwargs):
        response = super(__class__, self).get(request, args, kwargs)
        if len(response.data):
            file_path, url = gf.get_media_download_path(
                'users', 'list', 'user_list.xlsx', request)
            headers = response.data[0].keys()
            rows = []
            for d in response.data:
                row = []
                for key in d.keys():
                    row.append(d[key])
                rows.append(row)
            gf.create_simple_excel_file(headers, rows, file_path)
            return Response({'request_status': 1, 'msg': 'Found', 'url': url})
        else:
            return Response({'request_status': 0, 'msg': 'No Data', 'url': url})

# Module List User Wise
class ModuleUserList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserDetail.objects.filter(is_active=True,is_superuser=False).order_by('-id')
    serializer_class = UserModuleSerializer
    pagination_class = CSPageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'phone_no','email',)
    def get_queryset(self):
        try:
            order_by = self.request.query_params.get('order_by', None)
            field_name = self.request.query_params.get('field_name', None)
            if order_by and order_by.lower() == 'desc' and field_name:
                queryset = self.queryset.order_by('-' + field_name)
            elif order_by and order_by.lower() == 'asc' and field_name:
                queryset = self.queryset.order_by(field_name)
            else:
                queryset = self.queryset
            print('queryset',queryset)
            return queryset.filter(~Q(user_id=self.request.user.id))
        except Exception as e:
            # raise e
            raise APIException({'request_status': 0, 'msg': e})

# Role and Module assign to User
class RoleModuleAssignView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ModuleUser.objects.filter(is_deleted=False)
    serializer_class = RoleModuleAssignSerializer

# Login For New User
class LoginGetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        print('username',username)
        try:
            userDetails = UserDetail.objects.filter(user__username=username,is_deleted=False,user__is_active=True)
            print('userDetails',userDetails)
            if userDetails:
                userDetails = userDetails[0]

                # SEND SMS
                if userDetails.phone_no:
                    message_data = {"password": userDetails.password_to_know}
                    #print('message_data',message_data)
                    sms_class = GlobleSmsSendTxtLocal('US-S-GP',[userDetails.phone_no])
                    sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
                    sms_thread.start()

                # SEND MAIL
                if userDetails.official_email:
                    mail_data = {
                                "recipient_name": userDetails.user.get_full_name(),
                                "password":userDetails.password_to_know,
                                "username":userDetails.user.username
                                }
                    print('mail_data',mail_data)
                    gf.send_mail('US-M-GP',userDetails.official_email,mail_data)

                return Response({
                    'request_status':'success',
                    'msg':'SMS Sent',
                    'status_code':Response.status_code
                })
            else:
                raise APIException({
                        "error":{
                            'status_code':status.HTTP_404_NOT_FOUND,
                            'request_status': 'Failure', 
                            'msg': 'Your paycode does not exist!'
                            }
                        })
               
        except Exception as e:
             raise APIException({
                        "error":{
                            'status_code':status.HTTP_404_NOT_FOUND,
                            'request_status': 'Failure', 
                            'msg': 'Your paycode does not exist!'
                            }
                        })
                        
        #print('Response',dir(Response))
        

""" List of users under reporting head starts here
Created by : Bishal Goswami """

class UserListViewUnderReportingHead(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserDetail.objects.filter(is_active=True)
    serializer_class = UserUnderReporingHeadDetailSomeFieldsSerializer
    pagination_class = OnOffPagination

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)
        
    def get_queryset(self):
        exclude,ordering = {},'-id'
        logged_in_user=self.request.user
        return self.queryset.filter(reporting_head=logged_in_user).exclude(**exclude).order_by(ordering)
        
# ends here