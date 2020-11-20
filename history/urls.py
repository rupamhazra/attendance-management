from django.urls import path
from history import views


urlpatterns = [
    path('history/add/', views.ActionHistoryAddView.as_view()),
    path('history/edit/<pk>/', views.ActionHistoryRetrieveDestoryView.as_view()),
]
