from rest_framework import generics
from rest_framework import filters
from django.contrib.auth.models import *
from master.serializers import *
from users.models import UserDetail
from users.serializers import UserDetailSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from pagination import CSLimitOffestpagination, CSPageNumberPagination, OnOffPagination
import numpy as np
from django.db import transaction
from rest_framework.views import APIView
from threading import Thread  # for threading
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q
from custom_decorator import *
from knox.auth import TokenAuthentication
from rest_framework import permissions
from knox.models import AuthToken
import global_function as gf
from custom_exception_message import *


# region - grade and designation - added / updated by Shubhadeep

class DesignationAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Designation.cmobjects.all()
    serializer_class = DesignationAddSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        code = self.request.query_params.get('code', None)
        name = self.request.query_params.get('name', None)
        if name:
            filter['name__icontains'] = name
        if code:
            filter['code__icontains'] = code

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        if not gf.check_unique(Designation, request.data, 'code'):
                custom_exception_message(self, 'Designation code')
        if not gf.check_unique(Designation, request.data, 'name'):
                custom_exception_message(self, 'Designation name')
        return super().post(request, *args, **kwargs)


class DesignationUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserDetail.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer
    pagination_class = OnOffPagination

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    def get_queryset(self):
        designation_id = self.request.query_params.get('designation_id', None)
        if designation_id:
            return self.queryset.filter(designation=designation_id)
        else:
            raise Exception('Provide designation_id in query parameter')


class DesignationEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Designation.cmobjects.all()
    serializer_class = DesignationAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        if not gf.check_unique(Designation, request.data, 'code',skip_id=kwargs['pk']):
                custom_exception_message(self, 'Designation code')
        if not gf.check_unique(Designation, request.data, 'name', skip_id=kwargs['pk']):
                custom_exception_message(self, 'Designation name')
        return super().update(request, *args, **kwargs)

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = datetime.now()
        instance.deleted_by = self.request.user
        instance.save()
        # update all users to the new designation id provided in the API call
        new_designation_id = self.request.query_params.get(
            'new_designation_id', None)
        if new_designation_id:
            UserDetail.objects.filter(
                designation=instance).update(designation=new_designation_id)

# Grade #


class GradeAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Grade.cmobjects.all()
    serializer_class = GradeAddSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        name = self.request.query_params.get('name', None)
        code = self.request.query_params.get('code', None)
        grade = self.request.query_params.get('grade', None)
        child = self.request.query_params.get('child', None)
        if code:
            filter['code__icontains'] = code
        if name:
            filter['name__icontains'] = name
        if grade:
            if child == '1':
                filter['parent_id'] = grade
            else:
                filter['id'] = grade

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        if not gf.check_unique(Grade, request.data, 'code'):
                custom_exception_message(self, 'Grade code')
        if not gf.check_unique(Grade, request.data, 'name'):
                custom_exception_message(self, 'Grade name')
        return super().post(request, *args, **kwargs)


class GradeUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserDetail.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer
    pagination_class = OnOffPagination

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    def get_queryset(self):
        grade_id = self.request.query_params.get('grade_id', None)
        if grade_id:
            return self.queryset.filter(grade=grade_id)
        else:
            raise Exception('Provide grade_id in query parameter')


class GradeEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Grade.cmobjects.all()
    serializer_class = GradeAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        if not gf.check_unique(Grade, request.data, 'code', skip_id=kwargs['pk']):
                custom_exception_message(self, 'Grade code')
        if not gf.check_unique(Grade, request.data, 'name', skip_id=kwargs['pk']):
                custom_exception_message(self, 'Grade name')
        return super().update(request, *args, **kwargs)

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = datetime.now()
        instance.deleted_by = self.request.user
        instance.save()
        # update all users to the new grade id provided in the API call
        new_grade_id = self.request.query_params.get('new_grade_id', None)
        if new_grade_id:
            UserDetail.objects.filter(
                grade=instance).update(grade=new_grade_id)

# endregion


class PermissionsListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # pagination_class =CSPageNumberPagination
    queryset = Permission.objects.all()
    serializer_class = PermissionsSerializer
    filter_backends = (filters.SearchFilter,)


class ModuleListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Module.cmobjects.all()
    serializer_class = ModuleSerializer


class ModuleList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Module.objects.all()
    serializer_class = ModuleListSerializer


class EditModuleById(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


# class RoleListCreate(generics.ListCreateAPIView):
#     """docstring for ClassName"""
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = Role.objects.all()
#     serializer_class = RoleSerializer


# class RoleRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
#     """docstring for ClassName"""
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = Role.objects.all()
#     serializer_class = RoleSerializer

#  OBJECTS #


class OtherEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Other.objects.all()
    serializer_class = OtherEditSerializer


class OtherAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Other.objects.all()
    serializer_class = OtherAddSerializer


class OtherListNewView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # pagination_class = CSPageNumberPagination
    queryset = ModuleOther.cmobjects.all()
    serializer_class = OtherListSerializer

    def get_queryset(self):
        module_name = self.kwargs['module_name']
        # parent_id = self.kwargs['parent_id']
        result = ModuleOther.objects.filter(mmo_module__name=module_name, mmo_other__parent_id=0, is_deleted=False)
        #print('result', result)
        return result

    def get_child_list(self, object_id: int) -> list:
        try:
            childlist = []
            childlist_data = Other.objects.filter(
                parent_id=object_id, is_deleted=False)

            for child in childlist_data:
                #print('child', child)
                data_dict = collections.OrderedDict()
                # print('child::',child)
                data_dict['id'] = child.id
                data_dict['name'] = child.name
                data_dict['parent_id'] = child.parent_id
                data_dict['is_deleted'] = child.is_deleted
                data_dict['items'] = self.get_child_list(object_id=child.id)
                data_dict['mou_permisson'] = None
                data_dict['permission_list'] = AccessPermission.objects.values('id', 'name')
                # print('data_dict:: ', data_dict)
                childlist.append(data_dict)
            return childlist
        except Exception as e:
            raise e

    @response_modify_decorator_list_after_execution
    def list(self, request, *args, **kwargs):
        response = super(OtherListNewView, self).list(request, args, kwargs)
        # print('data',response.data)
        for data in response.data:
            # data['child'] = self.get_child_list(object_id=data['mmo_other'])
            OtherDetails = Other.objects.filter(
                pk=data['mmo_other'], is_deleted=False)
            # print('OtherDetails query',OtherDetails.query)
            for e_OtherModuleDetails in OtherDetails:
                # print('OtherDetails',OtherDetails)
                data['id'] = e_OtherModuleDetails.id
                data['name'] = e_OtherModuleDetails.name
                data['description'] = e_OtherModuleDetails.description
                data['parent_id'] = e_OtherModuleDetails.parent_id
                data['is_deleted'] = e_OtherModuleDetails.is_deleted
                data['permission_list'] = AccessPermission.objects.values('id', 'name')
                data['mou_permisson'] = None
                data['items'] = self.get_child_list(
                    object_id=e_OtherModuleDetails.id)
        return response


# class OtherListWithPermissionByRoleModuleNameView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     # pagination_class = CSPageNumberPagination
#     queryset = OtherRole.objects.all()
#     serializer_class = OtherListWithPermissionByRoleModuleNameSerializer

#     def get_queryset(self):
#         module_name = self.kwargs['module_name']
#         role_name = self.kwargs['role_name']
#         # parent_id = self.kwargs['parent_id']
#         return OtherRole.objects.filter(
#             mor_module__name=module_name,
#             mor_role__cr_name=role_name,
#             mor_module__is_deleted=False,
#             mor_role__cr_is_deleted=False
#         ).annotate(
#             mor_permissions_n=Case(
#                 When(mor_permissions__isnull=True, then=Value(0)),
#                 When(mor_permissions__isnull=False, then=F('mor_permissions')),
#                 output_field=IntegerField()
#             ),
#         )

#     @response_modify_decorator_list_after_execution
#     def list(self, request, *args, **kwargs):
#         response = super(OtherListWithPermissionByRoleModuleNameView, self).list(
#             request, args, kwargs)
#         print('data', response.data)
#         for data in response.data:
#             # data['child'] = self.get_child_list(object_id=data['mmo_other'])
#             OtherDetails = Other.objects.filter(
#                 pk=data['mor_other'], cot_is_deleted=False)
#             # print('OtherDetails query',OtherDetails.query)
#             for e_OtherModuleDetails in OtherDetails:
#                 # print('OtherDetails',OtherDetails)
#                 # data['id'] = e_OtherModuleDetails.id
#                 data['cot_name'] = e_OtherModuleDetails.cot_name
#                 data['description'] = e_OtherModuleDetails.description
#                 data['cot_parent_id'] = e_OtherModuleDetails.cot_parent_id
#                 data['cot_is_deleted'] = e_OtherModuleDetails.cot_is_deleted

#         return response


class OtherListWithPermissionByUserModuleNameView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = OtherUser.objects.all()
    serializer_class = OtherListWithPermissionByUserModuleNameSerializer

    def get_queryset(self):
        module_name = self.kwargs['module_name']
        user_id = self.kwargs['user_id']
        result = OtherUser.objects.filter(
            mou_user=user_id,
            mou_module__name=module_name,
            mou_module__is_deleted=False,
            mou_is_deleted=False
        ).annotate(
            mou_permissions_n=Case(
                When(mou_permissions__isnull=True, then=Value(0)),
                When(mou_permissions__isnull=False, then=F('mou_permissions')),
                output_field=IntegerField()
            ),
        )
        if result:
            result = result
        else:
            pass
        return result

    @response_modify_decorator_list_after_execution
    def list(self, request, *args, **kwargs):
        response = super(OtherListWithPermissionByUserModuleNameView, self).list(
            request, args, kwargs)
        module_name = self.kwargs['module_name']
        user_id = self.kwargs['user_id']
        if response.data:
            for data in response.data:
                OtherDetails = Other.objects.filter(
                    pk=data['mou_other'], is_deleted=False)
                for e_OtherModuleDetails in OtherDetails:
                    data['name'] = e_OtherModuleDetails.name
                    data['description'] = e_OtherModuleDetails.description
                    data['parent_id'] = e_OtherModuleDetails.parent_id
                    data['is_deleted'] = e_OtherModuleDetails.is_deleted
        else:
            pass
        return response


class OtherEditNewView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Other.objects.all()
    serializer_class = OtherEditNewSerializer

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

# DEPARTMENT #


class DepartmentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Department.cmobjects.all()
    serializer_class = DepartmentAddSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        department = self.request.query_params.get('department', None)
        child = self.request.query_params.get('child', None)
        name = self.request.query_params.get('name', None)
        code = self.request.query_params.get('code', None)
        hod = self.request.query_params.get('hod', None)
        if department:
            if child == '1':
                filter['parent_id'] = department
            else:
                filter['id'] = department
        if code:
            filter['code__icontains'] = code
        if name:
            filter['name__icontains'] = name
        if hod:
            filter['hod__in'] = hod

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        if not gf.check_unique(Department, request.data, 'code'):
            custom_exception_message(self, 'Department code')
        if not gf.check_unique(Department, request.data, 'name'):
            custom_exception_message(self, 'Department name')
        return super().post(request, *args, **kwargs)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)


class DepartmentMasterHodListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserDetail.objects.filter(is_active=True, is_hod=True)
    serializer_class = UserDetailSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter = {}
        sort_field = '-id'
        department = self.request.query_params.get('department_id', None)
        if department:
            filter['department_id'] = department
        result = self.queryset.filter(**filter).order_by(sort_field)
        return result

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)


class DepartmentEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Department.objects.all()
    serializer_class = DepartmentAddSerializer

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        if not gf.check_unique(Department, request.data, 'code',skip_id=kwargs['pk']):
            custom_exception_message(self, 'Department code')
        if not gf.check_unique(Department, request.data, 'name',skip_id=kwargs['pk']):
            custom_exception_message(self, 'Department name')
        return super().update(request, *args, **kwargs)

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.deleted_at = datetime.now()
            instance.deleted_by = self.request.user
            instance.save()
            # update hod to the new department id provided in the API call
            new_department_id = self.request.query_params.get(
                'new_department_id', None)
            if new_department_id:
                UserDetail.objects.filter(department=instance, is_hod=True).update(
                    department=new_department_id)

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

# COMPANY #


class CompanyAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Company.cmobjects.all()
    serializer_class = CompanyAddSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        name = self.request.query_params.get('name', None)
        code = self.request.query_params.get('code', None)
        short_name = self.request.query_params.get('short_name', None)
        email_id_1 = self.request.query_params.get('email_id_1', None)
        email_id_2 = self.request.query_params.get('email_id_2', None)
        if code:
            filter['code__icontains'] = code
        if name:
            filter['name__icontains'] = name
        if short_name:
            filter['short_name__icontains'] = short_name
        if email_id_1:
            filter['email_id_1__icontains'] = email_id_1
        if email_id_2:
            filter['email_id_2__icontains'] = email_id_2

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        if not gf.check_unique(Company, request.data, 'code'):
            custom_exception_message(self, 'Company code')
        if not gf.check_unique(Company, request.data, 'name'):
            custom_exception_message(self, 'Company name')
        return super().post(request, *args, **kwargs)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)


class CompanyMasterCategoryListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Category.cmobjects.all()
    serializer_class = CategoryAddSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter = {}
        sort_field = '-id'
        company = self.request.query_params.get('company_id', None)
        if company:
            filter['company_id'] = company
        result = self.queryset.filter(**filter).order_by(sort_field)
        return result

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)


class CompanyEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Company.objects.all()
    serializer_class = CompanyAddSerializer

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        if not gf.check_unique(Company, request.data, 'code',skip_id=kwargs['pk']):
            custom_exception_message(self, 'Company code')
        if not gf.check_unique(Company, request.data, 'name',skip_id=kwargs['pk']):
            custom_exception_message(self, 'Company name')
        return super().update(request, *args, **kwargs)

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.deleted_at = datetime.now()
            instance.deleted_by = self.request.user
            instance.save()
            # update all users to the new comapny id provided in the API call
            new_company_id = self.request.query_params.get(
                'new_company_id', None)
            if new_company_id:
                Category.objects.filter(company=instance).update(
                    company=new_company_id)

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

# RelationShip #


# class AllModuleRoleRelationMapping(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     serializer_class = ModuleSerializer
#     queryset = Module.cmobjects.all()

#     def get_child_list(self, role_id: int) -> list:
#         try:
#             childlist = []
#             childlist_data = Role.objects.filter(
#                 cr_parent_id=role_id, cr_is_deleted=False)

#             for child in childlist_data:
#                 data_dict = collections.OrderedDict()
#                 # print('child::',child)
#                 data_dict['id'] = child.id
#                 data_dict['cr_name'] = child.cr_name
#                 data_dict['cr_parent_id'] = child.cr_parent_id
#                 data_dict['child'] = self.get_child_list(role_id=child.id)
#                 data_dict['cr_is_deleted'] = child.cr_is_deleted
#                 # print('data_dict:: ', data_dict)
#                 childlist.append(data_dict)
#             return childlist

#         except Exception as e:
#             raise e

#     @response_modify_decorator_list_after_execution
#     def list(self, request, *args, **kwargs):
#         try:
#             response = super(AllModuleRoleRelationMapping,
#                              self).list(request, args, kwargs)
#             data_list = []
#             print('response', response.data)
#             for mmro_data in response.data:
#                 tMasterModuleRoleDetails = ModuleRole.objects.filter(
#                     mmro_role__cr_parent_id=0,
#                     mmro_role__cr_is_deleted=False,
#                     mmro_module_id=mmro_data['id']).order_by('-mmro_role__cr_parent_id')
#                 print('tMasterModuleRoleDetails', tMasterModuleRoleDetails)
#                 parent_role_list = list()
#                 for e_tMasterModuleRoleDetails in tMasterModuleRoleDetails:
#                     parent_role_details = {
#                         'id': e_tMasterModuleRoleDetails.mmro_role.id,
#                         'cr_name': e_tMasterModuleRoleDetails.mmro_role.cr_name,
#                         'cr_parent_id': e_tMasterModuleRoleDetails.mmro_role.cr_parent_id,
#                         'cr_is_deleted': e_tMasterModuleRoleDetails.mmro_role.cr_is_deleted,
#                         'child': self.get_child_list(role_id=e_tMasterModuleRoleDetails.mmro_role.id)
#                     }
#                     parent_role_list.append(parent_role_details)
#                 mmro_data['mmro_role'] = parent_role_list

#             return response
#         except Exception as e:
#             raise APIException({'request_status': 0, 'msg': e, 'error': e})


# class RolesByModuleName(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = ModuleRole.objects.filter(mmro_is_deleted=False)
#     serializer_class = ModuleRoleSerializer
#     lookup_fields = ('mmro_module_name',)

#     def get_queryset(self):
#         try:
#             mmro_module_name = self.kwargs['mmro_module_name']
#             p = ModuleRole.objects.filter(
#                 mmro_module__name=mmro_module_name,
#                 mmro_role__cr_is_deleted=False).order_by('-id')

#             return p

#         except Exception as e:
#             raise APIException({'request_status': 0, 'msg': e, 'error': e})

#     @response_modify_decorator_get
#     def get(self, request, *args, **kwargs):
#         return response


# class AssignPermissonToRoleAddNewView(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     # pagination_class =CSPageNumberPagination
#     queryset = OtherRole.objects.all()
#     serializer_class = AssignPermissonToRoleAddNewSerializer


# class ModuleRoleCreateNewView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     # pagination_class =CSPageNumberPagination
#     queryset = ModuleRole.objects.all()
#     serializer_class = ModuleRoleNewSerializer


class AssignPermissonToUserAddNewView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # pagination_class =CSPageNumberPagination
    queryset = OtherUser.objects.all()
    serializer_class = AssignPermissonToUserAddNewSerializer


# CATEGORY #

class CategoryAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Category.cmobjects.all()
    serializer_class = CategoryAddSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        category = self.request.query_params.get('category', None)
        code = self.request.query_params.get('code', None)
        name = self.request.query_params.get('name', None)
        company = self.request.query_params.get('company', None)
        if category:
            filter['id'] = category
        if name:
            filter['name__icontains'] = name
        if code:
            filter['code__icontains'] = code
        if company:
            filter['company_id__in'] = company.split(',')

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):

        if not gf.check_unique(Category, request.data, 'code'):
                custom_exception_message(self, 'Category code')
        if not gf.check_unique(Category, request.data, 'name'):
                custom_exception_message(self, 'Category name')

        return super().post(request, *args, **kwargs)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)


class CategoryMasterDepartmentListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Department.cmobjects.all()
    serializer_class = DepartmentAddSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter = {}
        sort_field = '-id'
        category = self.request.query_params.get('category_id', None)
        if category:
            filter['category_id'] = category
        result = self.queryset.filter(**filter).order_by(sort_field)
        return result

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)


class CategoryEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Category.objects.all()
    serializer_class = CategoryAddSerializer

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        if not gf.check_unique(Category, request.data, 'code',skip_id=kwargs['pk']):
                custom_exception_message(self, 'Category code')
        if not gf.check_unique(Category, request.data, 'name',skip_id=kwargs['pk']):
                custom_exception_message(self, 'Category name')
        return super().update(request, *args, **kwargs)

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.deleted_at = datetime.now()
            instance.deleted_by = self.request.user
            instance.save()
            # update all users to the new category id provided in the API call
            new_category_id = self.request.query_params.get(
                'new_category_id', None)
            if new_category_id:
                Department.objects.filter(category=instance).update(
                    category=new_category_id)

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)


class TemplateMasterView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = TemplateMaster.cmobjects.all()
    serializer_class = TemplateMasterSerializer

    def get(self, request, *args, **kwargs):
        response = super(__class__, self).get(self, request, *args, **kwargs)
        obj = None
        if len(response.data) > 0:
            obj = response.data[0]
        return Response(data=obj, status=200)

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        template_name = self.request.query_params.get('template_name', None)
        if template_name:
            filter['template_name'] = template_name

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

class TemplateMasterEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = TemplateMaster.cmobjects.all()
    serializer_class = TemplateMasterSerializer

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


