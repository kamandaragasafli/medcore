"""
Management command to create default notification templates
"""
from django.core.management.base import BaseCommand
from subscription.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Create default notification templates'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Sistem işləməsi haqqında',
                'title': 'Sistemdə texniki işlər aparılır',
                'message': 'Hörmətli istifadəçi,\n\nSistemdə texniki işlər aparılır. Xidmətlərdə müvəqqəti dayanmalar ola bilər. Narahatlığa görə üzr istəyirik.\n\nƏtraflı məlumat üçün dəstək xidməti ilə əlaqə saxlayın.',
                'notification_type': 'warning',
                'is_important': True,
            },
            {
                'name': 'Abunəlik bitməsi xəbərdarlığı (3 gün)',
                'title': 'Abunəliyiniz 3 gün sonra bitir',
                'message': 'Hörmətli müştəri,\n\nAbunəliyiniz 3 gün sonra bitəcək. Xidmətlərimizdən kəsintisiz istifadə etmək üçün abunəliyinizi yeniləyin.\n\nAbunəliyi yeniləmək üçün aşağıdakı düyməyə klikləyin.',
                'notification_type': 'warning',
                'is_important': True,
                'action_url': '/subscription/plans/',
                'action_text': 'Abunəliyi yenilə',
            },
            {
                'name': 'Abunəlik bitməsi xəbərdarlığı (1 gün)',
                'title': 'Abunəliyiniz sabah bitir',
                'message': 'Hörmətli müştəri,\n\nAbunəliyiniz sabah bitəcək. Xidmətlərimizdən kəsintisiz istifadə etmək üçün abunəliyinizi təcili yeniləyin.\n\nAbunəliyi yeniləmək üçün aşağıdakı düyməyə klikləyin.',
                'notification_type': 'error',
                'is_important': True,
                'action_url': '/subscription/plans/',
                'action_text': 'Abunəliyi yenilə',
            },
            {
                'name': 'Yeni funksiyalar haqqında',
                'title': 'Yeni funksiyalar əlavə edildi',
                'message': 'Hörmətli istifadəçi,\n\nSistemə yeni funksiyalar əlavə edildi. Yenilikləri görmək üçün sistemə daxil olun və yeni imkanlardan istifadə edin.\n\nƏtraflı məlumat üçün kömək bölməsinə baxın.',
                'notification_type': 'success',
                'is_important': False,
            },
            {
                'name': 'Təhlükəsizlik yeniləməsi',
                'title': 'Təhlükəsizlik yeniləməsi',
                'message': 'Hörmətli istifadəçi,\n\nSistem təhlükəsizliyini artırmaq üçün yeniləmələr aparıldı. Şifrənizi dəyişdirməyinizi tövsiyə edirik.\n\nTəhlükəsizlik məsləhətləri üçün parametrlər bölməsinə baxın.',
                'notification_type': 'info',
                'is_important': True,
            },
            {
                'name': 'Xidmət bərpası',
                'title': 'Xidmət bərpa olundu',
                'message': 'Hörmətli istifadəçi,\n\nTexniki işlər tamamlandı və xidmətlər bərpa olundu. Sistemdən normal şəkildə istifadə edə bilərsiniz.\n\nNarahatlığa görə üzr istəyirik.',
                'notification_type': 'success',
                'is_important': False,
            },
            {
                'name': 'Plan limitinə çatma',
                'title': 'Plan limitinə çatdınız',
                'message': 'Hörmətli müştəri,\n\nCari planınızın limitinə çatdınız. Daha çox imkanlar üçün planınızı yüksəldin.\n\nPlan seçimlərinə baxmaq üçün aşağıdakı düyməyə klikləyin.',
                'notification_type': 'warning',
                'is_important': True,
                'action_url': '/subscription/plans/',
                'action_text': 'Planları görüntülə',
            },
        ]

        created_count = 0
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Şablon yaradıldı: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Şablon artıq mövcuddur: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n{created_count} yeni şablon yaradıldı.')
        )

