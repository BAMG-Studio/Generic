# 🚀 Quick Start - Test ForgeTrace NOW

## Start in 3 Commands

```bash
cd /home/papaert/projects/ForgeTrace/forge_platform
./deploy.sh development
open http://localhost:3000/app/client-portal
```

## Test the Full Flow

### 1. Start Services (30 seconds)
```bash
cd forge_platform
docker-compose up -d
```

### 2. Create User (10 seconds)
```bash
docker-compose exec backend python -c "
from app.db.session import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

db = SessionLocal()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

user = User(
    email='test@forgetrace.com',
    hashed_password=pwd_context.hash('test123'),
    full_name='Test User',
    is_active=True,
    subscription_tier='professional'
)
db.add(user)
db.commit()
print('✅ User created: test@forgetrace.com / test123')
"
```

### 3. Get Token (5 seconds)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@forgetrace.com", "password": "test123"}' \
  | jq -r '.access_token'
```

### 4. Submit Audit (2 minutes)
```bash
TOKEN="paste_token_here"

curl -X POST http://localhost:8000/api/v1/audits \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repository": "https://github.com/django/django"}'
```

### 5. Check Status (5 seconds)
```bash
curl http://localhost:8000/api/v1/audits \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 6. Download Report (5 seconds)
```bash
AUDIT_ID="get_from_previous_command"

curl http://localhost:8000/api/v1/audits/$AUDIT_ID/report?format=json \
  -H "Authorization: Bearer $TOKEN" \
  -o report.json
```

## Or Use the UI

1. **Open**: http://localhost:3000/app/client-portal
2. **Login**: test@forgetrace.com / test123
3. **Submit**: Click "Submit Audit" tab
4. **Enter**: https://github.com/django/django
5. **Wait**: 1-2 minutes
6. **Download**: Click "Download" button

## Troubleshooting

### Services not starting?
```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

### Can't login?
```bash
# Check if user exists
docker-compose exec backend python cli.py list-users

# Create new user
docker-compose exec backend python cli.py create-user
```

### Audit failing?
```bash
# Check logs
docker-compose logs backend

# Test CLI directly
docker-compose exec backend forgetrace audit https://github.com/django/django --out /tmp/test
```

## What's Working

✅ Submit audits via API  
✅ Submit audits via UI  
✅ View audit history  
✅ Download reports (JSON/PDF)  
✅ Create API tokens  
✅ View usage stats  
✅ Authentication  
✅ Authorization  

## What's Not Working

⚠️ Data lost on restart (no database yet)  
⚠️ No real-time progress (must refresh)  
⚠️ No email notifications  
⚠️ No file upload (public repos only)  

## Next Steps

1. Test the platform
2. Report bugs
3. Request features
4. Plan production deployment

## Need Help?

- **Logs**: `docker-compose logs -f`
- **Docs**: `PROJECT_STATUS.md`
- **API**: http://localhost:8000/api/docs
- **Email**: hello@bamgstudio.com

---

**You're ready to test ForgeTrace! 🎉**
