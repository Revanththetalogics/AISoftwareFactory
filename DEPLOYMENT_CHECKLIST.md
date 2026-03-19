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

## Phase 3: Troubleshooting Unhealthy Containers
□ Check container logs
□ Verify health check configurations
□ Test network connectivity
□ Review resource allocations

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