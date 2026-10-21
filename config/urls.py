from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('master-admin/', include('master_admin.urls')),  # Master Admin Panel (Superuser only)
    path('subscription/', include('subscription.urls')),  # SaaS subscription
    path('', include('core.urls')),
    path('doctors/', include('doctors.urls')),
    path('drugs/', include('drugs.urls')),
    path('prescriptions/', include('prescriptions.urls')),  # Prescription/Recipe Management
    path('regions/', include('regions.urls')),
    path('reports/', include('reports.urls')),
    path('sales/', include('sales.urls')),
]

if getattr(settings, 'CHATBOT_ENABLED', False):
    urlpatterns.append(path('chatbot/', include('chatbot.urls')))

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

