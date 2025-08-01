# 03-Container-Deployment-Unity.md

## 🎯 Learning Objectives
- Master Docker containerization for Unity build environments and game servers
- Implement Kubernetes orchestration for scalable Unity multiplayer infrastructure
- Design containerized CI/CD pipelines for Unity projects
- Develop efficient container strategies for Unity WebGL and server deployments

## 🔧 Docker Containerization for Unity

### Unity Build Container
```dockerfile
# Dockerfile.unity-builder
FROM unityci/editor:2022.3.10f1-linux-il2cpp-3.0.0

# Set working directory
WORKDIR /project

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for WebGL builds
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install Android SDK for Android builds
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV ANDROID_HOME=$ANDROID_SDK_ROOT
ENV PATH=$PATH:$ANDROID_SDK_ROOT/tools:$ANDROID_SDK_ROOT/platform-tools

RUN mkdir -p $ANDROID_SDK_ROOT && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O /tmp/sdk-tools.zip && \
    unzip -q /tmp/sdk-tools.zip -d $ANDROID_SDK_ROOT && \
    rm /tmp/sdk-tools.zip && \
    mv $ANDROID_SDK_ROOT/cmdline-tools $ANDROID_SDK_ROOT/latest && \
    mkdir -p $ANDROID_SDK_ROOT/cmdline-tools && \
    mv $ANDROID_SDK_ROOT/latest $ANDROID_SDK_ROOT/cmdline-tools/

# Accept Android licenses
RUN yes | $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --licenses > /dev/null 2>&1

# Install required Android SDK components
RUN $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager \
    "platforms;android-33" \
    "build-tools;33.0.0" \
    "platform-tools" \
    "ndk;25.1.8937393"

# Copy build scripts
COPY Scripts/Docker/ /scripts/
RUN chmod +x /scripts/*.sh

# Set Unity license from environment variable
ENV UNITY_LICENSE_CONTENT=""

# Default command
CMD ["/bin/bash"]
```

### Unity Build Script for Container
```bash
#!/bin/bash
# Scripts/Docker/build-unity.sh

set -e

# Configuration
PROJECT_PATH="/project"
BUILD_OUTPUT_PATH="/builds"
BUILD_METHOD="BuildAutomation.PerformBuild"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --build-number)
            BUILD_NUMBER="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --development)
            DEVELOPMENT="true"
            shift
            ;;
        --il2cpp)
            IL2CPP="true"
            shift
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Set defaults
PLATFORM=${PLATFORM:-"StandaloneLinux64"}
BUILD_NUMBER=${BUILD_NUMBER:-$(date +%Y%m%d%H%M)}
VERSION=${VERSION:-"1.0.0"}
DEVELOPMENT=${DEVELOPMENT:-"false"}
IL2CPP=${IL2CPP:-"false"}

echo "🚀 Starting Unity build..."
echo "Platform: $PLATFORM"
echo "Build Number: $BUILD_NUMBER"
echo "Version: $VERSION"
echo "Development: $DEVELOPMENT"
echo "IL2CPP: $IL2CPP"

# Setup Unity license
if [ ! -z "$UNITY_LICENSE_CONTENT" ]; then
    echo "📄 Setting up Unity license..."
    echo "$UNITY_LICENSE_CONTENT" | base64 -d > /tmp/Unity_v2022.x.ulf
    unity-editor -batchmode -quit -manualLicenseFile /tmp/Unity_v2022.x.ulf -logFile /dev/stdout
fi

# Create build output directory
mkdir -p "$BUILD_OUTPUT_PATH"

# Build command
BUILD_ARGS=""
BUILD_ARGS="$BUILD_ARGS -batchmode"
BUILD_ARGS="$BUILD_ARGS -quit"
BUILD_ARGS="$BUILD_ARGS -projectPath $PROJECT_PATH"
BUILD_ARGS="$BUILD_ARGS -executeMethod $BUILD_METHOD"
BUILD_ARGS="$BUILD_ARGS -buildTarget $PLATFORM"
BUILD_ARGS="$BUILD_ARGS -buildNumber $BUILD_NUMBER"
BUILD_ARGS="$BUILD_ARGS -version $VERSION"
BUILD_ARGS="$BUILD_ARGS -logFile /dev/stdout"

if [ "$DEVELOPMENT" = "true" ]; then
    BUILD_ARGS="$BUILD_ARGS -development"
fi

if [ "$IL2CPP" = "true" ]; then
    BUILD_ARGS="$BUILD_ARGS -il2cpp"
fi

# Android-specific setup
if [ "$PLATFORM" = "Android" ]; then
    BUILD_ARGS="$BUILD_ARGS -android-keystore-path /keys/keystore.keystore"
    BUILD_ARGS="$BUILD_ARGS -android-keystore-pass $ANDROID_KEYSTORE_PASS"
    BUILD_ARGS="$BUILD_ARGS -android-keyalias-name $ANDROID_KEYALIAS_NAME"
    BUILD_ARGS="$BUILD_ARGS -android-keyalias-pass $ANDROID_KEYALIAS_PASS"
fi

echo "🔨 Executing Unity build command..."
unity-editor $BUILD_ARGS

# Check if build succeeded
if [ $? -eq 0 ]; then
    echo "✅ Unity build completed successfully!"
    
    # Copy build artifacts to output directory
    if [ -d "$PROJECT_PATH/builds" ]; then
        cp -r "$PROJECT_PATH/builds/"* "$BUILD_OUTPUT_PATH/"
        echo "📦 Build artifacts copied to $BUILD_OUTPUT_PATH"
    fi
    
    # Generate build metadata
    cat > "$BUILD_OUTPUT_PATH/build-metadata.json" << EOF
{
    "platform": "$PLATFORM",
    "buildNumber": "$BUILD_NUMBER",
    "version": "$VERSION",
    "development": $DEVELOPMENT,
    "il2cpp": $IL2CPP,
    "buildTime": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "unityVersion": "$(unity-editor -version | head -n 1)"
}
EOF
    
else
    echo "❌ Unity build failed!"
    exit 1
fi
```

### Unity Game Server Container
```dockerfile
# Dockerfile.game-server
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    libc6-dev \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxcursor1 \
    libxrandr2 \
    libxi6 \
    libxinerama1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -s /bin/bash gameserver

# Create directories
RUN mkdir -p /app/server /app/data /app/logs && \
    chown -R gameserver:gameserver /app

# Copy game server binary
COPY --from=build-stage /builds/linux/GameServer /app/server/
COPY ServerConfig/ /app/server/config/

# Set permissions
RUN chmod +x /app/server/GameServer && \
    chown -R gameserver:gameserver /app

# Switch to non-root user
USER gameserver

# Set working directory
WORKDIR /app/server

# Expose ports
EXPOSE 7777/tcp 7777/udp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Environment variables
ENV SERVER_PORT=7777
ENV MAX_PLAYERS=20
ENV SERVER_NAME="Unity Game Server"
ENV LOG_LEVEL=INFO

# Start the game server
CMD ["./GameServer", "-batchmode", "-nographics", "-port", "$SERVER_PORT", "-maxplayers", "$MAX_PLAYERS"]
```

### Docker Compose for Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Unity Build Service
  unity-builder:
    build:
      context: .
      dockerfile: Dockerfile.unity-builder
    container_name: unity-builder
    volumes:
      - .:/project
      - ./builds:/builds
      - ./cache/Library:/project/Library
    environment:
      - UNITY_LICENSE_CONTENT=${UNITY_LICENSE_CONTENT}
      - BUILD_NUMBER=${BUILD_NUMBER:-1}
      - VERSION=${VERSION:-1.0.0}
    networks:
      - unity-network

  # Game Server
  game-server:
    build:
      context: .
      dockerfile: Dockerfile.game-server
    container_name: unity-game-server
    ports:
      - "7777:7777/tcp"
      - "7777:7777/udp"
      - "8080:8080"  # Health check port
    volumes:
      - ./server-data:/app/data
      - ./server-logs:/app/logs
    environment:
      - SERVER_PORT=7777
      - MAX_PLAYERS=20
      - SERVER_NAME=Unity Development Server
      - LOG_LEVEL=DEBUG
    restart: unless-stopped
    depends_on:
      - database
      - redis
    networks:
      - unity-network

  # Database for game data
  database:
    image: postgres:15
    container_name: unity-database
    environment:
      - POSTGRES_DB=gamedb
      - POSTGRES_USER=gameuser
      - POSTGRES_PASSWORD=${DB_PASSWORD:-gamepassword}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - unity-network

  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    container_name: unity-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redispassword}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - unity-network

  # Web Server for WebGL builds
  webgl-server:
    image: nginx:alpine
    container_name: unity-webgl-server
    ports:
      - "8081:80"
    volumes:
      - ./builds/webgl:/usr/share/nginx/html
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - unity-builder
    networks:
      - unity-network

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: unity-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - unity-network

  grafana:
    image: grafana/grafana:latest
    container_name: unity-grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    networks:
      - unity-network

networks:
  unity-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

## 🚀 Kubernetes Orchestration

### Unity Game Server Deployment
```yaml
# k8s/game-server-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unity-game-server
  labels:
    app: unity-game-server
    tier: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: unity-game-server
  template:
    metadata:
      labels:
        app: unity-game-server
    spec:
      containers:
      - name: game-server
        image: your-registry/unity-game-server:latest
        ports:
        - containerPort: 7777
          name: game-port
          protocol: UDP
        - containerPort: 8080
          name: health-port
          protocol: TCP
        env:
        - name: SERVER_PORT
          value: "7777"
        - name: MAX_PLAYERS
          valueFrom:
            configMapKeyRef:
              name: game-config
              key: max-players
        - name: DB_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: connection-string
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        volumeMounts:
        - name: server-data
          mountPath: /app/data
        - name: server-logs
          mountPath: /app/logs
      volumes:
      - name: server-data
        persistentVolumeClaim:
          claimName: server-data-pvc
      - name: server-logs
        emptyDir: {}
      restartPolicy: Always
      
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
    protocol: UDP
    name: game-port
  - port: 8080
    targetPort: 8080
    protocol: TCP
    name: health-port
  selector:
    app: unity-game-server

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: server-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### Auto-scaling Configuration
```yaml
# k8s/game-server-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: unity-game-server-hpa
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
  - type: Pods
    pods:
      metric:
        name: concurrent_players
      target:
        type: AverageValue
        averageValue: "15"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
```

### CI/CD Pipeline with Kubernetes
```yaml
# .github/workflows/k8s-deploy.yml
name: Unity K8s Deployment

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build Unity Project
        uses: game-ci/unity-builder@v2
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
        with:
          unity-version: 2022.3.10f1
          target-platform: StandaloneLinux64
          build-name: GameServer
          build-path: builds/linux/

      - name: Build and push Docker image
        id: build
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile.game-server
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Configure kubectl
        uses: azure/k8s-set-context@v1
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}

      - name: Deploy to staging
        uses: azure/k8s-deploy@v1
        with:
          namespace: unity-staging
          manifests: |
            k8s/game-server-deployment.yaml
            k8s/game-server-hpa.yaml
          images: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ needs.build-and-push.outputs.image-digest }}

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/unity-game-server -n unity-staging --timeout=300s
          kubectl get services -n unity-staging

  deploy-production:
    needs: [build-and-push, deploy-staging]
    runs-on: ubuntu-latest
    environment: production
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Configure kubectl
        uses: azure/k8s-set-context@v1
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}

      - name: Deploy to production
        uses: azure/k8s-deploy@v1
        with:
          namespace: unity-production
          manifests: |
            k8s/game-server-deployment.yaml
            k8s/game-server-hpa.yaml
          images: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ needs.build-and-push.outputs.image-digest }}
          strategy: rolling

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/unity-game-server -n unity-production --timeout=600s
          kubectl get services -n unity-production

      - name: Run smoke tests
        run: |
          # Add smoke tests for production deployment
          ./scripts/smoke-tests.sh ${{ steps.get-service.outputs.external-ip }}
```

## 🚀 AI/LLM Integration Opportunities

### Container Optimization Analysis
```
PROMPT TEMPLATE - Container Optimization:

"Analyze and optimize this Unity Docker configuration:

```dockerfile
[PASTE YOUR DOCKERFILE]
```

```yaml
[PASTE YOUR DOCKER-COMPOSE OR K8S MANIFESTS]
```

Project Requirements:
- Platform: [Mobile Server/PC Server/WebGL/etc.]
- Scale: [Small/Medium/Large deployment]
- Performance: [Low latency/High throughput/Balanced]
- Budget: [Cost-conscious/Performance-focused/Balanced]

Provide optimizations for:
1. Image size reduction strategies
2. Multi-stage build improvements
3. Resource allocation optimization
4. Security hardening recommendations
5. Caching and layer optimization
6. Runtime performance improvements
7. Monitoring and observability setup"
```

### Kubernetes Strategy Design
```
PROMPT TEMPLATE - K8s Architecture:

"Design a Kubernetes architecture for this Unity multiplayer game:

Game Details:
- Type: [Battle Royale/MMORPG/MOBA/etc.]
- Expected Players: [100/1K/10K/100K concurrent]
- Regions: [Single/Multi-region deployment]
- Infrastructure: [Cloud provider/On-premise/Hybrid]

Create architecture including:
1. Pod and service topology
2. Auto-scaling strategies and triggers
3. Load balancing and traffic routing
4. Persistent storage solutions
5. Service mesh considerations
6. Security policies and network isolation
7. Monitoring and logging strategy
8. Disaster recovery and backup plans
9. Cost optimization recommendations"
```

## 💡 Key Container Principles for Unity

### Essential Containerization Checklist
- **Minimal base images** - Use slim images to reduce attack surface and size
- **Multi-stage builds** - Separate build and runtime environments
- **Non-root users** - Run containers with least privilege
- **Health checks** - Implement proper liveness and readiness probes
- **Resource limits** - Set appropriate CPU and memory constraints
- **Persistent data** - Properly handle game state and user data storage
- **Secrets management** - Secure handling of credentials and API keys
- **Monitoring integration** - Include observability from the start

### Common Unity Container Challenges
1. **Large build sizes** - Unity builds can be several GB
2. **Graphics dependencies** - Headless server setup complexity
3. **Platform-specific builds** - Different containers for different targets
4. **State management** - Handling persistent game state in containers
5. **Networking complexity** - UDP/TCP port management in orchestration
6. **Resource requirements** - Unity servers can be resource-intensive
7. **Licensing** - Unity licensing in containerized environments
8. **Asset streaming** - Managing large asset downloads in containers

This container deployment system provides Unity developers with production-ready containerization and orchestration solutions, enabling scalable, reliable, and efficient deployment of Unity applications across development, staging, and production environments.