# SSL Setup Guide

## Why SSL?
SSL (HTTPS) encrypts traffic between the user and server. Without it, passwords and data travel in plain text.

## Option 1: With a Real Domain (Let's Encrypt — Free)

```bash
# 1. Install Certbot on your server
sudo apt install certbot python3-certbot-nginx -y

# 2. Get certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# 3. Certbot auto-renews — add this to crontab for auto-renewal
0 12 * * * /usr/bin/certbot renew --quiet
```

Then in `nginx/nginx.conf`, uncomment the HTTPS server block.

## Option 2: No Domain (Self-Signed — for testing only)

```bash
# Generate self-signed certificate
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=localhost"
```

Self-signed certs trigger browser warnings — not for production, only for demos.

## Option 3: Cloudflare (Recommended for beginners)
1. Point your domain to Cloudflare
2. Enable "Full SSL" mode in Cloudflare dashboard
3. Cloudflare handles HTTPS between user ↔ Cloudflare
4. HTTP between Cloudflare ↔ your server (internal only, acceptable)

## Current Setup
Since no domain is available, HTTP (port 80) is active. The HTTPS block in `nginx.conf` is documented and ready to enable — just uncomment and add cert paths.
