# DocumentFiller v3.0 - Deployment Guide

Complete deployment guide for production environments.

## 🚀 Deployment Options

### 1. Kubernetes (Recommended for Scale)

**Prerequisites**:
- Kubernetes cluster (1.24+)
- kubectl configured
- Ingress controller (nginx)
- Cert-manager (for SSL)

**Deploy**:
```bash
# Apply all resources
kubectl apply -f kubernetes/deployment.yaml

# Check status
kubectl get pods -n documentfiller
kubectl get svc -n documentfiller

# Get external IP
kubectl get svc documentfiller-frontend -n documentfiller
```

**Access**: http://<EXTERNAL-IP>

**Features**:
- ✅ Auto-scaling (3-10 replicas)
- ✅ PostgreSQL StatefulSet
- ✅ SSL/TLS with cert-manager
- ✅ Health checks
- ✅ Resource limits

---

### 2. AWS (ECS + RDS)

**Prerequisites**:
- AWS Account
- AWS CLI configured
- Docker images pushed to ECR

**Deploy**:
```bash
# Create ECR repositories
aws ecr create-repository --repository-name documentfiller-backend
aws ecr create-repository --repository-name documentfiller-frontend

# Build and push images
./deploy/scripts/build-and-push.sh

# Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name documentfiller-prod \
  --template-body file://aws/cloudformation.yaml \
  --parameters ParameterKey=KeyPairName,ParameterValue=your-key \
  --capabilities CAPABILITY_IAM

# Check status
aws cloudformation describe-stacks --stack-name documentfiller-prod
```

**Get URL**:
```bash
aws cloudformation describe-stacks \
  --stack-name documentfiller-prod \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text
```

**Features**:
- ✅ RDS PostgreSQL (Multi-AZ)
- ✅ ECS Fargate (serverless)
- ✅ Application Load Balancer
- ✅ Auto-scaling
- ✅ CloudWatch logging

---

### 3. Docker Compose (Development/Small Scale)

**Deploy**:
```bash
# Production mode
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale backend=3
```

**Features**:
- ✅ Quick setup
- ✅ Local development
- ✅ Small deployments
- ⚠️  Limited scaling

---

## 🔧 Configuration

### Environment Variables

**Backend (.env)**:
```env
# Required
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host:5432/db

# Optional
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
ENCRYPTION_PASSWORD=your-encryption-password
```

**Frontend**:
```env
VITE_API_URL=https://api.yourdomain.com
```

### Database Migration

**Initial setup**:
```bash
# Run migrations
python -c "from backend.database import init_db; init_db()"

# Create admin user
python -c "
from backend.database import create_user
from backend.auth import get_password_hash
create_user('admin@example.com', 'admin', get_password_hash('changeme'))
"
```

---

## 🔐 Security Checklist

Before going to production:

- [ ] **Change all default passwords**
- [ ] **Generate strong SECRET_KEY**
- [ ] **Enable HTTPS/TLS**
- [ ] **Configure firewall rules**
- [ ] **Set up rate limiting**
- [ ] **Enable database backups**
- [ ] **Configure CORS properly**
- [ ] **Set up monitoring**
- [ ] **Enable audit logging**
- [ ] **Scan for vulnerabilities**

---

## 📊 Monitoring

### Health Checks

**Backend**:
```bash
curl http://localhost:8000/
# Should return: {"status": "online", ...}
```

**Database**:
```bash
pg_isready -h localhost -p 5432
```

### Metrics

**Kubernetes**:
```bash
# CPU/Memory usage
kubectl top pods -n documentfiller

# Logs
kubectl logs -f deployment/documentfiller-backend -n documentfiller
```

**AWS**:
```bash
# CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=documentfiller-backend \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

---

## 🔄 Scaling

### Horizontal Scaling

**Kubernetes**:
```bash
# Manual scale
kubectl scale deployment documentfiller-backend --replicas=5 -n documentfiller

# HPA already configured (3-10 replicas)
kubectl get hpa -n documentfiller
```

**AWS ECS**:
```bash
# Update desired count
aws ecs update-service \
  --cluster documentfiller-prod-cluster \
  --service documentfiller-backend \
  --desired-count 5
```

### Vertical Scaling

**Kubernetes**: Edit deployment.yaml resources
**AWS**: Update task definition with larger CPU/memory

---

## 💾 Backup & Recovery

### Database Backups

**Automated** (AWS RDS):
- Enabled by default (7-day retention)
- Point-in-time recovery available

**Manual** (PostgreSQL):
```bash
# Backup
pg_dump -h localhost -U documentfiller documentfiller > backup.sql

# Restore
psql -h localhost -U documentfiller documentfiller < backup.sql
```

### Disaster Recovery

1. **Database**: Restore from automated backups
2. **Files**: Stored in DB, included in backups
3. **Configuration**: Version controlled (this repo)

---

## 🧪 Testing Deployment

**Smoke tests**:
```bash
# Health check
curl https://yourdomain.com/api/ | jq .status

# Register user
curl -X POST https://yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123"}'

# Login
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start**:
```bash
# Check logs
kubectl logs deployment/documentfiller-backend -n documentfiller

# Verify database connection
kubectl exec -it deployment/documentfiller-backend -n documentfiller -- \
  python -c "from database import engine; print(engine.connect())"
```

**Database connection fails**:
- Check security groups/firewall
- Verify credentials in secrets
- Test connectivity from pod

**High CPU usage**:
- Check for infinite loops in logs
- Verify HPA is working
- Consider vertical scaling

---

## 📚 Additional Resources

- [Kubernetes Docs](https://kubernetes.io/docs/)
- [AWS ECS Docs](https://docs.aws.amazon.com/ecs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)

---

## 🎯 Performance Tuning

### Backend
- Use gunicorn workers: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app`
- Enable response caching for static endpoints
- Use connection pooling for database

### Frontend
- Enable CDN for static assets
- Implement code splitting
- Use lazy loading for routes

### Database
- Add indexes for frequently queried columns
- Configure connection pooling
- Enable query caching

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Review this guide
3. Check GitHub issues
4. Contact support

---

**Version**: 3.0.0
**Last Updated**: 2025-11-20
