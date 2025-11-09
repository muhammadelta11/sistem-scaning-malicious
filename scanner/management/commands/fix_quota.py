"""
Management command untuk memperbaiki quota user yang masih unlimited (quota_limit=0).
Command ini akan mengubah quota_limit=0 menjadi 10 untuk user client (non-admin/staff).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from scanner.models import UserScanQuota

User = get_user_model()


class Command(BaseCommand):
    help = 'Fix quota untuk user client yang masih unlimited (quota_limit=0), set ke default 10'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually changing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all user quotas with quota_limit=0
        quotas = UserScanQuota.objects.filter(quota_limit=0)
        
        fixed_count = 0
        skipped_count = 0
        
        self.stdout.write(self.style.WARNING('Checking quotas...'))
        
        for quota in quotas:
            user = quota.user
            
            # Skip admin/staff (they should remain unlimited)
            if user.is_superuser or user.is_staff:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'  Skipping {user.username} (admin/staff - should be unlimited)')
                )
                continue
            
            # Fix client users
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f'  Would fix: {user.username} (quota_limit: 0 → 10)')
                )
            else:
                quota.quota_limit = 10
                quota._calculate_next_reset()
                quota.save(update_fields=['quota_limit', 'next_reset', 'updated_at'])
                self.stdout.write(
                    self.style.SUCCESS(f'  Fixed: {user.username} (quota_limit: 0 → 10)')
                )
                fixed_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\nDry run complete. Would fix {fixed_count} users, skipped {skipped_count} admin/staff.')
            )
            self.stdout.write(self.style.WARNING('Run without --dry-run to apply changes.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nFixed {fixed_count} user quotas, skipped {skipped_count} admin/staff.')
            )

