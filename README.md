# DevOps Assignment — Production FastAPI Stack

A production-ready deployment of a FastAPI application with PostgreSQL, Redis, and NGINX reverse proxy, containerised with Docker and automated via GitHub Actions CI/CD.

## Architecture

```
Internet
    │
    ▼
┌─────────────────────────────┐
│   NGINX (Port 80/443)       │  ← Public entry point, rate limiting, SSL
│   Reverse Proxy             │
└─────────────┬───────────────┘
              │ proxy_pass
              ▼
┌─────────────────────────────┐
│   FastAPI App (Port 8000)   │  ← Python API, NOT exposed publicly
│   2 uvicorn workers         │
└──────┬──────────────┬───────┘
       │              │
       ▼              ▼
┌──────────┐   ┌──────────────┐
│PostgreSQL│   │    Redis     │  ← Both on private Docker network only
│(Port5432)│   │  (Port 6379) │
└──────────┘   └──────────────┘
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API | FastAPI (Python) | REST API with auto-docs |
| Database | PostgreSQL 15 | Persistent data storage |
| Cache | Redis 7 | Fast caching & counters |
| Proxy | NGINX | Traffic routing, SSL, rate limiting |
| Containers | Docker + Compose | Isolated, reproducible services |
| CI/CD | GitHub Actions | Auto-build and deploy on push |

## Quick Start (Local / Play-with-Docker)

### Prerequisites
- Docker installed
- Docker Compose installed

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/devops-assignment.git
cd devops-assignment

# 2. Create environment file
cp .env.example .env
# Edit .env with your values (or keep defaults for local testing)

# 3. Start all services
docker compose up -d --build

# 4. Verify everything is running
docker compose ps

# 5. Test the API
curl http://localhost/health
curl http://localhost/
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root - API info |
| GET | `/health` | Health check (PostgreSQL + Redis status) |
| GET | `/docs` | Auto-generated Swagger UI |
| POST | `/messages` | Create a message |
| GET | `/messages` | Get all messages |

### Test the API

```bash
# Health check
curl http://localhost/health

# Create a message
curl -X POST http://localhost/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from DevOps!"}'

# Get all messages
curl http://localhost/messages
```

## CI/CD Pipeline

Every push to `main` branch triggers GitHub Actions:

```
Push to main
     │
     ▼
┌─────────────────────┐
│ 1. Checkout code    │
│ 2. Build images     │
│ 3. Start services   │
│ 4. Health check     │
│ 5. Tear down        │
└──────────┬──────────┘
           │ (if all pass)
           ▼
┌─────────────────────┐
│ Deploy to server    │
│ (SSH + docker pull) │
└─────────────────────┘
```

### GitHub Secrets Required
Go to: Repository → Settings → Secrets → Actions

| Secret | Value |
|--------|-------|
| `POSTGRES_USER` | Your DB username |
| `POSTGRES_PASSWORD` | Your DB password |
| `POSTGRES_DB` | Your DB name |
| `SERVER_IP` | Your server IP (when available) |
| `SSH_PRIVATE_KEY` | SSH private key for server access |

## Logging Strategy

- **Application logs**: FastAPI logs to stdout → captured by Docker
- **NGINX logs**: Access + error logs inside nginx container
- **View logs**: `docker compose logs -f app` or `docker compose logs -f nginx`
- **Log format**: `timestamp | LEVEL | message` for easy parsing

## Security Measures

- NGINX rate limiting (10 req/s per IP)
- Security headers (X-Frame-Options, XSS protection)
- Database not exposed publicly (private Docker network)
- Secrets via environment variables (never in source code)
- `restart: unless-stopped` for auto-recovery

## SSL Setup

See [docs/ssl-setup.md](docs/ssl-setup.md) for full SSL configuration guide using:
- Let's Encrypt (free, with domain)
- Self-signed (testing only)
- Cloudflare (recommended for beginners)

## Backup Strategy

See [docs/backup-strategy.md](docs/backup-strategy.md) for:
- Daily automated PostgreSQL backups
- 7-day retention policy
- Zero-downtime deployment approach

## Useful Commands

```bash
# Start all services
docker compose up -d --build

# Stop all services
docker compose down

# View logs
docker compose logs -f

# Restart one service
docker compose restart app

# Check container health
docker compose ps

# Manual DB backup
docker exec devops_postgres pg_dump -U appuser appdb > backup.sql
```

---

**Author**: Sourabh Narvariya
**Assignment**: Webvory DevOps Engineer Technical Task  
**Date**: May 2026
