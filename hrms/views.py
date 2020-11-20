from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from hrms.models import *
from hrms.serializers import *
from custom_exception_message import *
from users.models import UserDetail
from users.serializers import UserDetailSerializer
import time
from multiplelookupfields import MultipleFieldLookupMixin
from rest_framework.views import APIView
from django.conf import settings
from pagination import CSLimitOffestpagination, CSPageNumberPagination, OnOffPagination
from rest_framework import filters
import calendar
from datetime import datetime
import collections
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q
from django_filters.rest_framework import DjangoFilterBackend
from users.models import UserDetail
from custom_decorator import *
from rest_framework.parsers import FileUploadParser
import os
from django.db import transaction, IntegrityError
from knox.auth import TokenAuthentication
from rest_framework import permissions
from knox.models import AuthToken
import global_function as gf


class HrmsMachineMasterView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsMachineMaster.cmobjects.all()
    serializer_class = HrmsMachineMasterSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            if field_name == 'company_name':
                field_name = 'company__name'
            if field_name == 'company_code':
                field_name = 'company__code'
            ordering = gf.get_ordering(field_name, order_by)

        machine_id = self.request.query_params.get('machine_id', None)
        company = self.request.query_params.get('company', None)
        company_name = self.request.query_params.get('company_name', None)
        company_code = self.request.query_params.get('company_code', None)
        if machine_id:
            filter['machine_id__icontains'] = machine_id
        if company:
            filter['company_id__in'] = company.split(',')
        if company_name:
            filter['company__name__icontains'] = company_name
        if company_code:
            filter['company__code__icontains'] = company_code

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            if not gf.check_unique(HrmsMachineMaster, request.data, 'machine_id'):
                custom_exception_message(self, 'Machine Id')
            response = super().post(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Create', previous_data=None, current_data=response.data)
            return response


class HrmsMachineMasterEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsMachineMaster.cmobjects.all()
    serializer_class = HrmsMachineMasterSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        with transaction.atomic():
            if not gf.check_unique(HrmsMachineMaster, request.data, 'machine_id', skip_id=kwargs['pk']):
                custom_exception_message(self, 'Machine Id')
            previous_data = HrmsMachineMaster.objects.filter(pk=kwargs['pk'], is_deleted=False).values(
                'id', 'machine_id', 'company', 'is_deleted')[0]
            response = super().update(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Update', previous_data=previous_data, current_data=response.data)
            return response

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = datetime.now()
        instance.deleted_by = self.request.user
        instance.save()


class HrmsShiftMasterView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsShiftMaster.cmobjects.all()
    serializer_class = HrmsShiftMasterSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            if field_name == 'company_name':
                field_name = 'company__name'
            if field_name == 'company_code':
                field_name = 'company__code'
            ordering = gf.get_ordering(field_name, order_by)

        shift_code = self.request.query_params.get('shift_code', None)
        company = self.request.query_params.get('company', None)
        company_name = self.request.query_params.get('company_name', None)
        company_code = self.request.query_params.get('company_code', None)
        if shift_code:
            filter['shift_code__icontains'] = shift_code
        if company:
            filter['company_id__in'] = company.split(',')
        if company_name:
            filter['company__name__icontains'] = company_name
        if company_code:
            filter['company__code__icontains'] = company_code

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            if not gf.check_unique(HrmsShiftMaster, request.data, 'shift_code'):
                custom_exception_message(self, 'Shift Code')
            response = super().post(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Create', previous_data=None, current_data=response.data)
            return response


class HrmsShiftMasterUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserDetail.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer
    pagination_class = OnOffPagination

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    def get_queryset(self):
        shift_id = self.request.query_params.get('shift_id', None)
        if shift_id:
            return self.queryset.filter(shift=shift_id)
        else:
            raise Exception('Provide shift_id in query parameter')


class HrmsShiftMasterEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsShiftMaster.cmobjects.all()
    serializer_class = HrmsShiftMasterSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        with transaction.atomic():
            if not gf.check_unique(HrmsShiftMaster, request.data, 'shift_code', skip_id=kwargs['pk']):
                custom_exception_message(self, 'Shift Code')
            previous_data = HrmsShiftMaster.objects.filter(pk=kwargs['pk'], is_deleted=False).values(
                'id', 'shift_code', 'company', 'is_deleted')[0]
            response = super().update(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Update', previous_data=previous_data, current_data=response.data)
            return response

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = datetime.now()
        instance.deleted_by = self.request.user
        instance.save()
        # update all users to the new shift id provided in the API call
        new_shift_id = self.request.query_params.get('new_shift_id', None)
        if new_shift_id:
            UserDetail.objects.filter(
                shift=instance).update(shift=new_shift_id)


class HrmsBusRouteMasterView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsBusRouteMaster.cmobjects.all()
    serializer_class = HrmsBusRouteMasterSerializer
    pagination_class = OnOffPagination
    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        route_no = self.request.query_params.get('route_no', None)
        route_name = self.request.query_params.get('route_name', None)
        if route_no:
            filter['route_no__icontains'] = route_no
        if route_name:
            filter['route_name__icontains'] = route_name

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            if not gf.check_unique(HrmsBusRouteMaster, request.data, 'route_no'):
                custom_exception_message(self, 'Route No')
            if not gf.check_unique(HrmsBusRouteMaster, request.data, 'route_name'):
                custom_exception_message(self, 'Route Name')
            response = super().post(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Create', previous_data=None, current_data=response.data)
            return response


class HrmsBusrouteMasterVehicleListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsVehicleMaster.cmobjects.all()
    serializer_class = HrmsVehicleMasterSerializer
    pagination_class = OnOffPagination

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    def get_queryset(self):
        bus_route_id = self.request.query_params.get('bus_route_id', None)
        if bus_route_id:
            return self.queryset.filter(bus_route=bus_route_id)
        else:
            raise Exception('Provide bus_route_id in query parameter')


class HrmsBusRouteMasterEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsBusRouteMaster.cmobjects.all()
    serializer_class = HrmsBusRouteMasterSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        with transaction.atomic():
            # Log History
            if not gf.check_unique(HrmsBusRouteMaster, request.data, 'route_no', skip_id=kwargs['pk']):
                custom_exception_message(self, 'Route No')
            if not gf.check_unique(HrmsBusRouteMaster, request.data, 'route_name', skip_id=kwargs['pk']):
                custom_exception_message(self, 'Route Name')
            previous_data = HrmsBusRouteMaster.objects.filter(pk=kwargs['pk'], is_deleted=False).values(
                'id', 'route_no', 'route_name', 'is_deleted')[0]
            response = super().update(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Update', previous_data=previous_data, current_data=response.data)
            return response

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.deleted_at = datetime.now()
            instance.deleted_by = self.request.user
            instance.save()
            # update all vehicles to the new bus route id provided in the API call
            new_bus_route_id = self.request.query_params.get(
                'new_bus_route_id', None)
            if new_bus_route_id:
                # Log History
                hrmsVehicleMaster = HrmsVehicleMaster.objects.filter(bus_route=instance)
                previous_data = hrmsVehicleMaster.values('id', 'vehicle_no', 'bus_route', 'is_deleted')[0]
                hrmsVehicleMaster.update(bus_route=new_bus_route_id)
                current_data = hrmsVehicleMaster.values('id', 'vehicle_no', 'bus_route', 'is_deleted')[0]
                gf.save_history(request, 'hrms', 'Update', previous_data=previous_data, current_data=current_data)


class HrmsVehicleMasterView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsVehicleMaster.cmobjects.all()
    serializer_class = HrmsVehicleMasterSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            if field_name == 'route_no':
                field_name = 'route__no'
            if field_name == 'route_name':
                field_name = 'route__name'
            ordering = gf.get_ordering(field_name, order_by)

        vehicle_no = self.request.query_params.get('vehicle_no', None)
        route_no = self.request.query_params.get('route_no', None)
        route_name = self.request.query_params.get('route_name', None)
        if vehicle_no:
            filter['vehicle_no__icontains'] = vehicle_no
        if route_no:
            filter['bus_route__no__icontains'] = route_no
        if route_name:
            filter['bus_route__name__icontains'] = route_name

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            if not gf.check_unique(HrmsVehicleMaster, request.data, 'vehicle_no'):
                custom_exception_message(self, 'Vehicle No')
            response = super().post(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Create', previous_data=None, current_data=response.data)
            return response


class HrmsVehicleMasterUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserDetail.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer
    pagination_class = OnOffPagination

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    def get_queryset(self):
        vehicle_id = self.request.query_params.get('vehicle_id', None)
        if vehicle_id:
            return self.queryset.filter(vehicle=vehicle_id)
        else:
            raise Exception('Provide vehicle_id in query parameter')


class HrmsVehicleMasterEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsVehicleMaster.cmobjects.all()
    serializer_class = HrmsVehicleMasterSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        with transaction.atomic():
            if not gf.check_unique(HrmsVehicleMaster, request.data, 'vehicle_no', skip_id=kwargs['pk']):
                custom_exception_message(self, 'Vehicle No')
            previous_data = HrmsVehicleMaster.objects.filter(pk=kwargs['pk'], is_deleted=False).values(
                'id', 'vehicle_no', 'bus_route', 'is_deleted')[0]
            response = super().update(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Update', previous_data=previous_data, current_data=response.data)
            return response

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.deleted_at = datetime.now()
            instance.deleted_by = self.request.user
            instance.save()
            # update all users to the new vehicle id provided in the API call
            new_vehicle_id = self.request.query_params.get('new_vehicle_id', None)
            if new_vehicle_id:
                UserDetail.objects.filter(
                    vehicle=instance).update(vehicle=new_vehicle_id)


class HrmsVehicleMasterUpdateUserListView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsVehicleMaster.cmobjects.all()
    serializer_class = HrmsVehicleMasterUpdateUserListSerializer

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        with transaction.atomic():
            previous_data = list(UserDetail.objects.filter(vehicle=kwargs['pk']).values_list('id'))
            response = super().update(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Update', previous_data=previous_data, current_data=response.data)
            return response


# region - Start Leave

class HrmsHolidayMasterView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsHolidayMaster.cmobjects.all()
    serializer_class = HrmsHolidayMasterSerializer
    pagination_class = OnOffPagination
    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-holiday_date'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            if field_name == 'company_name':
                field_name = 'company__name'
            if field_name == 'company_code':
                field_name = 'company__code'
            ordering = gf.get_ordering(field_name, order_by)

        company = self.request.query_params.get('company', None)
        company_name = self.request.query_params.get('company_name', None)
        company_code = self.request.query_params.get('company_code', None)
        if company:
            filter['company_id__in'] = company.split(',')
        if company_name:
            filter['company__name__icontains'] = company_name
        if company_code:
            filter['company__code__icontains'] = company_code

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            filtered_holidays = HrmsHolidayMaster.objects.filter(company=request.data['company'])
            if not gf.check_unique(filtered_holidays, request.data, 'holiday'):
                custom_exception_message(self, 'Holiday')
            if not gf.check_unique(filtered_holidays, request.data, 'holiday_date'):
                custom_exception_message(self, 'Holiday Date')
            response = super().post(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Create', previous_data=None, current_data=response.data)
            return response


class HrmsHolidayMasterEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsHolidayMaster.cmobjects.all()
    serializer_class = HrmsHolidayMasterSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        with transaction.atomic():
            # Log History
            previous_data = HrmsHolidayMaster.objects.filter(pk=kwargs['pk'], is_deleted=False).values(
                'id', 'holiday_date', 'holiday_date', 'adjustment_date', 'is_deleted')[0]
            response = super().update(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Update', previous_data=previous_data, current_data=response.data)
            return response

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.deleted_at = datetime.now()
            instance.deleted_by = self.request.user
            instance.save()


class HrmsLeaveMasterView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsLeaveMaster.cmobjects.all()
    serializer_class = HrmsLeaveMasterSerializer
    pagination_class = OnOffPagination
    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-leave_code'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        leave_code = self.request.query_params.get('leave_code', None)
        leave_type = self.request.query_params.get('leave_type', None)
        if leave_type:
            filter['leave_type'] = leave_type
        if leave_code:
            filter['leave_code__icontains'] = leave_code

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        response = super(__class__, self).get(self, request, *args, **kwargs)
        return response

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            filtered_holidays = HrmsLeaveMaster.objects.all()
            if not gf.check_unique(filtered_holidays, request.data, 'leave_code'):
                custom_exception_message(self, 'Leave Code')
            if not gf.check_unique(filtered_holidays, request.data, 'description'):
                custom_exception_message(self, 'Description')
            response = super().post(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Create', previous_data=None, current_data=response.data)
            return response


class HrmsGradeLeaveMappingView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsGradeLeaveMapping.cmobjects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return HrmsGradeLeaveMappingListSerializer
        else:
            return HrmsGradeLeaveMappingSerializer

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        grade_name = self.request.query_params.get('grade_name', None)
        year = self.request.query_params.get('year', None)
        if grade_name:
            filter['grade__name'] = grade_name
        if year:
            filter['year__in'] = year.split(',')
        else:
            filter['year__in'] = gf.get_current_financial_year()

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    def get(self, request, *args, **kwargs):
        response = super(__class__, self).get(self, request, *args, **kwargs)

        data_list = list()
        if response.data:
            id = 1
            for data in response.data:
                grade_details = data['grade_details']
                year = data['year']
                list_entry = [x for x in data_list if x['grade_details']['grade_id'] == grade_details['grade_id'] and x['year'] == year]
                if len(list_entry) == 0:
                    list_entry = {'id': id, 'grade_details': grade_details,  'year': year, 'leave_mapping': []}
                    data_list.append(list_entry)
                    id += 1
                else:
                    list_entry = list_entry[0]
                list_entry['leave_mapping'].append({
                    'leave_id': data['leave_details']['leave_id'],
                    'leave_code': data['leave_details']['leave_code'],
                    'leave_description': data['leave_details']['leave_description'],
                    'leave_quantity': data['quantity']
                })

        return Response(data=gf.create_pagination_data(self.request, data_list), status=200)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super().post(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Create', previous_data=None, current_data=response.data)
            return response


class HrmsHrmsGradeLeaveMappingEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsGradeLeaveMapping.cmobjects.all()
    serializer_class = HrmsGradeLeaveMappingSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        with transaction.atomic():
            # Log History
            previous_data = HrmsGradeLeaveMapping.objects.filter(pk=kwargs['pk'], is_deleted=False).values(
                'id', 'grade', 'designation', 'year', 'leave_master', 'quantity', 'is_deleted')[0]
            response = super().update(request, *args, **kwargs)
            gf.save_history(request, 'hrms', 'Update', previous_data=previous_data, current_data=response.data)
            return response

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.deleted_at = datetime.now()
            instance.deleted_by = self.request.user
            instance.save()


class LeaveHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsApprovalRequest.cmobjects.all()
    serializer_class = LeaveHistorySerializer

    def get_queryset(self):
        ordering = '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        employee = self.request.query_params.get('employee', None)

        if year and month:
            self.queryset = self.queryset.filter((Q(from_date__year=year) & Q(from_date__month=month)) |
                                                 (Q(to_date__year=year) & Q(to_date__month=month)))
        elif year:
            self.queryset = self.queryset.filter(from_date__year=year)

        return self.queryset.filter(employee=employee)

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# endregion

# Start Approval #
# Attendance

class AttendanceListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsAttendance.cmobjects.all()
    serializer_class = AttendanceListSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            if field_name == 'company_details.name':
                field_name = 'company__name'
            if field_name == 'company_details.code':
                field_name = 'company__code'
            ordering = gf.get_ordering(field_name, order_by)
        section = self.request.query_params.get('section', None)
        company = self.request.query_params.get('company', None)
        company_name = self.request.query_params.get('company_details.name', None)
        company_code = self.request.query_params.get('company_details.code', None)
        if section:
            filter['section'] = section
        if company:
            filter['company_id__in'] = company.split(',')
        if company_name:
            filter['company__name__icontains'] = company_name
        if company_code:
            filter['company__code__icontains'] = company_code

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response
        # with transaction.atomic():
        #     filtered_holidays = HrmsHolidayMaster.objects.filter(company=request.data['company'])
        #     if not gf.check_unique(filtered_holidays, request.data, 'holiday'):
        #         custom_exception_message(self, 'Holiday')
        #     if not gf.check_unique(filtered_holidays, request.data, 'holiday_date'):
        #         custom_exception_message(self, 'Holiday Date')
 

# Start Approval #

class ApprovalRequestAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsApprovalRequest.cmobjects.all()
    serializer_class = ApprovalRequestAddSerializer
    pagination_class = OnOffPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ApprovalRequestListSerializer
        return ApprovalRequestAddSerializer

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        # Soring or Ordering
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)

        if field_name and order_by:
            if field_name == 'department_name':
                field_name = 'employee__department__name'
            if field_name == 'username':
                field_name = 'employee__username'
            if field_name == 'card_no':
                field_name = 'employee__card_no'
            if field_name == 'name':
                field_name = 'employee__name'
            ordering = gf.get_ordering(field_name, order_by)
            
        # Filter
        approval_section = self.request.query_params.get('approval_section', None)
        voucher_no = self.request.query_params.get('status', None)
        leave_code = self.request.query_params.get('status', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        total_amount = self.request.query_params.get('total_amount', None)
        status = self.request.query_params.get('status', None)
        gate_type = self.request.query_params.get('gate_type', None)
        super_admin = self.request.query_params.get('super_admin', None)
        created_at = self.request.query_params.get('created_at', None)
        department_name = self.request.query_params.get('department_name', None)
        username = self.request.query_params.get('username', None)
        card_no = self.request.query_params.get('card_no', None)
        request_time = self.request.query_params.get('request_time', None)
        
        
        if department_name:
            filter['employee__department_id__in'] = department_name.split(',')
        if username:
            filter['employee__username__in'] = username.split(',')
        if card_no:
            filter['employee__card_no__in'] = card_no.split(',')
        if voucher_no:
            filter['voucher_no'] = voucher_no
        if leave_code:
            filter['leave_code__in'] = leave_code.split(',')
        if from_date:
            filter['from_date'] = from_date
        if to_date:
            filter['to_date'] = to_date
        if total_amount:
            filter['total_amount'] = total_amount
        if status:
            filter['status__in'] = status.split(',')
        if gate_type:
            filter['gate_type__in'] = gate_type.split(',')
        if super_admin:
            filter['super_admin'] = super_admin
        if created_at:
            filter['created_at__date'] = created_at
        if request_time:
            filter['request_time__date'] = request_time


        
        employee_id = self.request.query_params.get('employee_id', None)
        team = self.request.query_params.get('team', None) # [Employee with team memers]
        
        if approval_section:
            filter['approval_section'] = approval_section

            month = self.request.query_params.get('month', None)
            year = self.request.query_params.get('year', None)

            if approval_section in ['Tours','Leave']:
                if month and year:
                    filter['from_date__month__gte'] = month
                    filter['from_date__year__gte'] = year
                    filter['to_date__month__lte'] = month
                    filter['to_date__year__lte'] = year

            if approval_section in ['Card Replacement','Uniform Change','Get Pass']:
                if month and year:
                    filter['request_time__date__month__gte'] = month
                    filter['request_time__date__year__gte'] = year
                    filter['request_time__date__month__lte'] = month
                    filter['request_time__date__year__lte'] = year

            if approval_section in ['W/O Change']:
                if month and year:
                    filter['from_date__month__gte'] = month
                    filter['from_date__year__gte'] = year
                    filter['from_date__month__lte'] = month
                    filter['from_date__year__lte'] = year

            if approval_section in ['Canteen Punch','Miss Punch']:
                if month and year:
                    filter['punch_time__date__month__gte'] = month
                    filter['punch_time__date__year__gte'] = year
                    filter['punch_time__date__month__lte'] = month
                    filter['punch_time__date__year__lte'] = year

            if approval_section in ['Shift Change']:
                if month and year:
                    filter['created_at__date__month__gte'] = month
                    filter['created_at__date__year__gte'] = year
                    filter['created_at__date__month__lte'] = month
                    filter['created_at__date__year__lte'] = year

        
        if employee_id:
            # [ Only for Employee]
            filter['employee_id__in'] = employee_id.split(',')
            team = None # For Team Approval Section
            
        if team:
            # [Only team members]
            employee_id = self.request.user.id
            users = UserDetail.objects.filter(reporting_head_id=employee_id,is_active=True).values_list('id',flat=True)
            filter['employee_id__in'] = users

        # [For HR Section Approver type - POST]
        hr = self.request.query_params.get('hr', None)
        if hr:
           filter['current_approval_configuration__type'] = 'Post'
         
        # Final Queryset return
        self.queryset = self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)
        return self.queryset

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response
        # with transaction.atomic():
        #     filtered_holidays = HrmsHolidayMaster.objects.filter(company=request.data['company'])
        #     if not gf.check_unique(filtered_holidays, request.data, 'holiday'):
        #         custom_exception_message(self, 'Holiday')
        #     if not gf.check_unique(filtered_holidays, request.data, 'holiday_date'):
        #         custom_exception_message(self, 'Holiday Date')
            
class ApprovalRequestDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsApprovalRequestDocument.cmobjects.all()
    serializer_class = ApprovalRequestDocumentAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response


class ApprovalConfigListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsApprovalConfiguration.cmobjects.all()
    serializer_class = ApprovalConfigListSerializer
    pagination_class = OnOffPagination
    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        filter, exclude, ordering = {}, {}, '-id'

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:
            ordering = gf.get_ordering(field_name, order_by)

        section = self.request.query_params.get('section', None)
        if section:
            filter['section'] = section

        return self.queryset.filter(**filter).exclude(**exclude).order_by(ordering)

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)


class ApprovalStatusUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsApprovalRequest.cmobjects.all()
    serializer_class = ApprovalStatusUpdateSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super().update(request, *args, **kwargs)
            # gf.save_history(request, 'hrms', 'Update', previous_data=previous_data, current_data=response.data)
            return response


# End Approval #
