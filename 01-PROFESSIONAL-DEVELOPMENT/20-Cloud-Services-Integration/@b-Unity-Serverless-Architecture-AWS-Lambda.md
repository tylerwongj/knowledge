# @b-Unity-Serverless-Architecture-AWS-Lambda - Scalable Game Backend Systems

## 🎯 Learning Objectives
- Master serverless architecture design patterns for Unity game backends
- Implement AWS Lambda functions for game services and real-time processing
- Create cost-effective, auto-scaling game server architectures
- Develop event-driven game systems with cloud integration

## 🔧 Core Serverless Unity Architecture

### Unity AWS Lambda Integration Framework
```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using Newtonsoft.Json;

public class UnityServerlessManager : MonoBehaviour
{
    [System.Serializable]
    public class ServerlessConfiguration
    {
        public string awsRegion = "us-east-1";
        public string apiGatewayUrl;
        public string cognitoUserPoolId;
        public string cognitoClientId;
        public bool enableCompression = true;
        public int timeoutSeconds = 30;
    }
    
    [SerializeField] private ServerlessConfiguration config;
    
    // Lambda Function Endpoints
    private Dictionary<string, string> lambdaEndpoints;
    private Dictionary<string, object> cachedResponses;
    
    [System.Serializable]
    public class LambdaRequest
    {
        public string functionName;
        public string playerId;
        public Dictionary<string, object> payload;
        public Dictionary<string, string> headers;
        public long timestamp;
    }
    
    [System.Serializable]
    public class LambdaResponse
    {
        public int statusCode;
        public Dictionary<string, object> body;
        public Dictionary<string, string> headers;
        public bool success;
        public string errorMessage;
    }
    
    private void Start()
    {
        InitializeServerlessConnection();
    }
    
    private void InitializeServerlessConnection()
    {
        lambdaEndpoints = new Dictionary<string, string>
        {
            {"player-stats", $"{config.apiGatewayUrl}/player-stats"},
            {"leaderboard", $"{config.apiGatewayUrl}/leaderboard"},
            {"achievements", $"{config.apiGatewayUrl}/achievements"},
            {"matchmaking", $"{config.apiGatewayUrl}/matchmaking"},
            {"game-events", $"{config.apiGatewayUrl}/game-events"},
            {"user-progress", $"{config.apiGatewayUrl}/user-progress"},
            {"analytics", $"{config.apiGatewayUrl}/analytics"},
            {"notifications", $"{config.apiGatewayUrl}/notifications"}
        };
        
        cachedResponses = new Dictionary<string, object>();
        
        Debug.Log("Unity Serverless Manager initialized with AWS Lambda integration");
    }
    
    public IEnumerator InvokeLambdaFunction(string functionName, Dictionary<string, object> payload, System.Action<LambdaResponse> callback)
    {
        if (!lambdaEndpoints.ContainsKey(functionName))
        {
            callback(new LambdaResponse { success = false, errorMessage = $"Function {functionName} not configured" });
            yield break;
        }
        
        var request = new LambdaRequest
        {
            functionName = functionName,
            playerId = GetPlayerId(),
            payload = payload,
            timestamp = System.DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
            headers = GetAuthHeaders()
        };
        
        string jsonPayload = JsonConvert.SerializeObject(request);
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonPayload);
        
        using (UnityWebRequest webRequest = new UnityWebRequest(lambdaEndpoints[functionName], "POST"))
        {
            webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            webRequest.SetRequestHeader("Content-Type", "application/json");
            webRequest.SetRequestHeader("Authorization", GetAuthToken());
            webRequest.timeout = config.timeoutSeconds;
            
            yield return webRequest.SendWebRequest();
            
            var response = ProcessLambdaResponse(webRequest);
            callback(response);
        }
    }
    
    public IEnumerator UpdatePlayerStats(Dictionary<string, object> stats, System.Action<bool> callback)
    {
        yield return StartCoroutine(InvokeLambdaFunction("player-stats", stats, (response) =>
        {
            if (response.success)
            {
                Debug.Log("Player stats updated successfully");
                callback(true);
            }
            else
            {
                Debug.LogError($"Failed to update player stats: {response.errorMessage}");
                callback(false);
            }
        }));
    }
    
    public IEnumerator GetLeaderboard(string leaderboardType, int limit, System.Action<List<LeaderboardEntry>> callback)
    {
        var payload = new Dictionary<string, object>
        {
            {"leaderboard_type", leaderboardType},
            {"limit", limit},
            {"player_id", GetPlayerId()}
        };
        
        yield return StartCoroutine(InvokeLambdaFunction("leaderboard", payload, (response) =>
        {
            if (response.success)
            {
                var leaderboardData = JsonConvert.DeserializeObject<List<LeaderboardEntry>>(
                    response.body["leaderboard"].ToString());
                callback(leaderboardData);
            }
            else
            {
                callback(new List<LeaderboardEntry>());
            }
        }));
    }
    
    private LambdaResponse ProcessLambdaResponse(UnityWebRequest webRequest)
    {
        var response = new LambdaResponse();
        
        if (webRequest.result == UnityWebRequest.Result.Success)
        {
            response.statusCode = (int)webRequest.responseCode;
            response.success = webRequest.responseCode >= 200 && webRequest.responseCode < 300;
            
            try
            {
                response.body = JsonConvert.DeserializeObject<Dictionary<string, object>>(webRequest.downloadHandler.text);
            }
            catch (System.Exception ex)
            {
                response.success = false;
                response.errorMessage = $"JSON parsing error: {ex.Message}";
            }
        }
        else
        {
            response.success = false;
            response.errorMessage = webRequest.error;
            response.statusCode = (int)webRequest.responseCode;
        }
        
        return response;
    }
}
```

### AWS Lambda Function Examples for Unity Games
```python
# Python Lambda functions for Unity game backend
import json
import boto3
import uuid
from decimal import Decimal
from datetime import datetime, timezone

# DynamoDB client
dynamodb = boto3.resource('dynamodb')
player_stats_table = dynamodb.Table('unity-player-stats')
leaderboard_table = dynamodb.Table('unity-leaderboard')
achievements_table = dynamodb.Table('unity-achievements')

def lambda_handler_player_stats(event, context):
    """Lambda function for Unity player statistics management"""
    
    try:
        # Parse request
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        player_id = body.get('playerId')
        action = body.get('action', 'update')
        stats_data = body.get('payload', {})
        
        if not player_id:
            return create_error_response(400, 'Player ID is required')
        
        if action == 'update':
            return update_player_stats(player_id, stats_data)
        elif action == 'get':
            return get_player_stats(player_id)
        elif action == 'increment':
            return increment_player_stats(player_id, stats_data)
        else:
            return create_error_response(400, 'Invalid action')
            
    except Exception as e:
        print(f"Error in player_stats handler: {str(e)}")
        return create_error_response(500, 'Internal server error')

def update_player_stats(player_id, stats_data):
    """Update player statistics in DynamoDB"""
    
    try:
        current_timestamp = datetime.now(timezone.utc).isoformat()
        
        # Prepare update expression
        update_expression = "SET last_updated = :timestamp"
        expression_values = {':timestamp': current_timestamp}
        
        for stat_name, stat_value in stats_data.items():
            if stat_name not in ['playerId', 'timestamp']:
                update_expression += f", {stat_name} = :val_{stat_name}"
                expression_values[f':val_{stat_name}'] = Decimal(str(stat_value)) if isinstance(stat_value, (int, float)) else stat_value
        
        # Update player stats
        response = player_stats_table.update_item(
            Key={'player_id': player_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        
        # Check for achievements and leaderboard updates
        check_achievements(player_id, response['Attributes'])
        update_leaderboard_positions(player_id, response['Attributes'])
        
        return create_success_response({
            'message': 'Player stats updated successfully',
            'updated_stats': response['Attributes']
        })
        
    except Exception as e:
        print(f"Error updating player stats: {str(e)}")
        return create_error_response(500, f'Failed to update player stats: {str(e)}')

def lambda_handler_leaderboard(event, context):
    """Lambda function for Unity leaderboard management"""
    
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        leaderboard_type = body.get('leaderboard_type', 'global')
        limit = min(body.get('limit', 100), 100)  # Limit to max 100 entries
        player_id = body.get('player_id')
        
        # Get leaderboard data
        leaderboard_data = get_leaderboard_data(leaderboard_type, limit)
        
        # Get player's rank if player_id provided
        player_rank = None
        if player_id:
            player_rank = get_player_rank(leaderboard_type, player_id)
        
        return create_success_response({
            'leaderboard': leaderboard_data,
            'player_rank': player_rank,
            'leaderboard_type': leaderboard_type,
            'total_entries': len(leaderboard_data)
        })
        
    except Exception as e:
        print(f"Error in leaderboard handler: {str(e)}")
        return create_error_response(500, 'Failed to retrieve leaderboard')

def get_leaderboard_data(leaderboard_type, limit):
    """Retrieve leaderboard data from DynamoDB"""
    
    try:
        response = leaderboard_table.query(
            IndexName='leaderboard-type-score-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('leaderboard_type').eq(leaderboard_type),
            ScanIndexForward=False,  # Sort descending by score
            Limit=limit
        )
        
        leaderboard_entries = []
        for rank, item in enumerate(response['Items'], 1):
            leaderboard_entries.append({
                'rank': rank,
                'player_id': item['player_id'],
                'player_name': item.get('player_name', 'Anonymous'),
                'score': int(item['score']),
                'last_updated': item.get('last_updated', '')
            })
        
        return leaderboard_entries
        
    except Exception as e:
        print(f"Error retrieving leaderboard: {str(e)}")
        return []

def lambda_handler_matchmaking(event, context):
    """Lambda function for Unity multiplayer matchmaking"""
    
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        player_id = body.get('playerId')
        game_mode = body.get('game_mode', 'standard')
        skill_level = body.get('skill_level', 1000)
        region = body.get('region', 'us-east-1')
        
        if not player_id:
            return create_error_response(400, 'Player ID is required')
        
        # Find match or create matchmaking request
        match_result = find_or_create_match(player_id, game_mode, skill_level, region)
        
        return create_success_response(match_result)
        
    except Exception as e:
        print(f"Error in matchmaking handler: {str(e)}")
        return create_error_response(500, 'Matchmaking failed')

def find_or_create_match(player_id, game_mode, skill_level, region):
    """Find existing match or create new matchmaking request"""
    
    matchmaking_table = dynamodb.Table('unity-matchmaking')
    
    try:
        # Look for existing matches in the skill range
        skill_range = 100  # +/- 100 skill points
        
        response = matchmaking_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('game_mode').eq(game_mode) &
                           boto3.dynamodb.conditions.Attr('region').eq(region) &
                           boto3.dynamodb.conditions.Attr('skill_level').between(
                               skill_level - skill_range, skill_level + skill_range) &
                           boto3.dynamodb.conditions.Attr('status').eq('waiting') &
                           boto3.dynamodb.conditions.Attr('player_id').ne(player_id)
        )
        
        if response['Items']:
            # Found a match!
            match_item = response['Items'][0]
            match_id = str(uuid.uuid4())
            
            # Update matchmaking status
            matchmaking_table.update_item(
                Key={'request_id': match_item['request_id']},
                UpdateExpression="SET #status = :matched, match_id = :match_id",
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':matched': 'matched',
                    ':match_id': match_id
                }
            )
            
            return {
                'status': 'match_found',
                'match_id': match_id,
                'opponent_id': match_item['player_id'],
                'game_mode': game_mode,
                'estimated_wait_time': 0
            }
        else:
            # Create new matchmaking request
            request_id = str(uuid.uuid4())
            
            matchmaking_table.put_item(
                Item={
                    'request_id': request_id,
                    'player_id': player_id,
                    'game_mode': game_mode,
                    'skill_level': skill_level,
                    'region': region,
                    'status': 'waiting',
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
            )
            
            return {
                'status': 'searching',
                'request_id': request_id,
                'estimated_wait_time': 30,  # seconds
                'game_mode': game_mode
            }
            
    except Exception as e:
        print(f"Error in matchmaking: {str(e)}")
        raise

def create_success_response(data):
    """Create standardized success response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data, default=decimal_default)
    }

def create_error_response(status_code, message):
    """Create standardized error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message})
    }

def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
```

### Unity Serverless Event System
```csharp
public class UnityServerlessEvents : MonoBehaviour
{
    [System.Serializable]
    public class GameEvent
    {
        public string eventType;
        public string playerId;
        public Dictionary<string, object> eventData;
        public float timestamp;
        public string sessionId;
    }
    
    private Queue<GameEvent> eventQueue;
    private UnityServerlessManager serverlessManager;
    
    private void Start()
    {
        eventQueue = new Queue<GameEvent>();
        serverlessManager = GetComponent<UnityServerlessManager>();
        
        StartCoroutine(ProcessEventQueue());
    }
    
    public void TrackGameEvent(string eventType, Dictionary<string, object> eventData)
    {
        var gameEvent = new GameEvent
        {
            eventType = eventType,
            playerId = GetPlayerId(),
            eventData = eventData,
            timestamp = Time.time,
            sessionId = GetSessionId()
        };
        
        eventQueue.Enqueue(gameEvent);
    }
    
    private IEnumerator ProcessEventQueue()
    {
        while (true)
        {
            if (eventQueue.Count > 0)
            {
                var batchEvents = new List<GameEvent>();
                
                // Process up to 10 events per batch
                for (int i = 0; i < 10 && eventQueue.Count > 0; i++)
                {
                    batchEvents.Add(eventQueue.Dequeue());
                }
                
                yield return StartCoroutine(SendEventBatch(batchEvents));
            }
            
            yield return new WaitForSeconds(1f); // Process every second
        }
    }
    
    private IEnumerator SendEventBatch(List<GameEvent> events)
    {
        var payload = new Dictionary<string, object>
        {
            {"events", events},
            {"batch_id", System.Guid.NewGuid().ToString()},
            {"batch_timestamp", System.DateTimeOffset.UtcNow.ToUnixTimeSeconds()}
        };
        
        yield return StartCoroutine(serverlessManager.InvokeLambdaFunction("game-events", payload, (response) =>
        {
            if (response.success)
            {
                Debug.Log($"Successfully sent batch of {events.Count} events");
            }
            else
            {
                Debug.LogError($"Failed to send event batch: {response.errorMessage}");
                // Re-queue events for retry
                foreach (var eventItem in events)
                {
                    eventQueue.Enqueue(eventItem);
                }
            }
        }));
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### AI-Powered Lambda Function Generation
```
# Prompt Template for Lambda Function Development
"Generate an AWS Lambda function for Unity game backend with the following requirements:

Function Purpose: [e.g., Player inventory management, Tournament system, Chat moderation]
Database: DynamoDB with the following tables: [table schema]
Input Parameters: [expected request format]
Output Format: [response structure]
Error Handling: [specific error scenarios to handle]
Performance Requirements: [response time, concurrent users]

Include:
1. Complete Python Lambda function code
2. DynamoDB integration with proper error handling
3. Input validation and sanitization
4. Proper HTTP response formatting
5. CloudWatch logging for debugging
6. Cost optimization considerations

Ensure the function is production-ready with proper security and error handling."
```

### Automated Performance Optimization
```python
def optimize_lambda_performance_with_ai():
    """AI-driven Lambda function performance optimization"""
    
    performance_data = collect_lambda_metrics()
    ai_recommendations = analyze_performance_with_ai(performance_data)
    
    apply_optimization_recommendations(ai_recommendations)
```

## 💡 Key Highlights
- **Cost-Effective Scaling**: Pay only for actual usage with automatic scaling from zero to thousands of concurrent players
- **Real-Time Game Services**: Handle player stats, leaderboards, matchmaking, and events with minimal latency
- **Developer Productivity**: Focus on game logic while AWS handles infrastructure management and scaling
- **Global Availability**: Leverage AWS global infrastructure for worldwide game deployment
- **Event-Driven Architecture**: Build responsive game systems that react to player actions instantly
- **Integrated Analytics**: Built-in integration with AWS analytics services for player behavior insights