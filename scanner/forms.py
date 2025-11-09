# scanner/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import MaliciousKeyword

User = get_user_model()

SCAN_TYPE_CHOICES = [
    ('Cepat (Google Only)', 'Cepat (Google Only)'),
    ('Komprehensif (Google + Crawling)', 'Komprehensif (Google + Crawling)'),
]

class ScanForm(forms.Form):
    domain = forms.CharField(
        label="Domain Target",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'contoh: uns.ac.id'}),
        help_text="Masukkan domain tanpa http://"
    )
    scan_type = forms.ChoiceField(
        label="Tipe Scan",
        choices=SCAN_TYPE_CHOICES,
        widget=forms.Select(),
        help_text="Scan komprehensif akan memakan waktu lebih lama."
    )
    enable_verification = forms.BooleanField(
        label="Aktifkan Verifikasi Real-Time",
        required=False, # Jadikan opsional (checkbox)
        initial=True, # Default dicentang
        help_text="Verifikasi langsung ke website target."
    )
    show_all_results = forms.BooleanField(
        label="Tampilkan Semua Hasil Terindikasi",
        required=False,
        initial=False,
        help_text="Tampilkan semua URL yang terindikasi malicious beserta kontennya, tanpa filtering berdasarkan verifikasi."
    )
    # Kita bisa tambahkan field lain seperti enable_backlink jika diperlukan

class KeywordForm(forms.ModelForm):
    class Meta:
        model = MaliciousKeyword
        fields = ['keyword', 'category', 'is_active']
        widgets = {
            'keyword': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan kata kunci',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'keyword': 'Kata Kunci',
            'category': 'Kategori',
            'is_active': 'Aktif'
        }
        help_texts = {
            'keyword': 'Kata kunci yang akan dideteksi dalam konten malicious',
            'category': 'Kategori jenis konten malicious',
            'is_active': 'Centang untuk mengaktifkan deteksi keyword ini'
        }

class CustomUserCreationForm(UserCreationForm):
    """Form untuk membuat user baru dengan field tambahan"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'organization_name', 'user_api_key', 'is_active', 'is_staff', 'is_superuser')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tambahkan help text dan styling
        self.fields['username'].help_text = "Username unik untuk login"
        self.fields['email'].help_text = "Email untuk notifikasi dan recovery"
        self.fields['organization_name'].help_text = "Nama instansi/organisasi"
        self.fields['user_api_key'].help_text = "API key SerpApi (opsional, untuk user premium)"
        self.fields['is_active'].help_text = "User aktif dapat login"
        self.fields['is_staff'].help_text = "Staff dapat akses admin features"
        self.fields['is_superuser'].help_text = "Superuser memiliki akses penuh"

        # Set required fields
        self.fields['email'].required = True
        self.fields['organization_name'].required = True

class CustomUserChangeForm(UserChangeForm):
    """Form untuk edit user"""
    password = None  # Remove password field from change form

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'organization_name', 'user_api_key', 'is_premium', 'is_active', 'is_staff', 'is_superuser')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tambahkan help text
        self.fields['username'].help_text = "Username unik untuk login"
        self.fields['email'].help_text = "Email untuk notifikasi dan recovery"
        self.fields['organization_name'].help_text = "Nama instansi/organisasi"
        self.fields['user_api_key'].help_text = "API key SerpApi (opsional, untuk user premium)"
        self.fields['is_premium'].help_text = "User premium: hasil scan disimpan permanen di database"
        self.fields['is_active'].help_text = "User aktif dapat login"
        self.fields['is_staff'].help_text = "Staff dapat akses admin features"
        self.fields['is_superuser'].help_text = "Superuser memiliki akses penuh"

class UserPasswordResetForm(forms.Form):
    """Form untuk reset password user"""
    new_password1 = forms.CharField(
        label="Password Baru",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Minimal 8 karakter"
    )
    new_password2 = forms.CharField(
        label="Konfirmasi Password Baru",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Ulangi password yang sama"
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password tidak cocok")

        if password1 and len(password1) < 8:
            raise forms.ValidationError("Password minimal 8 karakter")

        return cleaned_data
