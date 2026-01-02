from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import os

def favicon_view(request):
    from django.conf import settings
    favicon_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', 'favicon-32x32.png')
    try:
        with open(favicon_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/png')
    except FileNotFoundError:
        return HttpResponse(status=404)

urlpatterns = [
    path('favicon.ico', favicon_view),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('testimonials/', include('testimonials.urls')),
    path('programs/', include('programs.urls')),
    path('donations/', include('donations.urls')),
    path('api/', include('api.urls')),
    path('staff/', include('staff_dashboard.urls', namespace='staff_dashboard')),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)