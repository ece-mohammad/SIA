"""
URL configuration for sia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from dashboard import views as dashboard_views


api_urlpatterns = [
    # api
    path("", include("api.urls")),
    
    # api authentication
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
]


urlpatterns = [
    # admin
    path("admin/", admin.site.urls),
    
    # accounts
    path("accounts/", include("accounts.urls")),

    # devices
    path("device/", include("devices.urls")),
    
    # dashboard
    path("dashboard", include("dashboard.urls")),

    path("api/", include(api_urlpatterns)),
    
    # homepage
    path("", dashboard_views.DashboardView.as_view(), name="homepage"),
    
    # debug toolbar 
    path('__debug__/', include('debug_toolbar.urls')),
]
