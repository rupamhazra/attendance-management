from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from history.models import *
from history.serializers import *
import time
from multiplelookupfields import MultipleFieldLookupMixin
from rest_framework.views import APIView
from django.conf import settings
from pagination import CSLimitOffestpagination, CSPageNumberPagination, OnOffPagination
from rest_framework import filters
import calendar
from datetime import datetime
import collections
from django_filters.rest_framework import DjangoFilterBackend
from custom_decorator import *
from rest_framework.parsers import FileUploadParser
import os
from django.db import transaction, IntegrityError
from knox.auth import TokenAuthentication
from rest_framework import permissions
from knox.models import AuthToken


class ActionHistoryAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ActionHistory.objects.filter(is_deleted=False)
    serializer_class = ActionHistoryAddSerializer
    pagination_class = OnOffPagination
    filter_backends = [filters.OrderingFilter]

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super(__class__, self).get(self, request, *args, **kwargs)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ActionHistoryRetrieveDestoryView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ActionHistory.objects.filter(is_deleted=False)
    serializer_class = ActionHistoryAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @response_modify_decorator_destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return self.perform_destroy(instance)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
