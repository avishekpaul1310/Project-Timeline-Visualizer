from django.contrib import admin
from django.urls import path, include
from timeline_app.views import logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('timeline_app.urls', namespace='timeline_app')),
    path('accounts/logout/', logout_view, name='logout'),  # Add this before django.contrib.auth.urls
    path('accounts/', include('django.contrib.auth.urls')),
]