# @b-Unity-Container-Deployment-Optimization - Scalable Game Server Containerization

## 🎯 Learning Objectives
- Master Docker containerization strategies for Unity applications and game servers
- Implement Kubernetes orchestration for scalable Unity multiplayer backends
- Optimize container performance and resource utilization for game workloads
- Create automated deployment pipelines for Unity server applications

## 🔧 Core Unity Container Architecture

### Unity Server Containerization Framework
```dockerfile
# Multi-stage Docker build for Unity server applications
FROM ubuntu:20.04 AS unity-base

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Unity dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    xvfb \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libgtk-3-0 \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# Install Unity Hub and Unity Editor
RUN wget -qO - https://hub.unity3d.com/linux/keys/public | apt-key add - \
    && echo "deb https://hub.unity3d.com/linux/repos/deb stable main" > /etc/apt/sources.list.d/unityhub.list \
    && apt-get update \
    && apt-get install -y unityhub

# Production stage for Unity server
FROM unity-base AS unity-server-production

# Set working directory
WORKDIR /app

# Copy Unity server build
COPY --from=build-stage /unity-project/Builds/LinuxServer/ .

# Create non-root user for security
RUN groupadd -r unityserver && useradd -r -g unityserver unityserver
RUN chown -R unityserver:unityserver /app

# Expose default Unity server ports
EXPOSE 7777/tcp
EXPOSE 7777/udp

# Health check configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Switch to non-root user
USER unityserver

# Environment variables for Unity server
ENV UNITY_SERVER_PORT=7777
ENV UNITY_MAX_PLAYERS=100
ENV UNITY_SERVER_NAME="Unity Container Server"

# Start Unity server
CMD ["./UnityServer.x86_64", "-batchmode", "-nographics", "-logFile", "/dev/stdout"]
```

### Kubernetes Deployment Configuration
```yaml
# Unity game server Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unity-game-server
  labels:
    app: unity-game-server
    version: v1.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: unity-game-server
  template:
    metadata:
      labels:
        app: unity-game-server
        version: v1.0
    spec:
      containers:
      - name: unity-server
        image: your-registry/unity-game-server:v1.0
        ports:
        - containerPort: 7777
          protocol: TCP
        - containerPort: 7777
          protocol: UDP
        env:
        - name: UNITY_SERVER_PORT
          value: "7777"
        - name: UNITY_MAX_PLAYERS
          value: "100"
        - name: SERVER_REGION
          valueFrom:
            fieldRef:
              fieldPath: metadata.labels['region']
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        volumeMounts:
        - name: game-data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: game-data
        persistentVolumeClaim:
          claimName: unity-game-data
      - name: logs
        emptyDir: {}
      nodeSelector:
        workload-type: game-server
      tolerations:
      - key: "game-server"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"

---
apiVersion: v1
kind: Service
metadata:
  name: unity-game-server-service
  labels:
    app: unity-game-server
spec:
  type: LoadBalancer
  ports:
  - port: 7777
    targetPort: 7777
    protocol: TCP
    name: tcp
  - port: 7777
    targetPort: 7777
    protocol: UDP
    name: udp
  selector:
    app: unity-game-server

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: unity-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: unity-game-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### Unity CI/CD Pipeline with Containers
```csharp
// Unity C# script for container health monitoring
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.Networking;

public class UnityContainerHealthManager : MonoBehaviour
{
    [System.Serializable]
    public class HealthMetrics
    {
        public float cpuUsage;
        public float memoryUsage;
        public int activeConnections;
        public int maxConnections;
        public float averageLatency;
        public int errorsPerMinute;
        public string serverStatus;
        public float uptime;
    }
    
    [SerializeField] private HealthMetrics currentHealth;
    [SerializeField] private int healthCheckPort = 8080;
    [SerializeField] private float healthCheckInterval = 30f;
    
    private Dictionary<string, object> healthData;
    private HttpListener httpListener;
    
    private void Start()
    {
        InitializeHealthMonitoring();
        StartCoroutine(UpdateHealthMetrics());
        StartHealthCheckEndpoint();
    }
    
    private void InitializeHealthMonitoring()
    {
        currentHealth = new HealthMetrics
        {
            serverStatus = "starting",
            uptime = 0f,
            activeConnections = 0,
            maxConnections = GetMaxConnectionsFromEnv(),
            errorsPerMinute = 0
        };
        
        healthData = new Dictionary<string, object>();
        
        Debug.Log($"Health monitoring initialized on port {healthCheckPort}");
    }
    
    private IEnumerator UpdateHealthMetrics()
    {
        while (true)
        {
            // Update health metrics
            currentHealth.cpuUsage = GetCPUUsage();
            currentHealth.memoryUsage = GetMemoryUsage();
            currentHealth.activeConnections = GetActiveConnectionCount();
            currentHealth.averageLatency = GetAverageLatency();
            currentHealth.uptime = Time.time;
            
            // Determine server status
            currentHealth.serverStatus = DetermineServerStatus();
            
            // Update health data dictionary
            UpdateHealthData();
            
            yield return new WaitForSeconds(healthCheckInterval);
        }
    }
    
    private void StartHealthCheckEndpoint()
    {
        StartCoroutine(HealthCheckServer());
    }
    
    private IEnumerator HealthCheckServer()
    {
        while (true)
        {
            // Simple HTTP server for Kubernetes health checks
            // In production, use a proper HTTP server implementation
            
            yield return new WaitForSeconds(1f);
            
            // Handle health check requests
            if (ShouldRespondToHealthCheck())
            {
                RespondToHealthCheck();
            }
        }
    }
    
    private string DetermineServerStatus()
    {
        if (currentHealth.cpuUsage > 90f || currentHealth.memoryUsage > 90f)
        {
            return "overloaded";
        }
        else if (currentHealth.activeConnections >= currentHealth.maxConnections * 0.8f)
        {
            return "near-capacity";
        }
        else if (currentHealth.errorsPerMinute > 10)
        {
            return "degraded";
        }
        else if (currentHealth.activeConnections > 0)
        {
            return "healthy";
        }
        else
        {
            return "idle";
        }
    }
    
    private float GetCPUUsage()
    {
        // Platform-specific CPU usage calculation
        return UnityEngine.Profiling.Profiler.GetRuntimeMemorySize(null) / 1024f / 1024f;
    }
    
    private float GetMemoryUsage()
    {
        return UnityEngine.Profiling.Profiler.GetTotalReservedMemory(UnityEngine.Profiling.Profiler.Area.Total) / 1024f / 1024f;
    }
    
    private int GetMaxConnectionsFromEnv()
    {
        string envMaxPlayers = System.Environment.GetEnvironmentVariable("UNITY_MAX_PLAYERS");
        return int.TryParse(envMaxPlayers, out int maxPlayers) ? maxPlayers : 100;
    }
    
    private void UpdateHealthData()
    {
        healthData.Clear();
        healthData["status"] = currentHealth.serverStatus;
        healthData["cpu_usage_percent"] = currentHealth.cpuUsage;
        healthData["memory_usage_mb"] = currentHealth.memoryUsage;
        healthData["active_connections"] = currentHealth.activeConnections;
        healthData["max_connections"] = currentHealth.maxConnections;
        healthData["average_latency_ms"] = currentHealth.averageLatency;
        healthData["uptime_seconds"] = currentHealth.uptime;
        healthData["timestamp"] = System.DateTime.UtcNow.ToString("o");
    }
}
```

### Docker Compose for Local Development
```yaml
# docker-compose.yml for Unity development environment
version: '3.8'

services:
  unity-server:
    build:
      context: .
      dockerfile: Dockerfile.unity-server
      target: unity-server-production
    image: unity-game-server:local
    container_name: unity-server-local
    ports:
      - "7777:7777/tcp"
      - "7777:7777/udp"
      - "8080:8080/tcp"  # Health check port
    environment:
      - UNITY_SERVER_PORT=7777
      - UNITY_MAX_PLAYERS=50
      - UNITY_SERVER_NAME=Local Unity Server
      - UNITY_LOG_LEVEL=Debug
    volumes:
      - ./game-data:/app/data
      - ./logs:/app/logs
    networks:
      - unity-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  unity-matchmaker:
    build:
      context: ./matchmaker
      dockerfile: Dockerfile
    image: unity-matchmaker:local
    container_name: unity-matchmaker-local
    ports:
      - "8081:8080"
    environment:
      - REDIS_URL=redis://redis:6379
      - SERVER_DISCOVERY_URL=http://unity-server:8080
    depends_on:
      - redis
      - unity-server
    networks:
      - unity-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: unity-redis-local
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - unity-network
    restart: unless-stopped
    command: redis-server --appendonly yes

  prometheus:
    image: prom/prometheus:latest
    container_name: unity-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - unity-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: unity-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - unity-network
    restart: unless-stopped

volumes:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  unity-network:
    driver: bridge
```

### Performance Optimization Strategies
```yaml
# Kubernetes resource optimization for Unity servers
apiVersion: v1
kind: ConfigMap
metadata:
  name: unity-server-optimization
data:
  # JVM-like optimization for Unity
  unity-optimization.conf: |
    # Memory optimization
    -force-gfx-direct
    -force-d3d11-no-singlethreaded
    -force-low-power-support
    
    # Performance settings
    -screen-width 1024
    -screen-height 768
    -screen-quality Beautiful
    -batchmode
    -nographics
    
    # Networking optimization
    -maxPlayerCount 100
    -sendRate 20
    -sendRateOnSerialize 15
  
  # Resource limits based on Unity requirements
  resource-profiles.yaml: |
    profiles:
      small:
        requests:
          memory: "256Mi"
          cpu: "100m"
        limits:
          memory: "1Gi"
          cpu: "500m"
      medium:
        requests:
          memory: "512Mi"
          cpu: "250m"
        limits:
          memory: "2Gi"
          cpu: "1000m"
      large:
        requests:
          memory: "1Gi"
          cpu: "500m"
        limits:
          memory: "4Gi"
          cpu: "2000m"
```

## 🚀 AI/LLM Integration Opportunities

### Automated Container Optimization
```
# Prompt Template for Container Performance Optimization
"Optimize this Unity server Docker container configuration for production deployment:

Current Configuration: [PASTE DOCKERFILE AND K8S CONFIG]
Target Environment: [AWS EKS / Google GKE / Azure AKS]
Expected Load: [Concurrent players, requests per second]
Resource Constraints: [Budget, performance requirements]

Provide optimizations for:
1. Docker image size reduction techniques
2. Multi-stage build improvements
3. Kubernetes resource allocation optimization
4. Security hardening recommendations
5. Monitoring and observability integration
6. Auto-scaling configuration improvements
7. Network performance optimization
8. Storage and persistence strategies

Include specific configuration files and implementation steps."
```

### Intelligent Resource Management
```python
# AI-powered container resource optimization
class UnityContainerOptimizer:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.ai_optimizer = AIOptimizer()
        
    def optimize_container_resources(self, deployment_name):
        """AI-driven container resource optimization"""
        
        current_metrics = self.metrics_collector.get_deployment_metrics(deployment_name)
        optimization_recommendations = self.ai_optimizer.analyze_resources(current_metrics)
        
        return {
            'cpu_recommendations': optimization_recommendations['cpu'],
            'memory_recommendations': optimization_recommendations['memory'],
            'scaling_recommendations': optimization_recommendations['scaling'],
            'cost_impact': optimization_recommendations['cost_analysis']
        }
```

## 💡 Key Highlights
- **Scalable Architecture**: Kubernetes orchestration enables automatic scaling based on player demand
- **Resource Efficiency**: Optimized container configurations reduce infrastructure costs while maintaining performance
- **Development Velocity**: Containerization enables consistent development, testing, and production environments
- **High Availability**: Load balancing and health checks ensure reliable game server uptime
- **Monitoring Integration**: Built-in observability with Prometheus, Grafana, and health check endpoints
- **Security Best Practices**: Non-root containers, resource limits, and network policies protect against attacks