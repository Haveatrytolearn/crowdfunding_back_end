from django.urls import path
from . import views
 
urlpatterns = [
    path('fundraisers/', views.FundraiserList.as_view()),
    path('fundraisers/<int:pk>/', views.FundraiserDetail.as_view()),
    path("pledges/", views.PledgeList.as_view()),
    path("users/", views.UserList.as_view())
]