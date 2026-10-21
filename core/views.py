from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from subscription.decorators import subscription_required, contract_required
from subscription.models import Notification
from doctors.models import Doctor
import json


def login_view(request):
    """Login view"""
    # Redirect to dashboard if already logged in
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect to next page or dashboard
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'auth/login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('core:login')


@login_required
@subscription_required
@contract_required
def dashboard(request):
    """Render the main dashboard based on subscription plan."""
    if not hasattr(request, 'company') or not request.company:
        messages.error(request, 'Şirkət məlumatı tapılmadı.')
        return redirect('core:login')
    
    # Get active subscription and plan
    subscription = request.company.active_subscription
    plan_type = 'basic'  # Default
    
    if subscription and subscription.plan:
        plan_type = subscription.plan.plan_type
    else:
        # Debug: Log if subscription or plan is missing
        import logging
        logger = logging.getLogger(__name__)
        if not subscription:
            logger.warning(f"No active subscription found for company: {request.company.name}")
        elif not subscription.plan:
            logger.warning(f"Subscription found but no plan assigned for company: {request.company.name}")
    
    # Get statistics based on plan level
    from doctors.models import Doctor
    from prescriptions.models import Prescription
    from sales.models import Sale
    from drugs.models import Drug
    from django.utils import timezone
    from datetime import timedelta
    from decimal import Decimal
    
    # Basic stats (available for all plans)
    total_doctors = Doctor.objects.count()
    total_drugs = Drug.objects.filter(is_active=True).count()
    
    # Get date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Prescription stats
    total_prescriptions = Prescription.objects.count()
    prescriptions_last_30 = Prescription.objects.filter(date__gte=last_30_days).count()
    prescriptions_last_7 = Prescription.objects.filter(date__gte=last_7_days).count()
    
    # Sales stats (for professional and enterprise)
    total_sales = 0
    sales_last_30 = 0
    sales_revenue = Decimal('0.00')
    if plan_type in ['professional', 'enterprise']:
        total_sales = Sale.objects.count()
        sales_last_30 = Sale.objects.filter(date__gte=last_30_days).count()
        # Calculate revenue from sales (sum from SaleItem using F expressions)
        from django.db.models import Sum, F
        from sales.models import SaleItem
        revenue_result = SaleItem.objects.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )
        sales_revenue = revenue_result['total'] or Decimal('0.00')
    
    # Recent prescriptions - safely handle potential DecimalField errors
    try:
        recent_prescriptions_qs = Prescription.objects.select_related(
            'doctor', 'region'
        ).order_by('-date')[:5]
        
        # Convert to list of dicts to avoid accessing problematic properties
        recent_prescriptions_list = []
        for prescription in recent_prescriptions_qs:
            try:
                # Safely calculate drug_count without accessing items
                from prescriptions.models import PrescriptionItem
                drug_count = PrescriptionItem.objects.filter(
                    prescription_id=prescription.id
                ).count()
                
                # Safely calculate total_amount - handle invalid Decimal values
                from django.db.models import Sum, F, Q
                try:
                    # Filter out items with invalid unit_price
                    total_result = PrescriptionItem.objects.filter(
                        prescription_id=prescription.id
                    ).exclude(
                        Q(unit_price__isnull=True) | Q(unit_price='')
                    ).aggregate(
                        total=Sum(F('quantity') * F('unit_price'))
                    )
                    total_amount = total_result['total'] or Decimal('0.00')
                except (TypeError, ValueError):
                    # If aggregation fails due to invalid data, calculate manually
                    total_amount = Decimal('0.00')
                    try:
                        items = PrescriptionItem.objects.filter(
                            prescription_id=prescription.id
                        ).only('quantity', 'unit_price')
                        for item in items:
                            try:
                                if item.unit_price and item.quantity:
                                    total_amount += Decimal(str(item.unit_price)) * Decimal(str(item.quantity))
                            except (TypeError, ValueError, AttributeError):
                                continue
                    except Exception:
                        total_amount = Decimal('0.00')
                
                recent_prescriptions_list.append({
                    'id': prescription.id,
                    'date': prescription.date,
                    'is_active': prescription.is_active,
                    'doctor': prescription.doctor,
                    'region': prescription.region,
                    'drug_count': drug_count,
                    'total_amount': total_amount,
                })
            except Exception:
                # Skip problematic prescriptions
                continue
        recent_prescriptions = recent_prescriptions_list
    except Exception:
        # If there's an error, return empty list
        recent_prescriptions = []
    
    # Top doctors by prescription count (for professional and enterprise)
    top_doctors = []
    if plan_type in ['professional', 'enterprise']:
        from django.db.models import Count
        try:
            # Get top doctors - use select_related to avoid N+1 queries, but don't access items
            top_doctors_qs = Doctor.objects.select_related('region').annotate(
                prescription_count=Count('prescriptions', distinct=True)
            ).order_by('-prescription_count')[:5]
            
            # Convert to list to avoid queryset evaluation issues with related data
            top_doctors_list = []
            for doctor in top_doctors_qs:
                try:
                    # Safely access region without triggering related queries
                    region_data = None
                    if doctor.region_id:
                        try:
                            region_data = {
                                'id': doctor.region.id,
                                'name': doctor.region.name,
                            }
                        except Exception:
                            pass
                    
                    top_doctors_list.append({
                        'id': doctor.id,
                        'ad': doctor.ad,
                        'code': doctor.code,
                        'region': region_data,
                        'prescription_count': doctor.prescription_count or 0,
                    })
                except Exception:
                    continue
            top_doctors = top_doctors_list
        except Exception:
            top_doctors = []
    
    # Monthly prescription trend (for enterprise)
    monthly_trend = []
    if plan_type == 'enterprise':
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        
        try:
            monthly_trend_qs = Prescription.objects.annotate(
                month=TruncMonth('date')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')[:12]
            
            # Convert date objects to strings for JSON serialization
            monthly_trend = [
                {
                    'month': item['month'].strftime('%Y-%m-%d') if item['month'] else None,
                    'count': item['count']
                }
                for item in monthly_trend_qs
            ]
        except Exception:
            monthly_trend = []
    
    # Region distribution (for enterprise)
    region_stats = []
    if plan_type == 'enterprise':
        from django.db.models import Count
        from regions.models import Region
        
        region_stats = Region.objects.annotate(
            prescription_count=Count('prescriptions')
        ).order_by('-prescription_count')[:5]
    
    # Chart data - Last 30 days prescription trend
    prescription_chart_data = []
    prescription_chart_labels = []
    if plan_type in ['professional', 'enterprise']:
        from django.db.models import Count
        for i in range(30):
            date = today - timedelta(days=29-i)
            count = Prescription.objects.filter(date=date).count()
            prescription_chart_data.append(count)
            prescription_chart_labels.append(date.strftime('%d.%m'))
    
    # Chart data - Last 30 days sales/revenue trend
    sales_chart_data = []
    revenue_chart_data = []
    sales_chart_labels = []
    if plan_type in ['professional', 'enterprise']:
        from django.db.models import Sum, F
        from sales.models import SaleItem
        for i in range(30):
            date = today - timedelta(days=29-i)
            sales_count = Sale.objects.filter(date=date).count()
            sales_chart_data.append(sales_count)
            
            # Revenue for this day
            revenue_result = SaleItem.objects.filter(
                sale__date=date
            ).aggregate(
                total=Sum(F('quantity') * F('unit_price'))
            )
            revenue = float(revenue_result['total'] or 0)
            revenue_chart_data.append(revenue)
            
            sales_chart_labels.append(date.strftime('%d.%m'))
    
    # Chart data - Last 12 months trend (for sparklines and monthly chart)
    monthly_prescription_data = []
    monthly_sales_data = []
    monthly_revenue_data = []
    monthly_labels = []
    if plan_type in ['professional', 'enterprise']:
        from django.db.models import Count, Sum, F
        from django.db.models.functions import TruncMonth
        from sales.models import SaleItem
        
        # Get last 12 months
        for i in range(12):
            month_start = (today.replace(day=1) - timedelta(days=32*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Prescriptions count
            pres_count = Prescription.objects.filter(
                date__gte=month_start,
                date__lte=month_end
            ).count()
            monthly_prescription_data.append(pres_count)
            
            # Sales count
            sales_count = Sale.objects.filter(
                date__gte=month_start,
                date__lte=month_end
            ).count()
            monthly_sales_data.append(sales_count)
            
            # Revenue
            revenue_result = SaleItem.objects.filter(
                sale__date__gte=month_start,
                sale__date__lte=month_end
            ).aggregate(
                total=Sum(F('quantity') * F('unit_price'))
            )
            revenue = float(revenue_result['total'] or 0)
            monthly_revenue_data.append(revenue)
            
            monthly_labels.append(month_start.strftime('%b'))
    
    # Doctors trend (last 12 months) - approximate based on creation date
    doctors_trend_data = []
    if plan_type in ['professional', 'enterprise']:
        from doctors.models import Doctor
        for i in range(12):
            month_start = (today.replace(day=1) - timedelta(days=32*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Count doctors created up to this month
            count = Doctor.objects.filter(
                created_at__lte=month_end
            ).count() if hasattr(Doctor, 'created_at') else total_doctors
            doctors_trend_data.append(count)
    
    context = {
        'plan_type': plan_type,
        'subscription': subscription,
        # Basic stats
        'total_doctors': total_doctors,
        'total_drugs': total_drugs,
        'total_prescriptions': total_prescriptions,
        'prescriptions_last_30': prescriptions_last_30,
        'prescriptions_last_7': prescriptions_last_7,
        # Professional/Enterprise stats
        'total_sales': total_sales,
        'sales_last_30': sales_last_30,
        'sales_revenue': sales_revenue,
        # Lists
        'recent_prescriptions': recent_prescriptions,
        'top_doctors': top_doctors,
        'monthly_trend': json.dumps(monthly_trend) if monthly_trend else json.dumps([]),
        'region_stats': region_stats,
        # Chart data (JSON serialized)
        'prescription_chart_data': json.dumps(prescription_chart_data),
        'prescription_chart_labels': json.dumps(prescription_chart_labels),
        'sales_chart_data': json.dumps(sales_chart_data),
        'revenue_chart_data': json.dumps(revenue_chart_data),
        'sales_chart_labels': json.dumps(sales_chart_labels),
        'monthly_prescription_data': json.dumps(monthly_prescription_data),
        'monthly_sales_data': json.dumps(monthly_sales_data),
        'monthly_revenue_data': json.dumps(monthly_revenue_data),
        'monthly_labels': json.dumps(monthly_labels),
        'doctors_trend_data': json.dumps(doctors_trend_data),
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def profile(request):
    """Render the profile page."""
    return render(request, 'profile.html')


@login_required
def help_support(request):
    """Help and support page"""
    return render(request, 'help.html')


@login_required
@subscription_required
@contract_required
def settings(request):
    """Settings page"""
    doctors_count = Doctor.objects.count() if hasattr(request, 'company') else 0
    
    # Get backup settings and backups
    from subscription.models import BackupSettings, Backup
    backup_settings = None
    backups = []
    if hasattr(request, 'company') and request.company:
        try:
            backup_settings = BackupSettings.objects.get(company=request.company)
        except BackupSettings.DoesNotExist:
            pass
        
        backups = Backup.objects.filter(company=request.company)[:20]  # Last 20 backups
    
    context = {
        'doctors_count': doctors_count,
        'backup_settings': backup_settings,
        'backups': backups,
    }
    return render(request, 'settings.html', context)


@login_required
@subscription_required
@contract_required
def notifications(request):
    """View all notifications for the company"""
    if not hasattr(request, 'company') or not request.company:
        messages.error(request, 'Şirkət məlumatı tapılmadı.')
        return redirect('core:dashboard')
    
    # Get all notifications for this company
    notifications_list = Notification.objects.filter(
        company=request.company
    ).order_by('-created_at')
    
    # Filter by read status
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications_list = notifications_list.filter(is_read=False)
    elif filter_type == 'read':
        notifications_list = notifications_list.filter(is_read=True)
    elif filter_type == 'important':
        notifications_list = notifications_list.filter(is_important=True)
    
    # Mark as read if requested
    if request.GET.get('mark_read'):
        notification_id = request.GET.get('mark_read')
        try:
            notification = Notification.objects.get(
                id=notification_id,
                company=request.company
            )
            notification.mark_as_read()
            messages.success(request, 'Bildiriş oxunmuş kimi işarələndi.')
            return redirect('core:notifications')
        except Notification.DoesNotExist:
            messages.error(request, 'Bildiriş tapılmadı.')
    
    context = {
        'notifications': notifications_list,
        'filter_type': filter_type,
        'unread_count': Notification.objects.filter(
            company=request.company,
            is_read=False
        ).count(),
    }
    
    return render(request, 'notifications.html', context)


@login_required
@subscription_required
@contract_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read (AJAX endpoint)"""
    if not hasattr(request, 'company') or not request.company:
        return JsonResponse({'success': False, 'error': 'Company not found'}, status=400)
    
    try:
        notification = Notification.objects.get(
            id=notification_id,
            company=request.company
        )
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)


@login_required
@subscription_required
@contract_required
def get_notification_count(request):
    """Get unread notification count (AJAX endpoint)"""
    if not hasattr(request, 'company') or not request.company:
        return JsonResponse({'count': 0})
    
    count = Notification.objects.filter(
        company=request.company,
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})


@login_required
@subscription_required
@contract_required
@require_http_methods(["POST"])
def backup_settings(request):
    """Save backup settings"""
    if not hasattr(request, 'company') or not request.company:
        messages.error(request, 'Şirkət məlumatı tapılmadı.')
        return redirect('core:settings')
    
    from subscription.models import BackupSettings
    from django.utils import timezone
    from datetime import timedelta
    
    interval = request.POST.get('backup_interval', 'disabled')
    retention_days = int(request.POST.get('backup_retention', 30))
    
    backup_settings, created = BackupSettings.objects.get_or_create(
        company=request.company,
        defaults={
            'interval': interval,
            'retention_days': retention_days,
        }
    )
    
    if not created:
        backup_settings.interval = interval
        backup_settings.retention_days = retention_days
        backup_settings.save()
    
    # Calculate next backup time
    if interval != 'disabled':
        if interval == 'daily':
            backup_settings.next_backup = timezone.now() + timedelta(days=1)
        elif interval == 'weekly':
            backup_settings.next_backup = timezone.now() + timedelta(days=7)
        elif interval == 'monthly':
            backup_settings.next_backup = timezone.now() + timedelta(days=30)
        backup_settings.save()
    else:
        backup_settings.next_backup = None
        backup_settings.save()
    
    messages.success(request, 'Backup parametrləri yadda saxlandı!')
    return redirect('core:settings')


@login_required
@subscription_required
@contract_required
@require_http_methods(["POST"])
def create_backup(request):
    """Create manual backup"""
    if not hasattr(request, 'company') or not request.company:
        messages.error(request, 'Şirkət məlumatı tapılmadı.')
        return redirect('core:settings')
    
    from subscription.models import Backup, BackupSettings
    from django.conf import settings
    from django.utils import timezone
    from django.core.management import call_command
    from django.db import connections
    import os
    import subprocess
    from pathlib import Path
    import io
    
    company = request.company
    default_db = settings.DATABASES['default']
    db_label = str(default_db.get('NAME', 'default'))
    
    try:
        # Create backup directory if it doesn't exist
        backup_dir = Path(settings.BASE_DIR) / 'backups' / company.slug
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if using PostgreSQL or SQLite
        from decouple import config
        USE_POSTGRESQL = config('USE_POSTGRESQL', default=False, cast=bool)
        
        # Create backup file name with timestamp (SQL format)
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'{company.slug}_{timestamp}.sql'
        backup_path = backup_dir / backup_filename
        
        if USE_POSTGRESQL:
            # PostgreSQL backup using pg_dump
            try:
                db_config = default_db
                
                # Use pg_dump command
                pg_dump_cmd = [
                    'pg_dump',
                    '-h', db_config.get('HOST', 'localhost'),
                    '-p', str(db_config.get('PORT', '5432')),
                    '-U', db_config.get('USER', ''),
                    '-d', str(db_config.get('NAME', '')),
                    '--no-owner',
                    '--no-acl',
                    '-F', 'p',  # Plain text format
                ]
                
                # Set PGPASSWORD environment variable
                env = os.environ.copy()
                env['PGPASSWORD'] = db_config.get('PASSWORD', '')
                
                result = subprocess.run(
                    pg_dump_cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    check=True,
                    timeout=300,  # 5 minutes timeout
                    env=env
                )
                
                # Write SQL dump to file
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(f'-- PostgreSQL Database Backup\n')
                    f.write(f'-- Database: {db_label}\n')
                    f.write(f'-- Created: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                    f.write(f'-- Company: {company.name}\n\n')
                    f.write(result.stdout)
                
                file_size = backup_path.stat().st_size
                
            except FileNotFoundError:
                messages.error(request, 'pg_dump komutu tapılmadı! PostgreSQL client quraşdırılmamışdır.')
                return redirect('core:settings')
            except subprocess.CalledProcessError as e:
                messages.error(request, f'PostgreSQL backup xətası: {e.stderr}')
                return redirect('core:settings')
            except Exception as e:
                messages.error(request, f'Backup xətası: {str(e)}')
                return redirect('core:settings')
        else:
            # SQLite backup (single default database)
            db_path = Path(default_db['NAME'])
            
            if not db_path.exists():
                messages.error(request, 'Verilənlər bazası tapılmadı!')
                return redirect('core:settings')
            
            # Export database to SQL format using Python sqlite3 module
            import sqlite3
            
            try:
                # Connect to database and dump to SQL
                conn = sqlite3.connect(str(db_path))
                conn.row_factory = sqlite3.Row
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    # Write header
                    f.write(f'-- SQLite Database Backup\n')
                    f.write(f'-- Database: {db_label}\n')
                    f.write(f'-- Created: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                    f.write(f'-- Company: {company.name}\n\n')
                    
                    # Iterate through all tables and dump their data
                    cursor = conn.cursor()
                    
                    # Get all table names
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        
                        # Get table schema
                        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                        schema = cursor.fetchone()
                        if schema and schema[0]:
                            f.write(f'\n-- Table: {table_name}\n')
                            f.write(f'{schema[0]};\n\n')
                        
                        # Get table data
                        cursor.execute(f"SELECT * FROM {table_name}")
                        rows = cursor.fetchall()
                        
                        if rows:
                            # Get column names
                            cursor.execute(f"PRAGMA table_info({table_name})")
                            columns = [col[1] for col in cursor.fetchall()]
                            
                            # Write INSERT statements
                            for row in rows:
                                values = []
                                for value in row:
                                    if value is None:
                                        values.append('NULL')
                                    elif isinstance(value, str):
                                        # Escape single quotes
                                        escaped = value.replace("'", "''")
                                        values.append(f"'{escaped}'")
                                    elif isinstance(value, (int, float)):
                                        values.append(str(value))
                                    else:
                                        values.append(f"'{str(value)}'")
                                
                                f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
                    
                    conn.close()
                
                file_size = backup_path.stat().st_size
                
            except Exception as sql_error:
                # If SQL export fails, try subprocess as fallback
                try:
                    result = subprocess.run(
                        ['sqlite3', str(db_path), '.dump'],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        check=True,
                        timeout=30
                    )
                    
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(result.stdout)
                    
                    file_size = backup_path.stat().st_size
                except Exception as e:
                    messages.error(request, f'SQL export xətası: {str(e)}')
                    return redirect('core:settings')
        
        # Create backup record
        backup = Backup.objects.create(
            company=company,
            file_path=str(backup_path),
            file_name=backup_filename,
            file_size=file_size,
            status='success',
            created_by=request.user
        )
        
        # Update backup settings
        backup_settings, _ = BackupSettings.objects.get_or_create(company=company)
        backup_settings.last_backup = timezone.now()
        backup_settings.save()
        
        messages.success(request, f'Backup uğurla yaradıldı! ({backup_filename})')
        
    except Exception as e:
        # Create failed backup record
        Backup.objects.create(
            company=company,
            file_path='',
            file_name='',
            file_size=0,
            status='failed',
            error_message=str(e),
            created_by=request.user
        )
        messages.error(request, f'Backup yaradılarkən xəta baş verdi: {str(e)}')
    
    return redirect('core:settings')


@login_required
@subscription_required
@contract_required
def download_backup(request, backup_id):
    """Download backup file"""
    if not hasattr(request, 'company') or not request.company:
        messages.error(request, 'Şirkət məlumatı tapılmadı.')
        return redirect('core:settings')
    
    from subscription.models import Backup
    from django.http import FileResponse
    from pathlib import Path
    
    try:
        backup = Backup.objects.get(id=backup_id, company=request.company, status='success')
        backup_path = Path(backup.file_path)
        
        if backup_path.exists():
            return FileResponse(
                open(backup_path, 'rb'),
                as_attachment=True,
                filename=backup.file_name
            )
        else:
            messages.error(request, 'Backup faylı tapılmadı!')
    except Backup.DoesNotExist:
        messages.error(request, 'Backup tapılmadı!')
    except Exception as e:
        messages.error(request, f'Xəta: {str(e)}')
    
    return redirect('core:settings')


@login_required
@subscription_required
@contract_required
@require_http_methods(["POST"])
def delete_backup(request, backup_id):
    """Delete backup file"""
    if not hasattr(request, 'company') or not request.company:
        messages.error(request, 'Şirkət məlumatı tapılmadı.')
        return redirect('core:settings')
    
    from subscription.models import Backup
    from pathlib import Path
    import os
    
    try:
        backup = Backup.objects.get(id=backup_id, company=request.company)
        
        # Delete file if exists
        if backup.file_path:
            backup_path = Path(backup.file_path)
            if backup_path.exists():
                os.remove(backup_path)
        
        # Delete backup record
        backup.delete()
        
        messages.success(request, 'Backup silindi!')
    except Backup.DoesNotExist:
        messages.error(request, 'Backup tapılmadı!')
    except Exception as e:
        messages.error(request, f'Xəta: {str(e)}')
    
    return redirect('core:settings')
