from django.shortcuts import render


def region_list(request):
    """Render the regions page."""
    return render(request, 'regions.html')
