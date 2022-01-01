"""poktwatch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from explorer import views
from analytics import views as analytics

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index ),
    path('tx/<str:hash>', views.tx),
    path('address/<str:address>', views.account),
    path('search', views.search),
    path('block/<int:blocknum>',views.block),
    path("txs", views.txs),
    path('test', views.test),
    path('analytics',analytics.dashboard),
    path('api/accounts', views.apiAccountHash),
    path('api/rewards', views.api)
]

handler500 = 'explorer.views.handler500'
