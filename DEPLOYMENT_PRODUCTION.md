# 🚀 Deployment Guide - Production Setup

## Overview

Panduan lengkap untuk deploy sistem deteksi malicious domain ke production environment dengan konfigurasi optimal.

## 📋 Prerequisites

### Software Requirements
- **Python**: 3.9 atau lebih tinggi
- **MySQL**: 8.0+ atau MariaDB 10.5+
- **Redis**: 7.0+ (untuk cache dan Celery)
- **Nginx**: 1.20+ (reverse proxy)
- **Systemd** (untuk service management)
- **Chrome/Chromium** (untuk Selenium headless)

### Server Requirements
- **CPU**: 2 core minimum, 4+ recommended
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 20GB+ (untuk database, cache, logs)
- **OS**: Ubuntu 20.04 LTS atau Debian 11+

## 🔧 Installation Steps

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
sudo apt install python3-pip python3-venv python3-dev -y

# Install MySQL
sudo apt install mysql-server -y
sudo mysql_secure_installation

# Install Redis
sudo apt install redis-server -y

# Install Nginx
sudo apt install nginx -y

# Install Chrome for Selenium
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y
```

### 2. Database Setup

```bash
# Login ke MySQL
sudo mysql -u root -p

# Create database dan user
CREATE DATABASE sistem_deteksi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sistem_deteksi_user'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON sistem_deteksi.* TO 'sistem_deteksi_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Application Setup

```bash
# Clone repository (atau copy files)
cd /var/www/
sudo git clone <repository-url> sistem_deteksi_malicious
cd sistem_deteksi_malicious

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
sudo nano .env
```

**isi .env:**
```env
# Django Settings
SECRET_KEY=your-very-long-secret-key-here-change-in-production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,IP_ADDRESS

# Database
DB_NAME=sistem_deteksi
DB_USER=sistem_deteksi_user
DB_PASSWORD=StrongPassword123!
DB_HOST=127.0.0.1
DB_PORT=3306

# Redis
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0

# SerpAPI
SERPAPI_API_KEY=your-serpapi-key-here

# Security
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True

# Static Files
STATIC_ROOT=/var/www/sistem_deteksi_malicious/staticfiles
MEDIA_ROOT=/var/www/sistem_deteksi_malicious/media

# Production Settings
USE_NATIVE_FLOW=True
```

### 4. Django Configuration

```bash
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Load initial keywords (opsional)
python manage.py shell
>>> from scanner.models import MaliciousKeyword
>>> # Import keywords data if needed
```

### 5. Redis Configuration

```bash
# Edit redis config
sudo nano /etc/redis/redis.conf

# Set:
# bind 127.0.0.1 (default OK)
# requirepass StrongRedisPassword (set password)

# Restart Redis
sudo systemctl restart redis
sudo systemctl enable redis
```

### 6. Celery Setup

```bash
# Create celery service
sudo nano /etc/systemd/system/celery.service
```

**isi celery.service:**
```ini
[Unit]
Description=Celery service for Sistem Deteksi Malicious
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
EnvironmentFile=/var/www/sistem_deteksi_malicious/.env
WorkingDirectory=/var/www/sistem_deteksi_malicious
ExecStart=/var/www/sistem_deteksi_malicious/venv/bin/celery -A sistem_deteksi_malicious multi start worker1 \
    --pidfile=/var/run/celery/%n.pid \
    --logfile=/var/log/celery/%n%I.log \
    --loglevel=INFO \
    --concurrency=4
ExecStop=/var/www/sistem_deteksi_malicious/venv/bin/celery -A sistem_deteksi_malicious multi stopwait worker1 \
    --pidfile=/var/run/celery/%n.pid
ExecReload=/var/www/sistem_deteksi_malicious/venv/bin/celery -A sistem_deteksi_malicious multi restart worker1 \
    --pidfile=/var/run/celery/%n.pid \
    --logfile=/var/log/celery/%n%I.log \
    --loglevel=INFO
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Create celerybeat service
sudo nano /etc/systemd/system/celerybeat.service
```

**isi celerybeat.service:**
```ini
[Unit]
Description=Celery Beat for Sistem Deteksi Malicious
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
EnvironmentFile=/var/www/sistem_deteksi_malicious/.env
WorkingDirectory=/var/www/sistem_deteksi_malicious
ExecStart=/var/www/sistem_deteksi_malicious/venv/bin/celery -A sistem_deteksi_malicious beat \
    --pidfile=/var/run/celery/celerybeat.pid \
    --logfile=/var/log/celery/celerybeat.log \
    --loglevel=INFO
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Create directories
sudo mkdir -p /var/run/celery /var/log/celery
sudo chown -R www-data:www-data /var/run/celery /var/log/celery

# Enable and start Celery
sudo systemctl daemon-reload
sudo systemctl enable celery
sudo systemctl enable celerybeat
sudo systemctl start celery
sudo systemctl start celerybeat
```

### 7. Gunicorn Setup

```bash
# Install gunicorn
pip install gunicorn

# Create gunicorn service
sudo nano /etc/systemd/system/gunicorn.service
```

**isi gunicorn.service:**
```ini
[Unit]
Description=Gunicorn daemon for Sistem Deteksi Malicious
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sistem_deteksi_malicious
EnvironmentFile=/var/www/sistem_deteksi_malicious/.env
ExecStart=/var/www/sistem_deteksi_malicious/venv/bin/gunicorn \
    --access-logfile - \
    --workers 4 \
    --bind unix:/var/www/sistem_deteksi_malicious/sistem_deteksi.sock \
    sistem_deteksi_malicious.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Set permissions
sudo chown -R www-data:www-data /var/www/sistem_deteksi_malicious

# Enable and start Gunicorn
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```

### 8. Nginx Configuration

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/sistem_deteksi_malicious
```

**isi config:**
```nginx
upstream sistem_deteksi_app {
    server unix:/var/www/sistem_deteksi_malicious/sistem_deteksi.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/sistem_deteksi_access.log;
    error_log /var/log/nginx/sistem_deteksi_error.log;

    # Client max body size
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /var/www/sistem_deteksi_malicious/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/sistem_deteksi_malicious/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://sistem_deteksi_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Selenium WebDriver endpoint (if using remote)
    location /wd/ {
        proxy_pass http://localhost:9515/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/sistem_deteksi_malicious /etc/nginx/sites-enabled/

# Test nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 9. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (automatic)
sudo certbot renew --dry-run
```

### 10. System Configuration via UI

Setelah deployment, akses admin panel dan configure:

```bash
# Login ke admin
https://your-domain.com/admin/

# Atau via web UI
https://your-domain.com/config/
```

**Recommended Production Settings:**

1. **Go to**: `/config/` page
2. **Click**: "Hemat Maksimal" preset
3. **Verify**:
   - ✅ Enable API Cache = ON
   - ✅ API Cache TTL = 14 hari
   - ✅ Use Comprehensive Query = ON
   - ✅ Max Search Results = 100
   - ❌ Bing Search = OFF
   - ✅ DuckDuckGo = ON
   - ✅ Subdomain DNS Lookup = ON
   - ❌ Subdomain Search = OFF
   - ❌ Subdomain Content Scan = OFF
   - ✅ Deep Crawling = ON
   - ✅ Sitemap Analysis = ON
   - ✅ Path Discovery = ON
   - ❌ Graph Analysis = OFF
   - Max Crawl Pages = 30

4. **Click**: "Simpan Semua Konfigurasi"

### 11. Monitoring Setup

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Setup log rotation
sudo nano /etc/logrotate.d/sistem_deteksi
```

**isi logrotate:**
```
/var/log/sistem_deteksi/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        /bin/systemctl reload gunicorn > /dev/null 2>&1 || true
    endscript
}

/var/log/celery/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        /bin/systemctl restart celery > /dev/null 2>&1 || true
    endscript
}
```

## 🔒 Security Checklist

- [x] Use strong SECRET_KEY
- [x] DEBUG = False
- [x] Set ALLOWED_HOSTS properly
- [x] Enable HTTPS with valid SSL cert
- [x] Use secure cookies (CSRF_COOKIE_SECURE, SESSION_COOKIE_SECURE)
- [x] Enable HSTS header
- [x] Set proper database passwords
- [x] Enable Redis password protection
- [x] Configure firewall (UFW)
- [x] Disable root SSH login
- [x] Enable fail2ban
- [x] Regular system updates
- [x] Backup strategy in place

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check services status
sudo systemctl status gunicorn
sudo systemctl status celery
sudo systemctl status celerybeat
sudo systemctl status nginx
sudo systemctl status redis
sudo systemctl status mysql

# Check logs
sudo journalctl -u gunicorn -f
sudo journalctl -u celery -f
sudo tail -f /var/log/nginx/sistem_deteksi_error.log
```

### Backup Strategy

```bash
# Create backup script
sudo nano /usr/local/bin/backup_sistem_deteksi.sh
```

**isi backup script:**
```bash
#!/bin/bash
BACKUP_DIR="/backup/sistem_deteksi"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="sistem_deteksi"
DB_USER="sistem_deteksi_user"
DB_PASS="StrongPassword123!"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media and code
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/sistem_deteksi_malicious/media

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup_sistem_deteksi.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup_sistem_deteksi.sh
```

### Performance Tuning

```python
# settings/production.py
# Adjust these for your server:

# Database connection pooling
DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
            'read_timeout': 10,
            'write_timeout': 10,
        }
    }
}

# Cache optimization
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True
            }
        },
        'KEY_PREFIX': 'sistem_deteksi',
        'TIMEOUT': 300,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## 🚨 Troubleshooting

### Issue: Gunicorn won't start
```bash
# Check socket permissions
sudo chown www-data:www-data /var/www/sistem_deteksi_malicious/sistem_deteksi.sock

# Check logs
sudo journalctl -u gunicorn -n 50
```

### Issue: Database connection refused
```bash
# Check MySQL status
sudo systemctl status mysql

# Check connection
mysql -u sistem_deteksi_user -p -h 127.0.0.1

# Check bind-address in /etc/mysql/mysql.conf.d/mysqld.cnf
# Should be: bind-address = 127.0.0.1
```

### Issue: Redis connection error
```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping
# Should return: PONG

# Check password
redis-cli -a StrongRedisPassword ping
```

### Issue: High memory usage
```bash
# Check memory
free -h
ps aux --sort=-%mem | head

# Reduce workers
# Edit /etc/systemd/system/gunicorn.service
# Change --workers 4 to --workers 2

# Restart
sudo systemctl restart gunicorn
```

## 📈 Scaling Considerations

### Horizontal Scaling
1. Add more Gunicorn workers
2. Use Nginx load balancer
3. Deploy multiple application servers
4. Use shared Redis instance
5. Use shared MySQL instance or replication

### Vertical Scaling
1. Increase CPU cores
2. Add more RAM
3. Use SSD storage
4. Optimize database queries
5. Enable query caching

## 📞 Support

Untuk bantuan lebih lanjut:
- Check logs: `/var/log/`
- System logs: `sudo journalctl -u service-name`
- Django logs: Settings `LOGGING`
- Nginx logs: `/var/log/nginx/`

---

**Deployment Checklist:**
- [ ] All services installed and configured
- [ ] Database migrated and seeded
- [ ] Static files collected
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Security hardening completed
- [ ] Performance optimization done
- [ ] Documentation updated

**Production Ready! 🎉**

