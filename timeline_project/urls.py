from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('timeline_app.urls', namespace='timeline_app')),
    path('accounts/', include('django.contrib.auth.urls')),
]