from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('prestamos.urls')),
    path('api/', include('backend.urls')),
    # Redirección de /portfolio/ a la página principal
    path('portfolio/', RedirectView.as_view(url='/')),
]
