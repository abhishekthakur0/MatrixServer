# Matrix Server Setup

A comprehensive guide for setting up a Matrix server using Synapse and PostgreSQL.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Security](#security)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project provides a complete solution for setting up a Matrix server. It includes:

- Matrix Synapse server setup
- PostgreSQL database configuration
- Nginx reverse proxy setup
- SSL/TLS configuration
- Security best practices
- Maintenance guidelines

## Features

- 🚀 High-performance Matrix server
- 🗄️ PostgreSQL database backend
- 🔒 SSL/TLS encryption
- 🔄 Reverse proxy with Nginx
- 📊 Monitoring and logging
- 🛡️ Enhanced security measures
- 🔄 Automatic updates

## Prerequisites

### Server Requirements
- Linux server (Ubuntu 20.04/22.04 recommended)
- Minimum 2GB RAM
- 10GB+ disk space
- Root or sudo access
- Docker and Docker Compose
- Domain name (for production use)

## Installation

### Server Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd matrix-server
```

2. Install Docker and Docker Compose:
```bash
# Update package lists
sudo apt update

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. Start the services:
```bash
docker-compose up -d
```

## Configuration

### Server Configuration

1. Update `docker-compose.yml`:
```yaml
services:
  matrix:
    image: matrixdotorg/synapse:latest
    container_name: matrix
    restart: unless-stopped
    ports:
      - "8008:8008"  # Client-server API
      - "8448:8448"  # Federation API
    volumes:
      - ./config:/config
      - ./data:/data
    environment:
      - SYNAPSE_SERVER_NAME=your-domain.com
      - SYNAPSE_REPORT_STATS=no
      - SYNAPSE_CONFIG_DIR=/config
      - SYNAPSE_CONFIG_PATH=/config/homeserver.yaml
    depends_on:
      - postgres

  postgres:
    image: postgres:13-alpine
    container_name: matrix-postgres
    restart: unless-stopped
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=your_secure_password
      - POSTGRES_USER=matrix
      - POSTGRES_DB=matrix
      - POSTGRES_INITDB_ARGS=--lc-collate=C --lc-ctype=C --encoding=UTF8
```

2. Configure `homeserver.yaml`:
```yaml
server_name: "your-domain.com"
public_baseurl: "https://your-domain.com:8448"
listeners:
  - port: 8008
    tls: false
    type: http
    x_forwarded: true
    resources:
      - names: [client, federation]
        compress: false

database:
  name: psycopg2
  args:
    user: matrix
    password: your_secure_password
    database: matrix
    host: postgres
    cp_min: 5
    cp_max: 10

enable_registration: true  # Set to false in production
```

3. Set up Nginx reverse proxy:
```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;

    location /_matrix {
        proxy_pass http://localhost:8008;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }

    location /.well-known/matrix/server {
        return 200 '{"m.server": "your-domain.com:8448"}';
        add_header Content-Type application/json;
    }
}
```

## Security

### Server Security

1. **Firewall Configuration**:
```bash
# Install UFW
sudo apt install ufw

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8448/tcp
sudo ufw enable
```

2. **SSL/TLS Configuration**:
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com
```

3. **Security Headers**:
```nginx
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options SAMEORIGIN;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

## Maintenance

### Regular Tasks

1. **Server Maintenance**:
```bash
# Update Docker images
docker-compose pull
docker-compose up -d

# Backup database
docker-compose exec postgres pg_dump -U matrix matrix > backup.sql

# Check logs
docker-compose logs -f
```

2. **Monitoring**:
- Resource usage
- Authentication attempts
- Error rates
- Performance metrics

### Backup Strategy

1. **Database Backups**:
```bash
# Daily backup
docker-compose exec postgres pg_dump -U matrix matrix > /backup/matrix_$(date +%Y%m%d).sql

# Weekly backup
tar -czf /backup/matrix_data_$(date +%Y%m%d).tar.gz /data
```

2. **Configuration Backups**:
```bash
# Backup configuration
tar -czf /backup/config_$(date +%Y%m%d).tar.gz /config
```

## Troubleshooting

### Common Issues

1. **Server Issues**:
- Database connection problems
- Authentication failures
- Performance issues
- Configuration errors

2. **Network Issues**:
- Port conflicts
- Firewall blocks
- SSL/TLS problems
- DNS configuration

### Solutions

1. **Server Solutions**:
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs matrix
docker-compose logs postgres

# Restart services
docker-compose restart
```

2. **Database Solutions**:
```bash
# Check database connection
docker-compose exec postgres psql -U matrix -d matrix -c "\l"

# Repair database
docker-compose exec postgres psql -U matrix -d matrix -c "VACUUM FULL;"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue
4. Contact the maintainers

## Acknowledgments

- Matrix.org for the Synapse server
- PostgreSQL team for the database
- Nginx team for the web server
- Open source community for contributions 