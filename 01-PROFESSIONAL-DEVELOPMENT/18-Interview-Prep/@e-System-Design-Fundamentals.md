# @e-System-Design-Fundamentals - System Design for Technical Interviews

## 🎯 Learning Objectives
- Master fundamental system design concepts and principles
- Learn structured approaches to system design interviews
- Understand scalability, reliability, and performance trade-offs
- Practice designing real-world systems from scratch

## 🔧 System Design Interview Framework

### The SNAKE Method
- **S**cope: Define requirements and constraints
- **N**umbers: Estimate scale and capacity
- **A**rchitecture: High-level design
- **K**ey Components: Detailed component design
- **E**valuate: Trade-offs and alternatives

### Interview Structure (45-60 minutes)
1. **Requirements Clarification** (5-10 min)
2. **Capacity Estimation** (5-10 min)
3. **High-Level Design** (10-15 min)
4. **Detailed Design** (15-20 min)
5. **Scale and Optimize** (5-10 min)

## 🔧 Core System Design Concepts

### Scalability Fundamentals

#### Horizontal vs Vertical Scaling
```
Vertical Scaling (Scale Up):
- Add more power (CPU, RAM) to existing machine
- Easier to implement
- Limited by hardware constraints
- Single point of failure

Horizontal Scaling (Scale Out):
- Add more machines to resource pool
- Better fault tolerance
- Complex coordination required
- Theoretically unlimited scaling
```

#### Load Balancing
```csharp
// Load Balancer Types and Algorithms

public enum LoadBalancingAlgorithm 
{
    RoundRobin,        // Distribute requests sequentially
    LeastConnections,  // Route to server with fewest active connections
    WeightedRoundRobin,// Assign weights based on server capacity
    IPHash,           // Hash client IP to determine server
    LeastResponseTime  // Route to server with fastest response
}

public class LoadBalancer 
{
    private List<Server> servers;
    private LoadBalancingAlgorithm algorithm;
    
    public Server GetServer() 
    {
        return algorithm switch 
        {
            LoadBalancingAlgorithm.RoundRobin => GetRoundRobinServer(),
            LoadBalancingAlgorithm.LeastConnections => GetLeastConnectionsServer(),
            LoadBalancingAlgorithm.WeightedRoundRobin => GetWeightedServer(),
            _ => GetRoundRobinServer()
        };
    }
}
```

### Database Design Patterns

#### SQL vs NoSQL Decision Matrix
```
SQL Databases (RDBMS):
✅ ACID compliance
✅ Complex queries and joins
✅ Structured data with relationships
✅ Strong consistency requirements
❌ Horizontal scaling challenges
❌ Schema rigidity

NoSQL Databases:
✅ Horizontal scaling
✅ Flexible schema
✅ High performance for simple queries
✅ Handle unstructured data
❌ Limited complex queries
❌ Eventual consistency
```

#### Database Sharding Strategies
```csharp
public class DatabaseSharding 
{
    // Horizontal Sharding - partition by key
    public int GetShardId(string userId, int numShards) 
    {
        return Math.Abs(userId.GetHashCode()) % numShards;
    }
    
    // Vertical Sharding - partition by feature
    public string GetDatabaseByTable(string tableName) 
    {
        return tableName switch 
        {
            "users" => "user_service_db",
            "orders" => "order_service_db",
            "products" => "catalog_service_db",
            _ => "main_db"
        };
    }
    
    // Directory-based Sharding
    public class ShardDirectory 
    {
        private Dictionary<string, string> userToShard = new();
        
        public string GetShardForUser(string userId) 
        {
            return userToShard.GetValueOrDefault(userId, "default_shard");
        }
    }
}
```

### Caching Strategies

#### Cache Patterns
```csharp
public class CachePatterns 
{
    private ICache cache;
    private IDatabase database;
    
    // Cache-Aside (Lazy Loading)
    public async Task<User> GetUserCacheAside(string userId) 
    {
        var cachedUser = await cache.GetAsync<User>($"user:{userId}");
        if (cachedUser != null) return cachedUser;
        
        var user = await database.GetUserAsync(userId);
        if (user != null) 
        {
            await cache.SetAsync($"user:{userId}", user, TimeSpan.FromHours(1));
        }
        return user;
    }
    
    // Write-Through
    public async Task UpdateUserWriteThrough(User user) 
    {
        await database.UpdateUserAsync(user);
        await cache.SetAsync($"user:{user.Id}", user, TimeSpan.FromHours(1));
    }
    
    // Write-Behind (Write-Back)
    public async Task UpdateUserWriteBehind(User user) 
    {
        await cache.SetAsync($"user:{user.Id}", user, TimeSpan.FromHours(1));
        // Queue for async database update
        await queueService.EnqueueUserUpdate(user);
    }
    
    // Refresh-Ahead
    public async Task RefreshAheadCache(string userId) 
    {
        var ttl = await cache.GetTTLAsync($"user:{userId}");
        if (ttl < TimeSpan.FromMinutes(10)) // Refresh before expiry
        {
            var user = await database.GetUserAsync(userId);
            await cache.SetAsync($"user:{userId}", user, TimeSpan.FromHours(1));
        }
    }
}
```

#### Cache Levels
```
Browser Cache → CDN → Load Balancer Cache → 
Application Cache → Database Cache → Disk Cache
```

### Microservices Architecture

#### Service Communication Patterns
```csharp
public class ServiceCommunication 
{
    // Synchronous - REST API
    public async Task<OrderResponse> CreateOrderSync(CreateOrderRequest request) 
    {
        var inventoryCheck = await inventoryService.CheckAvailabilityAsync(request.ProductId);
        if (!inventoryCheck.Available) 
            throw new OutOfStockException();
            
        var paymentResult = await paymentService.ProcessPaymentAsync(request.Payment);
        if (!paymentResult.Success) 
            throw new PaymentFailedException();
            
        return await orderService.CreateOrderAsync(request);
    }
    
    // Asynchronous - Message Queue
    public async Task CreateOrderAsync(CreateOrderRequest request) 
    {
        var orderCreatedEvent = new OrderCreatedEvent 
        {
            OrderId = Guid.NewGuid().ToString(),
            UserId = request.UserId,
            ProductId = request.ProductId,
            Timestamp = DateTime.UtcNow
        };
        
        await messageQueue.PublishAsync("order.created", orderCreatedEvent);
    }
    
    // Event Sourcing
    public class EventStore 
    {
        public async Task AppendEventAsync(string streamId, DomainEvent domainEvent) 
        {
            var eventData = new EventData 
            {
                EventId = Guid.NewGuid(),
                StreamId = streamId,
                EventType = domainEvent.GetType().Name,
                Data = JsonSerializer.Serialize(domainEvent),
                Timestamp = DateTime.UtcNow
            };
            
            await eventRepository.SaveAsync(eventData);
        }
    }
}
```

## 🔧 Common System Design Problems

### 1. URL Shortener (like bit.ly)

#### Requirements Analysis
```
Functional Requirements:
- Shorten long URLs
- Redirect shortened URLs to original
- Custom aliases (optional)
- URL expiration (optional)

Non-Functional Requirements:
- 100:1 read/write ratio
- 100M URLs shortened per day
- URL redirection < 100ms
- System available 99.9% of time

Capacity Estimation:
- Write: 100M / (24 * 3600) = 1160 URLs/sec
- Read: 1160 * 100 = 116K redirections/sec
- Storage: 100M * 365 * 5 years = 182.5B URLs
- Storage size: 182.5B * 500 bytes = 91.25TB
```

#### High-Level Architecture
```csharp
public class URLShortenerService 
{
    private readonly ICache cache;
    private readonly IDatabase database;
    private readonly IKeyGenerator keyGenerator;
    
    public async Task<string> ShortenURL(string originalUrl, string customAlias = null) 
    {
        // Validate URL
        if (!IsValidUrl(originalUrl)) 
            throw new InvalidUrlException();
        
        // Check if URL already exists
        var existingShortUrl = await database.GetShortUrlAsync(originalUrl);
        if (existingShortUrl != null) return existingShortUrl;
        
        // Generate short key
        string shortKey = customAlias ?? await keyGenerator.GenerateKeyAsync();
        
        // Check collision
        if (await database.KeyExistsAsync(shortKey)) 
        {
            if (customAlias != null) throw new AliasAlreadyExistsException();
            shortKey = await keyGenerator.GenerateKeyAsync();
        }
        
        // Store mapping
        var urlMapping = new UrlMapping 
        {
            ShortKey = shortKey,
            OriginalUrl = originalUrl,
            CreatedAt = DateTime.UtcNow,
            ExpiresAt = DateTime.UtcNow.AddYears(1)
        };
        
        await database.SaveMappingAsync(urlMapping);
        return $"https://short.ly/{shortKey}";
    }
    
    public async Task<string> ExpandURL(string shortKey) 
    {
        // Check cache first
        var cachedUrl = await cache.GetAsync($"url:{shortKey}");
        if (cachedUrl != null) return cachedUrl;
        
        // Fetch from database
        var mapping = await database.GetMappingAsync(shortKey);
        if (mapping == null || mapping.ExpiresAt < DateTime.UtcNow) 
            throw new UrlNotFoundException();
        
        // Cache the result
        await cache.SetAsync($"url:{shortKey}", mapping.OriginalUrl, TimeSpan.FromHours(24));
        
        // Update analytics asynchronously
        _ = Task.Run(() => UpdateAnalyticsAsync(shortKey));
        
        return mapping.OriginalUrl;
    }
}

// Key Generation Strategies
public class Base62KeyGenerator : IKeyGenerator 
{
    private const string Characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    private readonly Random random = new();
    
    public async Task<string> GenerateKeyAsync() 
    {
        var key = new char[7]; // 62^7 = 3.5 trillion combinations
        for (int i = 0; i < 7; i++) 
        {
            key[i] = Characters[random.Next(Characters.Length)];
        }
        return new string(key);
    }
}
```

### 2. Chat System Design

#### System Architecture
```csharp
public class ChatSystemDesign 
{
    // WebSocket Connection Management
    public class ConnectionManager 
    {
        private readonly ConcurrentDictionary<string, WebSocket> connections = new();
        
        public async Task AddConnectionAsync(string userId, WebSocket webSocket) 
        {
            connections.TryAdd(userId, webSocket);
            await NotifyUserOnlineAsync(userId);
        }
        
        public async Task RemoveConnectionAsync(string userId) 
        {
            connections.TryRemove(userId, out _);
            await NotifyUserOfflineAsync(userId);
        }
        
        public async Task SendMessageToUserAsync(string userId, ChatMessage message) 
        {
            if (connections.TryGetValue(userId, out var webSocket)) 
            {
                var messageJson = JsonSerializer.Serialize(message);
                await webSocket.SendAsync(
                    Encoding.UTF8.GetBytes(messageJson),
                    WebSocketMessageType.Text,
                    true,
                    CancellationToken.None
                );
            }
        }
    }
    
    // Message Service
    public class MessageService 
    {
        private readonly IMessageRepository messageRepository;
        private readonly INotificationService notificationService;
        
        public async Task<ChatMessage> SendMessageAsync(SendMessageRequest request) 
        {
            // Validate participants
            var chat = await GetChatAsync(request.ChatId);
            if (!chat.Participants.Contains(request.SenderId)) 
                throw new UnauthorizedAccessException();
            
            // Create message
            var message = new ChatMessage 
            {
                Id = Guid.NewGuid().ToString(),
                ChatId = request.ChatId,
                SenderId = request.SenderId,
                Content = request.Content,
                MessageType = request.MessageType,
                Timestamp = DateTime.UtcNow
            };
            
            // Store message
            await messageRepository.SaveMessageAsync(message);
            
            // Send to online users
            foreach (var participantId in chat.Participants) 
            {
                if (participantId != request.SenderId) 
                {
                    await connectionManager.SendMessageToUserAsync(participantId, message);
                    
                    // Send push notification if user is offline
                    if (!await IsUserOnlineAsync(participantId)) 
                    {
                        await notificationService.SendPushNotificationAsync(participantId, message);
                    }
                }
            }
            
            return message;
        }
    }
    
    // Message Storage Strategy
    public class MessageRepository 
    {
        // Partition messages by chat_id and timestamp
        public async Task SaveMessageAsync(ChatMessage message) 
        {
            var partition = GetPartition(message.ChatId, message.Timestamp);
            await database.InsertAsync($"messages_{partition}", message);
        }
        
        public async Task<List<ChatMessage>> GetMessagesAsync(string chatId, DateTime before, int limit) 
        {
            var partitions = GetPartitionsForTimeRange(chatId, before.AddMonths(-1), before);
            var messages = new List<ChatMessage>();
            
            foreach (var partition in partitions) 
            {
                var partitionMessages = await database.QueryAsync<ChatMessage>(
                    $"messages_{partition}",
                    "SELECT * FROM messages WHERE chat_id = @chatId AND timestamp < @before ORDER BY timestamp DESC LIMIT @limit",
                    new { chatId, before, limit }
                );
                messages.AddRange(partitionMessages);
            }
            
            return messages.OrderByDescending(m => m.Timestamp).Take(limit).ToList();
        }
    }
}
```

### 3. Social Media Feed Design

#### Feed Generation Strategies
```csharp
public class SocialMediaFeed 
{
    // Pull Model (On-demand generation)
    public class PullBasedFeedService 
    {
        public async Task<List<Post>> GenerateFeedAsync(string userId, int limit) 
        {
            // Get user's following list
            var followingIds = await GetFollowingAsync(userId);
            
            // Fetch recent posts from all followed users
            var posts = new List<Post>();
            foreach (var followingId in followingIds) 
            {
                var userPosts = await GetRecentPostsAsync(followingId, limit);
                posts.AddRange(userPosts);
            }
            
            // Sort by timestamp and apply ML ranking
            return posts
                .OrderByDescending(p => p.Timestamp)
                .Take(limit)
                .ToList();
        }
    }
    
    // Push Model (Pre-computed feeds)
    public class PushBasedFeedService 
    {
        public async Task OnPostCreatedAsync(Post post) 
        {
            // Get all followers of the post author
            var followerIds = await GetFollowersAsync(post.AuthorId);
            
            // Add post to each follower's pre-computed feed
            var tasks = followerIds.Select(followerId => 
                AddPostToFeedAsync(followerId, post)
            );
            
            await Task.WhenAll(tasks);
        }
        
        public async Task<List<Post>> GetFeedAsync(string userId, int limit) 
        {
            // Simply read from pre-computed feed
            return await GetPrecomputedFeedAsync(userId, limit);
        }
        
        private async Task AddPostToFeedAsync(string userId, Post post) 
        {
            var feedKey = $"feed:{userId}";
            await cache.ListPushAsync(feedKey, post);
            
            // Keep only recent N posts to prevent unlimited growth
            await cache.ListTrimAsync(feedKey, 0, 999);
        }
    }
    
    // Hybrid Model (Best of both worlds)
    public class HybridFeedService 
    {
        public async Task<List<Post>> GenerateFeedAsync(string userId, int limit) 
        {
            var userProfile = await GetUserProfileAsync(userId);
            
            if (userProfile.FollowingCount < 1000) 
            {
                // Use Pull model for users with few followings
                return await pullBasedService.GenerateFeedAsync(userId, limit);
            } 
            else 
            {
                // Use Push model for users with many followings
                return await pushBasedService.GetFeedAsync(userId, limit);
            }
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Architecture Review
```
PROMPT: "Review this system architecture for [SYSTEM_TYPE]. Identify potential bottlenecks, single points of failure, and scalability issues: [ARCHITECTURE_DESCRIPTION]"
```

### Capacity Planning
```
PROMPT: "Help me estimate capacity requirements for [SYSTEM]. Given [USER_COUNT] users with [USAGE_PATTERN], calculate storage, bandwidth, and compute needs."
```

### Technology Selection
```
PROMPT: "Compare database options for [USE_CASE]. Consider factors like consistency, scalability, query patterns, and operational complexity."
```

### Monitoring Strategy
```
PROMPT: "Design a comprehensive monitoring and alerting strategy for [SYSTEM]. Include key metrics, SLIs, SLOs, and alert thresholds."
```

## 💡 Key Highlights

### System Design Principles
- **Reliability**: System continues to work correctly even when failures occur
- **Scalability**: System remains performant as load increases
- **Availability**: System remains operational over time
- **Consistency**: All nodes see the same data simultaneously
- **Partition Tolerance**: System continues despite network failures

### CAP Theorem Trade-offs
- **CP Systems**: RDBMS, MongoDB - Choose consistency over availability
- **AP Systems**: Cassandra, DynamoDB - Choose availability over consistency
- **CA Systems**: Not realistic in distributed systems

### Performance Optimization Techniques
- **Caching**: Multiple layers (browser, CDN, application, database)
- **Database Optimization**: Indexing, query optimization, connection pooling
- **Asynchronous Processing**: Message queues, event-driven architecture
- **Content Delivery**: CDNs, geographic distribution
- **Load Distribution**: Load balancers, auto-scaling

### Common Anti-Patterns to Avoid
- **Premature Optimization**: Don't optimize before measuring
- **Single Point of Failure**: Ensure redundancy in critical components
- **Tight Coupling**: Design loosely coupled services
- **Ignoring Data Consistency**: Plan for eventual consistency scenarios
- **Over-Engineering**: Start simple, scale based on actual needs

### Essential Metrics to Monitor
- **Latency**: Response time percentiles (P50, P95, P99)
- **Throughput**: Requests per second, transactions per second
- **Error Rate**: 4xx/5xx error percentages
- **Availability**: Uptime percentage
- **Resource Utilization**: CPU, memory, disk, network usage

This comprehensive guide provides the foundation for succeeding in system design interviews and building scalable distributed systems.