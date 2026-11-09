# Kubernetes for Developers

## Overview

Kubernetes (K8s) is a container orchestration platform that automates deployment, scaling, and management of containerized applications. This guide covers the essential concepts developers need to work effectively with Kubernetes.

## Core Concepts

### Pods
- Smallest deployable unit in Kubernetes
- Contains one or more containers sharing network and storage
- Ephemeral — pods are replaced, not updated

### Services
- **ClusterIP**: Internal service discovery (default)
- **NodePort**: Expose on each node's IP at a static port
- **LoadBalancer**: External load balancer (cloud provider)
- **Headless**: Direct pod access (for stateful sets)

### Deployments
- Manages replica sets of pods
- Rolling updates: gradual replacement of old pods
- Rollback: revert to previous revision

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:1.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### ConfigMaps and Secrets
- **ConfigMap**: Non-sensitive configuration data
- **Secret**: Sensitive data (base64 encoded, use encryption at rest)
- Mount as environment variables or volumes

## Essential Patterns

### Health Checks
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```
- **Liveness**: Restart container if unhealthy
- **Readiness**: Remove from service if not ready

### Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Staff-Level Insights

### Resource Management
- Always set **requests** and **limits** — without them, pods compete for resources
- Set requests based on **P95 usage**, not averages
- **Staff insight**: Over-provisioning wastes money; under-provisioning causes OOM kills. Use Vertical Pod Autoscaler (VPA) recommendations to right-size resources, then set HPA for scaling.

### Graceful Shutdown
- Kubernetes sends SIGTERM, waits for `terminationGracePeriodSeconds` (default 30s)
- Handle SIGTERM in your app to stop accepting requests and finish in-flight requests
- **Staff insight**: Set `preStop` hook with sleep to give time for load balancer to remove the pod from rotation:
```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 10"]
```

### Zero-Downtime Deployments
- Use **rolling updates** with proper readiness probes
- Set `maxUnavailable: 0` and `maxSurge: 1` for safe deployments
- **Staff insight**: The #1 cause of deployment downtime is missing or misconfigured readiness probes. Without them, Kubernetes routes traffic to pods before they're ready to serve.
