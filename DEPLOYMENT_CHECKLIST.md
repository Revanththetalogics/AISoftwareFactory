# AI Software Factory - Complete Deployment Checklist

## Phase 1: Prerequisites Check
□ Docker Desktop installed and running
□ Docker Compose available
□ Git repository cloned
□ Portainer access (if using)

## Phase 2: Local Testing Setup
□ Create project directory structure
□ Generate environment variables
□ Test basic container deployment
□ Verify health checks work

## Critical Backend Fix Required

### 🚨 **Urgent Issue**: Backend Container Crashing
**Symptom**: `/usr/local/bin/python: No module named uvicorn` repeated in logs
**Impact**: Entire application stack affected - backend API unavailable
**Priority**: HIGH - Must be fixed immediately

### 🔧 **Immediate Solutions**

**Option 1: Emergency Fix Script** *(Fastest)*
```bash
# Run emergency fix
./emergency-fix.sh  # Linux/Mac
./emergency-fix.ps1 # Windows
```

**Option 2: Manual Fix**
1. Stop crashing container: `docker stop ai-factory-backend`
2. Remove container: `docker rm ai-factory-backend`  
3. Run with uvicorn install: `docker run -d --name ai-factory-backend [same params] sh -c "pip install uvicorn && python main.py"`

**Option 3: Permanent Fix**
1. Update backend Dockerfile to include uvicorn
2. Rebuild image with proper dependencies
3. Redeploy with corrected image

### ✅ **Verification Steps**
- [ ] Backend container shows "running" status
- [ ] `docker logs ai-factory-backend` shows no uvicorn errors
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] Frontend can connect to backend API

## Phase 4: Production Deployment
□ Configure domain DNS (ai-staging.thetalogics.com)
□ Set up SSL certificates
□ Deploy to VPS
□ Configure monitoring

## Phase 5: Post-Deployment Validation
□ Verify all services are healthy
□ Test application functionality
□ Confirm SSL certificate installation
□ Set up backup procedures

---

## Detailed Troubleshooting Steps

### For Frontend Container Issues:
1. Check logs: `docker logs ai-factory-frontend`
2. Verify port 3000 is exposed and listening
3. Test health endpoint: `curl http://localhost:3000`
4. Check environment variables are set correctly

### For Ollama Container Issues:
1. Check logs: `docker logs ollama-ai`
2. Verify model downloads: `curl http://localhost:11434/api/tags`
3. Check disk space for model storage
4. Verify resource limits aren't too restrictive

### Common Fixes:
- Increase startup time in health checks
- Adjust resource allocations (CPU/Memory)
- Check network connectivity between containers
- Verify volume mounts are working