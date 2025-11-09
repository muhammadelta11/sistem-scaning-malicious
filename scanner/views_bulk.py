from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import core_scanner
from .models import ActivityLog, MaliciousKeyword
from .forms_bulk import BulkKeywordForm

@login_required
def bulk_keyword_create_view(request):
    """
    View untuk membuat multiple keywords sekaligus
    """
    if not request.user.is_admin:
        messages.error(request, 'Anda tidak memiliki izin untuk mengakses halaman ini.')
        return redirect('scanner:scanner_page')

    if request.method == 'POST':
        form = BulkKeywordForm(request.POST)
        if form.is_valid():
            keywords_text = form.cleaned_data['keywords_text']
            category = form.cleaned_data['category']
            is_active = form.cleaned_data['is_active']

            # Get the cleaned keywords list
            keywords_list = form.cleaned_data['keywords_text']

            # Create keywords
            created_count = 0
            skipped_count = 0
            skipped_keywords = []

            for keyword_text in keywords_list:
                # Check if keyword already exists
                if MaliciousKeyword.objects.filter(keyword__iexact=keyword_text).exists():
                    skipped_count += 1
                    skipped_keywords.append(keyword_text)
                    continue

                # Create new keyword
                MaliciousKeyword.objects.create(
                    keyword=keyword_text,
                    category=category,
                    is_active=is_active,
                    created_by=request.user
                )
                created_count += 1

            # Clear cache untuk memaksa reload keywords
            core_scanner.get_active_malicious_keywords.cache_clear()

            # Log aktivitas
            ActivityLog.objects.create(
                user=request.user,
                action='BULK_CREATE_KEYWORDS',
                details=f'Created {created_count} keywords in category {category}, skipped {skipped_count} duplicates'
            )

            # Success message
            if created_count > 0:
                messages.success(request, f'Berhasil menambahkan {created_count} kata kunci baru.')
            if skipped_count > 0:
                messages.warning(request, f'{skipped_count} kata kunci dilewati karena sudah ada: {", ".join(skipped_keywords[:5])}{"..." if len(skipped_keywords) > 5 else ""}')

            return redirect('scanner:keywords')
    else:
        form = BulkKeywordForm()

    context = {
        'form': form,
        'title': 'Tambah Kata Kunci Massal'
    }
    return render(request, 'scanner/bulk_keyword_form.html', context)
