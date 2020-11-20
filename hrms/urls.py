from django.urls import path
from hrms import views


urlpatterns = [
    # ----- machine master ------
    path('machine/add/', views.HrmsMachineMasterView.as_view()),
    path('machine/edit/<pk>/', views.HrmsMachineMasterEditView.as_view()),
    # -----

    # ----- shift master -------
    path('shift/add/', views.HrmsShiftMasterView.as_view()),
    # user_list - pass 'shift_id' in query param
    path('shift/user_list/', views.HrmsShiftMasterUserListView.as_view()),
    # edit - pass 'new_shift_id' in query param while deleting
    path('shift/edit/<pk>/', views.HrmsShiftMasterEditView.as_view()),
    # -----

    # ----- bus route master -------
    path('bus_route/add/', views.HrmsBusRouteMasterView.as_view()),
    # vehicle_list - pass 'bus_route_id' in query param
    path('bus_route/vehicle_list/', views.HrmsBusrouteMasterVehicleListView.as_view()),
    # edit - pass 'new_bus_route_id' in query param while deleting
    path('bus_route/edit/<pk>/', views.HrmsBusRouteMasterEditView.as_view()),
    # -----

    # ----- vehicle master -------
    # add - user_list field is mandatory, pass "[null]" if empty
    path('vehicle/add/', views.HrmsVehicleMasterView.as_view()),
    # user_list - pass 'vehicle_id' in query param
    path('vehicle/user_list/', views.HrmsVehicleMasterUserListView.as_view()),
    # edit - pass 'new_vehicle_id' in query param while deleting
    path('vehicle/edit/<pk>/', views.HrmsVehicleMasterEditView.as_view()),
    # update_user_list - user_list field is mandatory, pass "[null]" if empty
    path('vehicle/update_user_list/<pk>/', views.HrmsVehicleMasterUpdateUserListView.as_view()),
    # -----

    # ----- holiday master ------
    path('holiday/add/', views.HrmsHolidayMasterView.as_view()),
    path('holiday/edit/<pk>/', views.HrmsHolidayMasterEditView.as_view()),
    # -----

    # ----- holiday master ------
    path('leave_master/add/', views.HrmsLeaveMasterView.as_view()),
    # -----

    # ----- leave mapping ------
    path('leave_map/add/', views.HrmsGradeLeaveMappingView.as_view()),
    path('leave_map/edit/<pk>/', views.HrmsHrmsGradeLeaveMappingEditView.as_view()),
    path('leave/history/', views.LeaveHistoryView.as_view()),
    # -----

    # Approval #
    path('approval_request/add/', views.ApprovalRequestAddView.as_view()),
    path('approval_request/document/add/', views.ApprovalRequestDocumentAddView.as_view()),
    # --------
    path('approval_request/status_update/<pk>/', views.ApprovalStatusUpdateView.as_view()),
    path('approval_config/list/', views.ApprovalConfigListView.as_view()),

    # path

    # Attendance #
    path('attendance/list/', views.AttendanceListView.as_view()),
    # --------
]
