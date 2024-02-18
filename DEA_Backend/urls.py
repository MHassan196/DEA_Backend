from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentication.urls')),
    path('main_api/', include('main_api.urls')),
    path('handwriting_recognition/', include('handwriting_recognition.urls'))
    # path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)