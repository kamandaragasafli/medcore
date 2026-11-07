from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    # Landing Page
    path('landing/', views.landing_page, name='landing'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & Pages
    path('', views.dashboard, name='dashboard'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/count/', views.get_notification_count, name='notification_count'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('help/', views.help_support, name='help'),
    
    # Backup
    path('settings/backup/', views.backup_settings, name='backup_settings'),
    path('settings/backup/create/', views.create_backup, name='create_backup'),
    path('settings/backup/<int:backup_id>/download/', views.download_backup, name='download_backup'),
    path('settings/backup/<int:backup_id>/delete/', views.delete_backup, name='delete_backup'),
]

