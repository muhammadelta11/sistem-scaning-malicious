# Generated manually for MaliciousKeyword model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scanner', '0002_alter_activitylog_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaliciousKeyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(help_text='Kata kunci untuk deteksi malicious content', max_length=100, unique=True)),
                ('category', models.CharField(choices=[('gambling', 'Judi Online'), ('pornography', 'Pornografi'), ('hacking', 'Hacking/Malware'), ('phishing', 'Phishing/Scam'), ('other', 'Lainnya')], default='other', help_text='Kategori keyword', max_length=20)),
                ('is_active', models.BooleanField(default=True, help_text='Apakah keyword aktif digunakan')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, help_text='User yang membuat keyword', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_keywords', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Malicious Keyword',
                'verbose_name_plural': 'Malicious Keywords',
                'ordering': ['-created_at'],
            },
        ),
    ]
