from django.utils.deprecation import MiddlewareMixin
from .models import UserProfile, Company, ContractAgreement


class CompanyContextMiddleware(MiddlewareMixin):
    """
    Sets company / profile / contract context for authenticated users.
    Single-database deployment: no tenant DB switching.
    """

    def process_request(self, request):
        if request.path.startswith('/master-admin/'):
            request.company = None
            request.user_profile = None
            request.user_role = None
            request.contract_agreed = True
            return None

        if request.user.is_authenticated:
            if request.user.is_superuser and request.session.get('impersonating_company_id'):
                try:
                    impersonated_company = Company.objects.get(
                        id=request.session['impersonating_company_id']
                    )
                    request.company = impersonated_company
                    request.user_profile = None
                    request.user_role = 'master_admin'
                    request.contract_agreed = True
                    return None
                except Company.DoesNotExist:
                    request.session.pop('impersonating_company_id', None)
                    request.session.pop('impersonating_company_name', None)
                    request.session.pop('master_admin_mode', None)

            try:
                profile = UserProfile.objects.select_related('company').get(user=request.user)
                request.company = profile.company
                request.user_profile = profile
                request.user_role = profile.role

                if (
                    not request.path.startswith('/subscription/contract')
                    and not request.path.startswith('/subscription/plans')
                    and not request.path.startswith('/subscription/register')
                    and not request.path.startswith('/admin/')
                    and not request.path.startswith('/master-admin/')
                ):
                    try:
                        contract = ContractAgreement.objects.get(
                            company=profile.company,
                            user=request.user,
                        )
                        request.contract_agreed = contract.agreed
                    except ContractAgreement.DoesNotExist:
                        request.contract_agreed = False
                else:
                    request.contract_agreed = True

            except UserProfile.DoesNotExist:
                if request.user.is_superuser or request.user.is_staff:
                    first_company = Company.objects.first()
                    if first_company:
                        request.company = first_company
                        request.user_profile = None
                        request.user_role = 'admin'
                        request.contract_agreed = True
                    else:
                        request.company = None
                        request.user_profile = None
                        request.user_role = None
                        request.contract_agreed = True
                else:
                    request.company = None
                    request.user_profile = None
                    request.user_role = None
                    request.contract_agreed = True
        else:
            request.company = None
            request.user_profile = None
            request.user_role = None
            request.contract_agreed = True

        return None
