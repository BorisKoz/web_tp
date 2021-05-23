"""web_tp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.conf.urls import url, include
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from ask_me import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^question/(?P<pk>\d+)/', views.one_question, name='question'),
    path('tag/<int:pk>', views.one_tag, name='tag_questions'),
    path('hot/', views.hot_index, name='hot_index'),
    path('login/', views.log_in, name='login'),
    path('accounts/login/', views.log_in, name='login'),
    path('logout/',  views.log_out, name='logout'),
    path('signup/', views.sign_up, name='sign_up'),
    path('profile/edit/', views.edit, name='edit_user'),
    path('ask/', views.ask, name='ask'),
    path('vote/', views.vote, name='vote'),
    path('correct/', views.is_correct, name='correct'),
    url(r'^$', views.index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
