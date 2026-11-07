from django.contrib import admin

from .models import MonthlyDoctorReport

admin.site.register(MonthlyDoctorReport)
class MonthlyDoctorReportAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'region', 'year', 'month', 'total_quantity', 'evvelki_borc', 'hesablanan', 'silinen_miqdar', 'avans', 'investisiya', 'geriqaytarma', 'datasiya', 'yekun_borc')
    search_fields = ('doctor__ad', 'region__name', 'year', 'month')
    list_filter = ('region', 'year', 'month')
    list_per_page = 100
    list_max_show_all = 100
    list_editable = ('evvelki_borc', 'hesablanan', 'silinen_miqdar', 'avans', 'investisiya', 'geriqaytarma', 'datasiya', 'yekun_borc')
    list_display_links = ('doctor', 'region', 'year', 'month')
    list_select_related = ('doctor', 'region')
    list_prefetch_related = ('doctor__region', 'doctor__items')
    list_per_page = 100
    list_max_show_all = 100
    list_editable = ('evvelki_borc', 'hesablanan', 'silinen_miqdar', 'avans', 'investisiya', 'geriqaytarma', 'datasiya', 'yekun_borc')
    list_display_links = ('doctor', 'region', 'year', 'month')
    list_select_related = ('doctor', 'region')
    list_prefetch_related = ('doctor__region', 'doctor__items')