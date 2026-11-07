"""
Chatbot Views - AI Chatbot with OpenAI integration
Only available for Professional and Enterprise plans
"""
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from subscription.decorators import subscription_required, contract_required
from .decorators import chatbot_required
from django.contrib import messages

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None



@login_required
@subscription_required
@contract_required
@chatbot_required
def chatbot_view(request):
    """
    Main chatbot interface
    """
    # Get subscription and plan type explicitly
    subscription = None
    plan_type = None
    
    if hasattr(request, 'company') and request.company:
        subscription = request.company.active_subscription
        if subscription and subscription.plan:
            plan_type = subscription.plan.plan_type
    
    context = {
        'company_name': request.company.name if hasattr(request, 'company') else '',
        'subscription': subscription,
        'plan_type': plan_type,
    }
    return render(request, 'chatbot/chatbot.html', context)


@login_required
@subscription_required
@contract_required
@chatbot_required
@require_http_methods(["POST"])
def send_message(request):
    """
    Send message to OpenAI API and get AI response
    """
    try:
        # Check if OpenAI is available
        if OpenAI is None:
            return JsonResponse({
                'success': False,
                'error': 'OpenAI paketi quraşdırılmamışdır. Zəhmət olmasa openai paketini quraşdırın.'
            }, status=500)
        
        # Check if API key is configured
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            return JsonResponse({
                'success': False,
                'error': 'OpenAI API açarı təyin edilməyib. Zəhmət olmasa OPENAI_API_KEY təyin edin.'
            }, status=500)
        
        # Debug: Log the request
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Chatbot message received from user {request.user.id}")
        
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        logger.info(f"User message: {user_message[:50]}...")
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Mesaj boş ola bilməz'
            }, status=400)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Get conversation history from session
        conversation_history = request.session.get('chatbot_history', [])
        
        # Build system message with context
        company_name = request.company.name if hasattr(request, 'company') and request.company else 'Şirkət'
        
        # Read user guide for help support information
        from pathlib import Path
        guide_path = Path(settings.BASE_DIR) / 'AI_USER_GUIDE.md'
        user_guide_content = ""
        if guide_path.exists():
            try:
                with open(guide_path, 'r', encoding='utf-8') as f:
                    user_guide_content = f.read()
            except Exception as e:
                logger.warning(f"Could not read AI_USER_GUIDE.md: {e}")
        
        # Default fallback content
        default_content = """MedCor tibbi idarəetmə sistemidir. Sistemdə həkimlər, dərmanlar, resept qeydiyyatları, satışlar və hesabatlar idarə olunur.

Əsas funksiyalar:
- Həkim idarəetməsi: Həkimlərin siyahısı, əlavə etmə, detay səhifəsi
- Dərman idarəetməsi: Dərmanların siyahısı və əlavə etmə
- Resept qeydiyyatı: Reseptlərin əlavə edilməsi və siyahısı
- Satış idarəetməsi: Satışların əlavə edilməsi və redaktəsi
- Hesabatlar: Aylıq hesabatların yaradılması və bağlanması

Maliyyə hesablamaları avtomatikdir. Resept və ya satış əlavə edildikdə həkimin borc məlumatları avtomatik yenilənir."""
        
        guide_text = user_guide_content[:6000] if user_guide_content else default_content
        
        system_message = f"""Sən MedCor tibbi idarəetmə sisteminin köməkçi asistanısan. Şirkət adı: {company_name}

ƏSAS QAYDALAR:
1. Cavablarını həmişə Azərbaycan dilində ver
2. Qısa və aydın cavablar ver (maksimum 2-3 cümlə)
3. Admin panel, master admin, superuser, kod, texniki detallar haqqında danışma
4. Sadəcə istifadəçiyə kömək et - sistemdə necə işləməyi izah et
5. Help dəstəyi kimi işlə - praktik məsləhətlər ver

SİSTEM HAQQINDA MƏLUMAT (İSTİFADƏÇİ ÜÇÜN):
{guide_text}

NÜMUNƏ SUALLAR VƏ CAVABLAR:
- "Resept necə əlavə edim?" → "Bölgə seçin, həkim seçin, tarix seçin, dərmanlar üçün miqdar daxil edin və göndərin."
- "Həkim borcu necə hesablanır?" → "Həkimin borcu avtomatik hesablanır. Resept və satışlar üzrə komissiya hesablanır və həkimin dərəcəsinə görə faktor tətbiq edilir."
- "Excel import necə işləyir?" → "Excel faylında lazımi sütunları doldurun və import edin. Dərmanlar üçün: Ad, Tam Ad, Komissiya, Qiymət. Borclar üçün: Bölgə, Həkim adı, Yekun Borc."

İstifadəçiyə kömək et və praktik məsləhətlər ver. Kod və texniki detallardan danışma.
"""
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL if hasattr(settings, 'OPENAI_MODEL') else "gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            
            # Get AI response
            ai_message = response.choices[0].message.content.strip()
            
            # Update conversation history (keep last 10 messages to avoid token limit)
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": ai_message})
            if len(conversation_history) > 20:  # Keep last 10 exchanges (20 messages)
                conversation_history = conversation_history[-20:]
            request.session['chatbot_history'] = conversation_history
            request.session.modified = True
            
            logger.info(f"AI response generated successfully")
            
            return JsonResponse({
                'success': True,
                'message': ai_message,
            })
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'OpenAI API xətası: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Yanlış məlumat formatı'
        }, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in send_message: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Gözlənilməz xəta: {str(e)}'
        }, status=500)


@login_required
@subscription_required
@contract_required
@chatbot_required
@require_http_methods(["POST"])
def clear_history(request):
    """
    Clear chatbot conversation history from session
    """
    try:
        if 'chatbot_history' in request.session:
            del request.session['chatbot_history']
            request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Söhbət tarixçəsi təmizləndi'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Xəta: {str(e)}'
        }, status=500)
