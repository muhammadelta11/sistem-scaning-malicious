import os
import sys
from importlib.machinery import SourceFileLoader
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the native FastAPI server from the 'sistem-nativ' folder without renaming it."

    def add_arguments(self, parser):
        parser.add_argument('--host', default='0.0.0.0')
        parser.add_argument('--port', type=int, default=8000)
        parser.add_argument('--reload', action='store_true', default=False)

    def handle(self, *args, **options):
        native_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../sistem-nativ'))
        api_path = os.path.join(native_dir, 'api.py')
        if not os.path.exists(api_path):
            self.stderr.write(self.style.ERROR(f"Native API not found at: {api_path}"))
            return

        # Ensure native dir is importable for its relative imports
        if native_dir not in sys.path:
            sys.path.insert(0, native_dir)

        loader = SourceFileLoader('native_api', api_path)
        native_api = loader.load_module()
        app = getattr(native_api, 'app', None)
        if app is None:
            self.stderr.write(self.style.ERROR("Could not load FastAPI app from native api.py"))
            return

        import uvicorn
        host = options['host']
        port = options['port']
        reload = options['reload']
        self.stdout.write(self.style.SUCCESS(f"Starting native FastAPI on http://{host}:{port}"))
        uvicorn.run(app, host=host, port=port, reload=reload)


