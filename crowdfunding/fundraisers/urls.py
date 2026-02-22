from django.urls import path
from . import views
 
urlpatterns = [
    path("fundraisers/restore/<int:pk>/", views.RestoreFundraiser.as_view()),
    path('fundraisers/', views.FundraiserList.as_view()),
    #path('fundraisers/deleted/', views.DeletedFundraiserList.as_view()),
    #path('fundraisers/deleted/<int:pk>/', views.DeletedFundraiserDetail.as_view()),
    path('fundraisers/<int:pk>/', views.FundraiserDetail.as_view()),
    path("pledges/", views.PledgeList.as_view()),
    path("pledges/<int:pk>/", views.PledgesDetail.as_view())
]