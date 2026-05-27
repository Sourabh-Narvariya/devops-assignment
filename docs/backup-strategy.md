# Backup & Restart Strategy

## Automatic Restart Strategy

All containers have `restart: unless-stopped` in docker-compose.yml.

This means:
- Container crashes → Docker automatically restarts it
- Server reboots → All containers start automatically
- Manual `docker stop` → Does NOT restart (intentional)

## Database Backup Strategy

### Manual Backup
```bash
# Backup PostgreSQL database
docker exec devops_postgres pg_dump -U appuser appdb > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup_20240101.sql | docker exec -i devops_postgres psql -U appuser appdb
```

### Automated Daily Backup (Cron Job)
```bash
# Add this to crontab on your server (runs every day at 2 AM)
# crontab -e
0 2 * * * docker exec devops_postgres pg_dump -U appuser appdb > /backups/db_$(date +\%Y\%m\%d).sql

# Keep only last 7 days of backups
0 3 * * * find /backups -name "*.sql" -mtime +7 -delete
```

## Zero-Downtime Deployment Strategy

When deploying updates, we use Docker's rolling update approach:

```bash
# Pull latest code
git pull origin main

# Build new images (old containers still running)
docker compose build

# Start new containers alongside old ones, then switch
docker compose up -d --build

# Docker handles the cutover — health checks confirm new containers are healthy
# before old ones stop
```

## Security Measures

| Measure | Implementation |
|---------|---------------|
| No root containers | FastAPI runs as non-root user |
| Secrets via env vars | Never hardcoded in source code |
| NGINX rate limiting | 10 req/s per IP |
| Network isolation | App/DB on private Docker network |
| Read-only NGINX config | `nginx.conf` mounted as `:ro` |
| fail2ban (recommended) | Ban IPs after 5 failed login attempts |
| UFW Firewall | Only ports 22, 80, 443 open |

## Firewall Setup (on real server)
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```
