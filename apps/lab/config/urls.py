"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path

from authn.views import (
    home,
    oidc_backchannel_logout,
    oidc_callback,
    oidc_logged_out,
    oidc_login,
    oidc_logout,
    private_page,
)

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("auth/login/", oidc_login, name="oidc_login"),
    path("auth/callback/", oidc_callback, name="oidc_callback"),
    path("private/", private_page, name="private"),
    path("auth/logout/", oidc_logout, name="oidc_logout"),
    path("auth/logged-out/", oidc_logged_out, name="oidc_logged_out"),
        path(
        "auth/backchannel-logout/",
        oidc_backchannel_logout,
        name="oidc_backchannel_logout",
    ),
]
