"""
Chatbot API Views - Allow AI to query company database
These endpoints are called by n8n/AI to get company-specific data
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from subscription.decorators import subscription_required, contract_required
from .decorators import chatbot_required
from doctors.models import Doctor, DoctorPayment
from prescriptions.models import Prescription, PrescriptionItem
from sales.models import Sale, SaleItem

# Import archived report models if they exist
try:
    from reports.models import MonthlyDoctorReport
except ImportError:
    MonthlyDoctorReport = None


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_query_api(request):
    """
    API endpoint for AI chatbot to query company database
    Called by n8n workflow to get company-specific data
    
    Security: Can be protected with API key via CHATBOT_API_KEY setting
    """
    """
    API endpoint for AI chatbot to query company database
    Called by n8n workflow to get company-specific data
    
    Expected JSON payload:
    {
        "query_type": "doctor_debt" | "doctor_info" | "prescription_count" | "monthly_report" | etc.
        "parameters": {
            "doctor_name": "...",
            "month": 11,
            "year": 2025,
            ...
        },
        "company_id": 1,
        "session_id": "..."
    }
    """
    try:
        # Security: Verify API key if configured
        from django.conf import settings
        if hasattr(settings, 'CHATBOT_API_KEY') and settings.CHATBOT_API_KEY:
            api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
            if api_key != settings.CHATBOT_API_KEY:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid API key'
                }, status=401)
        
        data = json.loads(request.body)
        query_type = data.get('query_type', '').strip()
        parameters = data.get('parameters', {})
        company_id = data.get('company_id')
        session_id = data.get('session_id')
        
        # Import Company model
        from subscription.models import Company
        
        # Validate company_id (optional: falls back to the sole company)
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Company not found'
                }, status=404)
        else:
            company = Company.objects.first()
            if not company:
                return JsonResponse({
                    'success': False,
                    'error': 'company_id is required'
                }, status=400)
        
        # Set company in request for compatibility
        request.company = company
        
        # Route to appropriate query handler
        if query_type == 'doctor_debt':
            return handle_doctor_debt_query(request, parameters)
        elif query_type == 'doctor_info':
            return handle_doctor_info_query(request, parameters)
        elif query_type == 'prescription_count':
            return handle_prescription_count_query(request, parameters)
        elif query_type == 'monthly_report':
            return handle_monthly_report_query(request, parameters)
        elif query_type == 'doctor_list':
            return handle_doctor_list_query(request, parameters)
        elif query_type == 'recent_prescriptions':
            return handle_recent_prescriptions_query(request, parameters)
        elif query_type == 'sales_summary':
            return handle_sales_summary_query(request, parameters)
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unknown query_type: {query_type}'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing query: {str(e)}'
        }, status=500)


def handle_doctor_debt_query(request, parameters):
    """Get doctor's debt information"""
    doctor_name = parameters.get('doctor_name', '').strip()
    month = parameters.get('month')
    year = parameters.get('year')
    
    if not doctor_name:
        return JsonResponse({
            'success': False,
            'error': 'doctor_name parameter is required'
        }, status=400)
    
    try:
        # Search for doctor by name (partial match)
        doctors = Doctor.objects.filter(
            Q(ad__icontains=doctor_name) | Q(code__icontains=doctor_name)
        )
        
        if not doctors.exists():
            return JsonResponse({
                'success': True,
                'data': {
                    'found': False,
                    'message': f'"{doctor_name}" adlı həkim tapılmadı.'
                }
            })
        
        # If multiple doctors found, return list
        if doctors.count() > 1:
            doctor_list = []
            for doctor in doctors[:5]:  # Limit to 5
                doctor_list.append({
                    'id': doctor.id,
                    'name': doctor.ad,
                    'code': doctor.code,
                    'current_debt': float(doctor.yekun_borc) if doctor.yekun_borc else 0.0,
                })
            return JsonResponse({
                'success': True,
                'data': {
                    'found': True,
                    'multiple': True,
                    'doctors': doctor_list,
                    'message': f'"{doctor_name}" üçün {doctors.count()} həkim tapıldı. Zəhmət olmasa daha spesifik ad daxil edin.'
                }
            })
        
        # Single doctor found
        doctor = doctors.first()
        
        # Get debt information
        result = {
            'found': True,
            'doctor': {
                'id': doctor.id,
                'name': doctor.ad,
                'code': doctor.code,
                'current_debt': float(doctor.yekun_borc) if doctor.yekun_borc else 0.0,
                'previous_debt': float(doctor.evvelki_borc) if doctor.evvelki_borc else 0.0,
                'calculated_amount': float(doctor.hesablanmish_miqdar) if doctor.hesablanmish_miqdar else 0.0,
                'deleted_amount': float(doctor.silinen_miqdar) if doctor.silinen_miqdar else 0.0,
            }
        }
        
        # If month/year specified, check archived reports
        if month and year and MonthlyDoctorReport:
            try:
                archived_entry = MonthlyDoctorReport.objects.get(
                    doctor=doctor,
                    year=year,
                    month=month
                )
                
                # Get data from archived entry
                result['archived_month'] = {
                    'month': month,
                    'year': year,
                    'final_debt': float(archived_entry.yekun_borc) if archived_entry.yekun_borc else 0.0,
                    'calculated_amount': float(archived_entry.hesablanan) if archived_entry.hesablanan else 0.0,
                    'previous_debt': float(archived_entry.evvelki_borc) if archived_entry.evvelki_borc else 0.0,
                }
            except MonthlyDoctorReport.DoesNotExist:
                result['archived_month'] = None
                result['message'] = f'{year} ilinin {month} ayı hələ arxivləşdirilməyib.'
        
        # Format response message
        debt_amount = result['doctor']['current_debt']
        if month and year and result.get('archived_month'):
            debt_amount = result['archived_month']['final_debt']
            result['message'] = f'{doctor.ad} həkiminin {year} ilinin {month} ayındakı yekun borcu: {debt_amount:.2f} ₼'
        else:
            result['message'] = f'{doctor.ad} həkiminin cari yekun borcu: {debt_amount:.2f} ₼'
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error querying doctor debt: {str(e)}'
        }, status=500)


def handle_doctor_info_query(request, parameters):
    """Get detailed doctor information"""
    doctor_name = parameters.get('doctor_name', '').strip()
    
    if not doctor_name:
        return JsonResponse({
            'success': False,
            'error': 'doctor_name parameter is required'
        }, status=400)
    
    try:
        doctor = Doctor.objects.filter(
            Q(ad__icontains=doctor_name) | Q(code__icontains=doctor_name)
        ).select_related('region', 'city', 'clinic', 'ixtisas').first()
        
        if not doctor:
            return JsonResponse({
                'success': True,
                'data': {
                    'found': False,
                    'message': f'"{doctor_name}" adlı həkim tapılmadı.'
                }
            })
        
        # Get prescription count
        prescription_count = Prescription.objects.filter(doctor=doctor).count()
        
        # Get recent payments
        recent_payments = DoctorPayment.objects.filter(
            doctor=doctor
        ).order_by('-date')[:3]
        
        payments_list = []
        for payment in recent_payments:
            try:
                payments_list.append({
                    'date': payment.date.strftime('%Y-%m-%d'),
                    'amount': float(payment.amount) if payment.amount else 0.0,
                    'type': payment.payment_type if hasattr(payment, 'payment_type') else 'unknown'
                })
            except Exception:
                continue
        
        result = {
            'found': True,
            'doctor': {
                'id': doctor.id,
                'name': doctor.ad,
                'code': doctor.code,
                'phone': doctor.telefon or 'Yoxdur',
                'email': doctor.email or 'Yoxdur',
                'region': doctor.region.name if doctor.region else 'Yoxdur',
                'specialization': doctor.ixtisas.name if doctor.ixtisas else 'Yoxdur',
                'degree': doctor.degree or 'Yoxdur',
                'category': doctor.category or 'Yoxdur',
                'current_debt': float(doctor.yekun_borc) if doctor.yekun_borc else 0.0,
                'prescription_count': prescription_count,
                'recent_payments': payments_list,
            },
            'message': f'{doctor.ad} həkiminin məlumatları uğurla tapıldı.'
        }
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error querying doctor info: {str(e)}'
        }, status=500)


def handle_prescription_count_query(request, parameters):
    """Get prescription count for a doctor or period"""
    doctor_name = parameters.get('doctor_name', '').strip()
    month = parameters.get('month')
    year = parameters.get('year')
    
    try:
        query = Prescription.objects.all()
        
        if doctor_name:
            doctor = Doctor.objects.filter(
                Q(ad__icontains=doctor_name) | Q(code__icontains=doctor_name)
            ).first()
            if doctor:
                query = query.filter(doctor=doctor)
            else:
                return JsonResponse({
                    'success': True,
                    'data': {
                        'found': False,
                        'message': f'"{doctor_name}" adlı həkim tapılmadı.'
                    }
                })
        
        if month and year:
            query = query.filter(date__year=year, date__month=month)
        
        count = query.count()
        
        message = f'Ümumi qeydiyyat sayı: {count}'
        if doctor_name and month and year:
            message = f'{doctor_name} həkiminin {year} ilinin {month} ayındakı qeydiyyat sayı: {count}'
        elif doctor_name:
            message = f'{doctor_name} həkiminin ümumi qeydiyyat sayı: {count}'
        elif month and year:
            message = f'{year} ilinin {month} ayındakı ümumi qeydiyyat sayı: {count}'
        
        return JsonResponse({
            'success': True,
            'data': {
                'count': count,
                'message': message
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error querying prescription count: {str(e)}'
        }, status=500)


def handle_monthly_report_query(request, parameters):
    """Get monthly report summary"""
    month = parameters.get('month')
    year = parameters.get('year')
    
    if not month or not year:
        # Use current month/year
        now = timezone.now()
        month = now.month
        year = now.year
    
    try:
        # Check if month is archived
        is_archived = False
        if MonthlyDoctorReport:
            try:
                entries = MonthlyDoctorReport.objects.filter(year=year, month=month)
                if entries.exists():
                    is_archived = True
                    total_doctors = entries.count()
                    total_debt = sum(float(entry.yekun_borc) if entry.yekun_borc else 0.0 for entry in entries)
                    
                    return JsonResponse({
                        'success': True,
                        'data': {
                            'month': month,
                            'year': year,
                            'archived': True,
                            'total_doctors': total_doctors,
                            'total_debt': total_debt,
                            'message': f'{year} ilinin {month} ayı arxivləşdirilib. Ümumi həkim sayı: {total_doctors}, Ümumi borc: {total_debt:.2f} ₼'
                        }
                    })
            except Exception:
                is_archived = False
        
        # Get live data
        prescriptions = Prescription.objects.filter(
            date__year=year,
            date__month=month
        )
        
        doctors_with_prescriptions = prescriptions.values('doctor').distinct().count()
        total_prescriptions = prescriptions.count()
        
        # Calculate total debt from current doctor data
        total_debt = sum(
            float(doctor.yekun_borc) if doctor.yekun_borc else 0.0
            for doctor in Doctor.objects.all()
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'month': month,
                'year': year,
                'archived': False,
                'doctors_with_prescriptions': doctors_with_prescriptions,
                'total_prescriptions': total_prescriptions,
                'total_debt': total_debt,
                'message': f'{year} ilinin {month} ayı üçün hesabat: {doctors_with_prescriptions} həkim, {total_prescriptions} qeydiyyat, Ümumi borc: {total_debt:.2f} ₼'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error querying monthly report: {str(e)}'
        }, status=500)


def handle_doctor_list_query(request, parameters):
    """Get list of doctors"""
    search_term = parameters.get('search', '').strip()
    limit = parameters.get('limit', 10)
    
    try:
        query = Doctor.objects.all()
        
        if search_term:
            query = query.filter(
                Q(ad__icontains=search_term) | Q(code__icontains=search_term)
            )
        
        doctors = query.select_related('region', 'ixtisas')[:limit]
        
        doctor_list = []
        for doctor in doctors:
            try:
                doctor_list.append({
                    'id': doctor.id,
                    'name': doctor.ad,
                    'code': doctor.code,
                    'region': doctor.region.name if doctor.region else 'Yoxdur',
                    'specialization': doctor.ixtisas.name if doctor.ixtisas else 'Yoxdur',
                    'current_debt': float(doctor.yekun_borc) if doctor.yekun_borc else 0.0,
                })
            except Exception:
                continue
        
        return JsonResponse({
            'success': True,
            'data': {
                'doctors': doctor_list,
                'count': len(doctor_list),
                'message': f'{len(doctor_list)} həkim tapıldı.'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error querying doctor list: {str(e)}'
        }, status=500)


def handle_recent_prescriptions_query(request, parameters):
    """Get recent prescriptions"""
    limit = parameters.get('limit', 5)
    doctor_name = parameters.get('doctor_name', '').strip()
    
    try:
        query = Prescription.objects.select_related('doctor', 'region').order_by('-date')
        
        if doctor_name:
            doctor = Doctor.objects.filter(
                Q(ad__icontains=doctor_name) | Q(code__icontains=doctor_name)
            ).first()
            if doctor:
                query = query.filter(doctor=doctor)
        
        prescriptions = query[:limit]
        
        prescription_list = []
        for prescription in prescriptions:
            try:
                prescription_list.append({
                    'id': prescription.id,
                    'date': prescription.date.strftime('%Y-%m-%d'),
                    'doctor': prescription.doctor.ad if prescription.doctor else 'Yoxdur',
                    'region': prescription.region.name if prescription.region else 'Yoxdur',
                })
            except Exception:
                continue
        
        return JsonResponse({
            'success': True,
            'data': {
                'prescriptions': prescription_list,
                'count': len(prescription_list),
                'message': f'Son {len(prescription_list)} qeydiyyat tapıldı.'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error querying recent prescriptions: {str(e)}'
        }, status=500)


def handle_sales_summary_query(request, parameters):
    """Get sales summary"""
    month = parameters.get('month')
    year = parameters.get('year')
    
    try:
        query = Sale.objects.all()
        
        if month and year:
            query = query.filter(date__year=year, date__month=month)
        
        total_sales = query.count()
        
        # Calculate total revenue
        total_revenue = Decimal('0.00')
        for sale in query:
            try:
                # Calculate from sale items
                sale_items = SaleItem.objects.filter(sale=sale)
                sale_total = sum(
                    float(item.quantity * item.unit_price) 
                    for item in sale_items 
                    if item.quantity and item.unit_price
                )
                total_revenue += Decimal(str(sale_total))
            except Exception:
                continue
        
        message = f'Ümumi satış sayı: {total_sales}, Ümumi gəlir: {float(total_revenue):.2f} ₼'
        if month and year:
            message = f'{year} ilinin {month} ayı üçün: {total_sales} satış, {float(total_revenue):.2f} ₼ gəlir'
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_sales': total_sales,
                'total_revenue': float(total_revenue),
                'message': message
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error querying sales summary: {str(e)}'
        }, status=500)

