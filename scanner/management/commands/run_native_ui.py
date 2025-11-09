import os
import sys
import subprocess
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the native Streamlit UI from the 'sistem-nativ' folder without renaming it."

    def add_arguments(self, parser):
        parser.add_argument('--port', type=int, default=8501)

    def handle(self, *args, **options):
        native_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../sistem-nativ'))
        app_path = os.path.join(native_dir, 'app.py')
        if not os.path.exists(app_path):
            self.stderr.write(self.style.ERROR(f"Native UI not found at: {app_path}"))
            return

        env = os.environ.copy()
        # Ensure native dir can import its modules
        env['PYTHONPATH'] = native_dir + os.pathsep + env.get('PYTHONPATH', '')

        port = str(options['port'])
        cmd = [sys.executable, '-m', 'streamlit', 'run', app_path, '--server.port', port]
        self.stdout.write(self.style.SUCCESS(f"Starting native Streamlit UI on http://localhost:{port}"))
        subprocess.run(cmd, cwd=native_dir, env=env, check=False)


