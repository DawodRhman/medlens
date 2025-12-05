# MedLens Deployment & DevOps Guide

Complete guide for deploying MedLens to production using Docker, Kubernetes, AWS, and CI/CD pipelines.

## Table of Contents

- [Local Development](#local-development)
- [Docker & Docker Compose](#docker--docker-compose)
- [Kubernetes Deployment](#kubernetes-deployment)
- [AWS Deployment](#aws-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Disaster Recovery](#backup--disaster-recovery)
- [Performance Tuning](#performance-tuning)

---

## Local Development

### Quick Start

```powershell
cd C:\Users\USER\Desktop\medlens
docker-compose up --build
```

### Manual Setup

**Backend:**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install alembic
alembic upgrade head
python app/db/seed_admin.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```powershell
cd frontend
npm install
npm run dev
```

---

## Docker & Docker Compose

### Building Docker Images

**Backend:**
```powershell
cd backend
docker build -t medlens-backend:latest .
```

**Frontend:**
```powershell
cd frontend
docker build -t medlens-frontend:latest .
```

### Docker Compose (Local Development)

File: `docker-compose.yml`

```powershell
# Start all services
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Scale backend
docker-compose up --scale backend=3
```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'
services:
  backend:
    image: medlens-backend:prod
    restart: always
    environment:
      - DATABASE_URL=postgresql://medlens:${DB_PASSWORD}@postgres:5432/medlens
      - MONGO_URL=mongodb://mongo:27017
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - mongo
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: medlens-frontend:prod
    restart: always
    ports:
      - "80:5173"

  postgres:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_USER: medlens
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: medlens
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U medlens"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongo:
    image: mongo:6.0
    restart: always
    volumes:
      - mongodata:/data/db

volumes:
  pgdata:
  mongodata:
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
# Install Minikube (local) or configure access to EKS/GKE

# Verify cluster
kubectl cluster-info
```

### Backend Deployment

File: `k8s/backend-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: medlens-backend
  labels:
    app: medlens-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: medlens-backend
  template:
    metadata:
      labels:
        app: medlens-backend
    spec:
      containers:
      - name: backend
        image: medlens-backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: medlens-secrets
              key: database-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: medlens-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: medlens-backend-service
spec:
  selector:
    app: medlens-backend
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

### Frontend Deployment

File: `k8s/frontend-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: medlens-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: medlens-frontend
  template:
    metadata:
      labels:
        app: medlens-frontend
    spec:
      containers:
      - name: frontend
        image: medlens-frontend:latest
        ports:
        - containerPort: 5173
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: medlens-frontend-service
spec:
  selector:
    app: medlens-frontend
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5173
```

### Deploy to Kubernetes

```bash
# Create secrets
kubectl create secret generic medlens-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=jwt-secret="your-secret"

# Apply manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get deployments
kubectl get services
kubectl logs deployment/medlens-backend

# Scale backend
kubectl scale deployment medlens-backend --replicas=5

# Update image
kubectl set image deployment/medlens-backend backend=medlens-backend:v1.1
```

---

## AWS Deployment

### Prerequisites

```bash
# Install AWS CLI
# Configure AWS credentials
aws configure

# Create ECR repositories
aws ecr create-repository --repository-name medlens-backend --region us-east-1
aws ecr create-repository --repository-name medlens-frontend --region us-east-1
```

### Push Images to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Tag images
docker tag medlens-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/medlens-backend:latest
docker tag medlens-frontend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/medlens-frontend:latest

# Push
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/medlens-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/medlens-frontend:latest
```

### Create RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier medlens-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username medlens \
  --master-user-password <strong-password> \
  --allocated-storage 20 \
  --storage-type gp2 \
  --publicly-accessible false \
  --multi-az
```

### Create RDS MongoDB (DocumentDB)

```bash
aws docdb create-db-cluster \
  --db-cluster-identifier medlens-docdb \
  --engine docdb \
  --master-username medlens \
  --master-user-password <strong-password> \
  --backup-retention-period 7
```

### Create S3 Buckets

```bash
# Raw signals bucket
aws s3 mb s3://medlens-signals-prod --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket medlens-signals-prod \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket medlens-signals-prod \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}
    }]
  }'
```

### Deploy to EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name medlens-prod \
  --region us-east-1 \
  --nodegroup-name standard-nodes \
  --node-type t3.medium \
  --nodes 3

# Get kubeconfig
aws eks update-kubeconfig --name medlens-prod --region us-east-1

# Deploy
kubectl apply -f k8s/
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

File: `.github/workflows/ci.yml`

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-and-build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install backend dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run backend tests
      run: |
        cd backend
        pytest tests/ -v --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
    
    - name: Set up Node
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Build frontend
      run: |
        cd frontend
        npm run build
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Login to ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push backend image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: medlens-backend
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG backend/
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
    
    - name: Build and push frontend image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: medlens-frontend
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG frontend/
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
    
    - name: Deploy to EKS
      if: github.ref == 'refs/heads/main'
      run: |
        aws eks update-kubeconfig --name medlens-prod
        kubectl set image deployment/medlens-backend backend=<account>.dkr.ecr.us-east-1.amazonaws.com/medlens-backend:${{ github.sha }}
        kubectl set image deployment/medlens-frontend frontend=<account>.dkr.ecr.us-east-1.amazonaws.com/medlens-frontend:${{ github.sha }}
        kubectl rollout status deployment/medlens-backend
```

---

## Monitoring & Logging

### Prometheus Setup

```bash
# Deploy Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### Grafana Dashboard

Import JSON dashboard:

```json
{
  "dashboard": {
    "title": "MedLens Metrics",
    "panels": [
      {
        "title": "Predictions per minute",
        "targets": [
          {
            "expr": "rate(medlens_predictions_total[1m])"
          }
        ]
      },
      {
        "title": "Model Accuracy",
        "targets": [
          {
            "expr": "medlens_model_accuracy"
          }
        ]
      },
      {
        "title": "Prediction Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(medlens_prediction_latency_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

### CloudWatch Logging

```python
# backend/app/main.py
import logging
import watchtower

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        watchtower.CloudWatchLogHandler(log_group='medlens', stream_name='backend')
    ]
)
```

---

## Backup & Disaster Recovery

### PostgreSQL Backups

```bash
# Automated daily backups via AWS RDS
aws rds create-db-instance-read-replica \
  --db-instance-identifier medlens-db-backup \
  --source-db-instance-identifier medlens-db

# Manual backup
aws rds create-db-snapshot \
  --db-instance-identifier medlens-db \
  --db-snapshot-identifier medlens-db-$(date +%Y%m%d)
```

### S3 Backup

```bash
# Enable S3 cross-region replication
aws s3api put-bucket-replication \
  --bucket medlens-signals-prod \
  --replication-configuration file://replication.json
```

### Restore from Backup

```bash
# Restore RDS from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier medlens-db-restored \
  --db-snapshot-identifier medlens-db-20251129

# Restore S3 objects
aws s3 sync \
  s3://medlens-signals-backup/2025-11-29/ \
  s3://medlens-signals-prod/
```

---

## Performance Tuning

### Backend Optimization

```python
# Increase worker count
# In docker-compose or k8s, set workers:
# gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Enable caching
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend
from redis import asyncio as aioredis

@cached(namespace="analytics", expire=300)
@app.get("/analytics/")
async def get_analytics():
    ...
```

### Database Optimization

```sql
-- Index frequently queried columns
CREATE INDEX idx_predictions_record_id ON predictions(record_id);
CREATE INDEX idx_records_patient_id ON records(patient_id);
CREATE INDEX idx_users_username ON users(username);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM predictions WHERE record_id = 123;
```

### Frontend Optimization

```bash
# Enable gzip compression
# In frontend Dockerfile or Nginx config
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;

# Code splitting
npm run build -- --optimize-modules

# CDN configuration (CloudFront for AWS)
aws cloudfront create-distribution ...
```

---

## Troubleshooting

### Pod CrashLoopBackOff

```bash
kubectl logs deployment/medlens-backend
kubectl describe pod <pod-name>
```

### High CPU Usage

```bash
kubectl top nodes
kubectl top pod -A
```

### Database Connection Timeout

```bash
# Check database status
aws rds describe-db-instances --db-instance-identifier medlens-db

# Verify security group
aws ec2 describe-security-groups --group-ids sg-xxxxxx
```

---

## Checklist for Production Deployment

- [ ] Set strong database passwords
- [ ] Configure HTTPS/TLS certificates
- [ ] Enable multi-AZ RDS
- [ ] Setup CloudWatch monitoring
- [ ] Configure backups and replication
- [ ] Test disaster recovery
- [ ] Enable VPC security groups
- [ ] Setup auto-scaling policies
- [ ] Configure load balancer
- [ ] Enable access logs
- [ ] Setup alerts and notifications
- [ ] Create runbooks for common issues

---

## Support

For deployment issues or questions, refer to `DOCUMENTATION.md` or contact DevOps team.
