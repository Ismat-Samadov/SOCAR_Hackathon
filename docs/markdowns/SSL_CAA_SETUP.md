# SSL/TLS and CAA DNS Record Setup Guide

This guide explains how to configure SSL/TLS certificates and CAA (Certificate Authority Authorization) DNS records for the SOCAR AI System in production.

## What is CAA?

CAA (Certificate Authority Authorization) is a DNS record type that specifies which Certificate Authorities (CAs) are authorized to issue SSL/TLS certificates for your domain. This prevents unauthorized certificate issuance and helps protect against man-in-the-middle attacks.

## Prerequisites

1. A registered domain name
2. Access to your DNS provider's management console
3. Docker and Docker Compose installed
4. The SOCAR AI System codebase

## Step 1: Configure CAA DNS Records

Add the following CAA records to your domain's DNS configuration:

### For Let's Encrypt (Recommended - Free)

```dns
yourdomain.com.  CAA  0 issue "letsencrypt.org"
yourdomain.com.  CAA  0 issuewild "letsencrypt.org"
yourdomain.com.  CAA  0 iodef "mailto:security@yourdomain.com"
```

### For Other Certificate Authorities

| CA Provider | CAA Record Value |
|-------------|------------------|
| Let's Encrypt | `letsencrypt.org` |
| DigiCert | `digicert.com` |
| Comodo/Sectigo | `sectigo.com` |
| GlobalSign | `globalsign.com` |
| Amazon (ACM) | `amazon.com` |
| Cloudflare | `cloudflare.com` |
| ZeroSSL | `zerossl.com` |

### DNS Record Examples

**Using Cloudflare:**
1. Go to DNS settings
2. Add a CAA record:
   - Name: `@` (or your subdomain)
   - Tag: `issue`
   - CA domain name: `letsencrypt.org`

**Using AWS Route 53:**
```json
{
  "ResourceRecords": [
    { "Value": "0 issue \"letsencrypt.org\"" }
  ]
}
```

### Verify CAA Records

Use these commands to verify your CAA records are properly configured:

```bash
# Using dig
dig CAA yourdomain.com

# Using nslookup
nslookup -type=CAA yourdomain.com

# Using online tools
# https://caatest.co.uk/
# https://dnschecker.org/
```

## Step 2: Generate SSL Certificates

### Option A: Let's Encrypt with Certbot (Recommended)

1. **Create required directories:**

```bash
mkdir -p nginx/ssl
mkdir -p certbot/www
```

2. **Initial certificate generation:**

```bash
# Start nginx in HTTP-only mode first
docker run -d --name temp-nginx \
  -v $(pwd)/nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  -v $(pwd)/certbot/www:/var/www/certbot:ro \
  -p 80:80 \
  nginx:alpine

# Generate certificate
docker run -it --rm \
  -v $(pwd)/nginx/ssl:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email

# Stop temp nginx
docker stop temp-nginx && docker rm temp-nginx
```

3. **Copy certificates to correct location:**

```bash
cp nginx/ssl/live/yourdomain.com/fullchain.pem nginx/ssl/fullchain.pem
cp nginx/ssl/live/yourdomain.com/privkey.pem nginx/ssl/privkey.pem
```

### Option B: Self-Signed Certificates (Development/Testing Only)

```bash
mkdir -p nginx/ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=AZ/ST=Baku/L=Baku/O=SOCAR/CN=localhost"
```

### Option C: Using Existing Certificates

If you have certificates from another CA:

```bash
# Copy your certificate files to the ssl directory
cp /path/to/your/fullchain.pem nginx/ssl/fullchain.pem
cp /path/to/your/privkey.pem nginx/ssl/privkey.pem

# Set correct permissions
chmod 600 nginx/ssl/privkey.pem
chmod 644 nginx/ssl/fullchain.pem
```

## Step 3: Configure Environment Variables

Update your `.env` file with production settings:

```bash
# Production Settings
PRODUCTION=true
HTTPS_ONLY=true

# Domain Configuration
TRUSTED_HOSTS=yourdomain.com,www.yourdomain.com

# CORS Origins (your production domains)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Existing configuration...
AZURE_OPENAI_API_KEY=your_key_here
# ... rest of your config
```

## Step 4: Deploy with Production Docker Compose

```bash
# Start the production stack
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Verify health
curl -k https://yourdomain.com/health
```

## Step 5: Verify SSL Configuration

### Test SSL Certificate

```bash
# Test SSL connection
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check certificate details
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -text

# Test with curl
curl -I https://yourdomain.com/health
```

### Online SSL Testing Tools

- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/)
- [Qualys SSL Checker](https://www.ssllabs.com/ssltest/)
- [SSL Shopper Checker](https://www.sslshopper.com/ssl-checker.html)

## Step 6: Certificate Renewal

### Automatic Renewal (with Certbot container)

The `docker-compose.prod.yml` includes a certbot container that automatically renews certificates every 12 hours. No manual action required.

### Manual Renewal

```bash
docker-compose -f docker-compose.prod.yml exec certbot certbot renew

# Reload nginx to use new certificates
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## Troubleshooting

### CAA Record Issues

**Error: "CAA record prevents issuance"**
- Verify CAA records include your CA
- Wait for DNS propagation (up to 48 hours)
- Use `dig CAA yourdomain.com` to verify

**Error: "DNS resolution failed"**
- Check your domain's DNS configuration
- Verify nameservers are responding
- Check for DNSSEC issues

### SSL Certificate Issues

**Error: "Certificate not yet valid"**
- Check server time synchronization
- Run `ntpdate pool.ntp.org`

**Error: "Certificate has expired"**
- Renew certificate: `certbot renew`
- Check certbot logs for renewal failures

**Error: "Certificate chain incomplete"**
- Ensure fullchain.pem includes intermediate certificates
- Verify certificate order in the chain

### Nginx Issues

**Error: "nginx: [emerg] cannot load certificate"**
- Check file permissions (644 for cert, 600 for key)
- Verify file paths in nginx.conf
- Check file exists: `ls -la nginx/ssl/`

**Error: "502 Bad Gateway"**
- Check if backend container is running
- Verify network connectivity between containers
- Check backend health: `docker logs socar-ai-system`

## Security Best Practices

1. **Keep CAA records updated** - If you change CAs, update CAA records
2. **Monitor certificate expiry** - Set up alerts for expiring certificates
3. **Use HSTS preloading** - Submit domain to [HSTS Preload List](https://hstspreload.org/)
4. **Disable old protocols** - Only allow TLS 1.2 and 1.3
5. **Regular security audits** - Run SSL Labs tests periodically
6. **Backup certificates** - Store copies of certificates securely

## File Structure

After setup, your directory should look like:

```
SOCAR_Hackathon/
├── nginx/
│   ├── nginx.conf
│   └── ssl/
│       ├── fullchain.pem
│       └── privkey.pem
├── certbot/
│   └── www/
│       └── .well-known/
│           └── acme-challenge/
├── docker-compose.prod.yml
├── .env
└── ...
```

## Quick Reference

| Action | Command |
|--------|---------|
| Start production stack | `docker-compose -f docker-compose.prod.yml up -d` |
| Stop production stack | `docker-compose -f docker-compose.prod.yml down` |
| View logs | `docker-compose -f docker-compose.prod.yml logs -f` |
| Renew certificates | `docker-compose -f docker-compose.prod.yml exec certbot certbot renew` |
| Reload nginx | `docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload` |
| Check SSL | `openssl s_client -connect yourdomain.com:443` |
| Check CAA | `dig CAA yourdomain.com` |
