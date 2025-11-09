@echo off
echo ========================================
echo Starting Django Server for Parallels
echo Listening on all interfaces (0.0.0.0:8000)
echo ========================================
echo.
echo To connect from macOS, use:
echo http://[WINDOWS_VM_IP]:8000
echo.
echo Find Windows VM IP with: ipconfig
echo.
python manage.py runserver 0.0.0.0:8000
pause

