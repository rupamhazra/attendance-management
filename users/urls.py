from users import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from knox_views import views as knox_views

# For removing the group module on Django admin #
from django.contrib import admin
from django.contrib.auth.models import Group
#admin.site.unregister(Group)
# For removing the group module on Django admin #

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/', views.LoginView.as_view(), name='knox_login'),
    path('login/get_password/', views.LoginGetPasswordView.as_view(), name='knox_login'),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('change_password/', views.ChangePasswordView.as_view()),
    path('change_password_with_username/',views.ChangePasswordWithUsernameView.as_view()),
    #path('forgot_password/', views.ForgotPasswordView.as_view()),
    path('add/', views.CreateUserView.as_view()),
    path('edit/<pk>/', views.EditUserView.as_view()),
    path('list/', views.UserListView.as_view()),
    path('download_list/', views.UserListDownloadView.as_view()),
    # Assign module and role to user
    path('role_module_assign/',views.RoleModuleAssignView.as_view()),
    # Role List by Module for all users
    path('user_module_list/', views.ModuleUserList.as_view()),
    #list of users under Reporing head
    path('users_under_reporting_head/', views.UserListViewUnderReportingHead.as_view()),
    

]
