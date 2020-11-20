from master import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path

urlpatterns = [

    ## Applications ##
    path('permissions_list/', views.PermissionsListCreate.as_view()),
    path('add_application/', views.ModuleListCreate.as_view()),
    path('applications_list/', views.ModuleList.as_view()),
    path('edit_application/<pk>/', views.EditModuleById.as_view()),
    ## -- ##

    ## ROLE ##
    # add role and list of role
    #path('add_role/', views.RoleListCreate.as_view()),
    # add role and list of role
#     path('edit_role/<pk>/', views.RoleRetrieveUpdateAPIView.as_view()),
    ## -- ##

    ## OBJECTS ##
    path('other/add/', views.OtherAddView.as_view()),
    path('other/edit/<pk>/', views.OtherEditView.as_view()),
    path('other/edit_new/<pk>/', views.OtherEditNewView.as_view()),
    path('other/list/<module_name>/',
         views.OtherListNewView.as_view()),  # D
#     path('other_list_with_permission_by_role_module_name/<module_name>/<role_name>/',
#          views.OtherListWithPermissionByRoleModuleNameView.as_view()),
    path('other_list_with_permission_by_user_module_name/<module_name>/<user_id>/',
         views.OtherListWithPermissionByUserModuleNameView.as_view()),
    ## -- ##

    ## COMPANY ##
    path('company/add/', views.CompanyAddView.as_view()),
    # category list under company
    path('company/category/list/', views.CompanyMasterCategoryListView.as_view()),
    path('company/edit/<pk>/', views.CompanyEditView.as_view()),
    ## -- ##

    ## CATEGORY ##
    path('category/add/', views.CategoryAddView.as_view()),
    # department list under category
    path('category/department/list/',
         views.CategoryMasterDepartmentListView.as_view()),
    path('category/edit/<pk>/', views.CategoryEditView.as_view()),
    ## -- ##

    ## DEPARTMENT ##
    path('department/add/', views.DepartmentAddView.as_view()),
    # hod list under department
    path('department/hod/list/', views.DepartmentMasterHodListView.as_view()),
    path('department/edit/<pk>/', views.DepartmentEditView.as_view()),
    ## -- ##

    # ----- designation -------
    path('designation/add/', views.DesignationAddView.as_view()),
    # user_list - pass 'designation_id' in query param
    path('designation/user_list/', views.DesignationUserListView.as_view()),
    # edit - pass 'new_designation_id' in query param while deleting
    path('designation/edit/<pk>/', views.DesignationEditView.as_view()),
    # -----

    # ----- grade -------
    path('grade/add/', views.GradeAddView.as_view()),
    # user_list - pass 'grade_id' in query param
    path('grade/user_list/', views.GradeUserListView.as_view()),
    # edit - pass 'new_grade_id' in query param while deleting
    path('grade/edit/<pk>/', views.GradeEditView.as_view()),
    # -----

    # Role Creation in Module
#     path('module_role_create_new/', views.ModuleRoleCreateNewView.as_view()),

    # List of Roles in Modules
#     path('all_module_role_relation_mapping/',
#          views.AllModuleRoleRelationMapping.as_view()),  # D

    # Get roles by Module Name
#     path('roles_by_module_name/<mmro_module_name>/',
#          views.RolesByModuleName.as_view()),  # D

    # Assign Permisson to Object List by role
#     path('assign_permission_to_role_add_or_update_new/',
#          views.AssignPermissonToRoleAddNewView.as_view()),

    # Assign Permisson to Object List by user
    path('assign_permission_to_user_add_or_update_new/',
         views.AssignPermissonToUserAddNewView.as_view()),

    # ----- template master -------
    path('template_master/add/', views.TemplateMasterView.as_view()),
    path('template_master/edit/<pk>/', views.TemplateMasterEditView.as_view()),
    # -----
]
