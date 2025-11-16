# Nginx Configuration for MLflow

## Setup Basic Authentication

Create the `.htpasswd` file with your desired credentials:

```bash
# Install htpasswd utility
sudo apt install apache2-utils  # Debian/Ubuntu
# OR
brew install httpd  # macOS

# Create password file
cd deployment/nginx
htpasswd -c .htpasswd mlflow_admin

# Enter password when prompted (recommended: use strong password)
# For additional users:
htpasswd .htpasswd another_user
```

## Setup SSL/TLS (Optional but Recommended)

### Option 1: Self-Signed Certificate (Development)

```bash
mkdir -p deployment/nginx/ssl
cd deployment/nginx/ssl

# Generate self-signed certificate (valid for 365 days)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem \
  -out cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=mlflow.forgetrace.local"
```

### Option 2: Let's Encrypt (Production)

```bash
# Install certbot
sudo apt install certbot

# Generate certificate (requires domain DNS pointing to your server)
sudo certbot certonly --standalone -d mlflow.yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/mlflow.yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/mlflow.yourdomain.com/privkey.pem

# Symlink to nginx directory
ln -s /etc/letsencrypt/live/mlflow.yourdomain.com/fullchain.pem deployment/nginx/ssl/cert.pem
ln -s /etc/letsencrypt/live/mlflow.yourdomain.com/privkey.pem deployment/nginx/ssl/key.pem
```

## Enable HTTPS

Uncomment the HTTPS server block in `nginx.conf` after SSL setup.

## Testing

```bash
# Start with authentication
docker-compose --profile with-auth up -d

# Test authentication
curl -u mlflow_admin:your_password http://localhost/api/2.0/mlflow/experiments/list

# Access UI in browser
open http://localhost
# Enter credentials: mlflow_admin / your_password
```
