from django import forms

class BulkKeywordForm(forms.Form):
    """Form untuk membuat multiple keywords sekaligus"""
    keywords_text = forms.CharField(
        label="Kata Kunci (satu per baris)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Masukkan kata kunci, satu per baris\nContoh:\njudol\ncasino online\npornografi\nhack site'
        }),
        help_text="Masukkan kata kunci yang akan dideteksi, satu kata kunci per baris. Baris kosong akan diabaikan."
    )
    category = forms.ChoiceField(
        label="Kategori",
        choices=[
            ('judi', 'Judi Online'),
            ('pornografi', 'Pornografi'),
            ('hacking', 'Hacking/Malware'),
            ('phishing', 'Phishing'),
            ('spam', 'Spam'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Kategori untuk semua kata kunci yang akan dibuat"
    )
    is_active = forms.BooleanField(
        label="Aktifkan semua kata kunci",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Centang untuk mengaktifkan semua kata kunci yang dibuat"
    )

    def clean_keywords_text(self):
        """Validasi dan bersihkan input keywords"""
        keywords_text = self.cleaned_data['keywords_text']
        keywords = []

        for line in keywords_text.split('\n'):
            line = line.strip()
            if line:  # Skip empty lines
                # Basic validation
                if len(line) < 2:
                    raise forms.ValidationError(f'Kata kunci "{line}" terlalu pendek (minimal 2 karakter)')
                if len(line) > 100:
                    raise forms.ValidationError(f'Kata kunci "{line}" terlalu panjang (maksimal 100 karakter)')
                keywords.append(line)

        if not keywords:
            raise forms.ValidationError('Minimal satu kata kunci harus dimasukkan')

        if len(keywords) > 50:
            raise forms.ValidationError('Maksimal 50 kata kunci per batch')

        # Check for duplicates within the batch
        if len(keywords) != len(set(keywords)):
            raise forms.ValidationError('Ada kata kunci duplikat dalam batch ini')

        return keywords
