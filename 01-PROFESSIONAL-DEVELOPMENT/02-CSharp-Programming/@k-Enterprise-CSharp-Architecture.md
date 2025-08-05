# @k-Enterprise-CSharp-Architecture

## 🎯 Learning Objectives
- Master enterprise-level C# architecture patterns and practices
- Understand Domain-Driven Design (DDD) implementation in Unity projects
- Implement Clean Architecture principles for scalable game development
- Build maintainable, testable, and extensible Unity systems

## 🔧 Core Enterprise Architecture Patterns

### Clean Architecture Implementation
```csharp
// Domain Layer - Core business logic
namespace GameDomain.Entities
{
    public class Player
    {
        public PlayerId Id { get; private set; }
        public string Name { get; private set; }
        public int Level { get; private set; }
        public Experience Experience { get; private set; }

        public Player(PlayerId id, string name)
        {
            Id = id ?? throw new ArgumentNullException(nameof(id));
            Name = name ?? throw new ArgumentNullException(nameof(name));
            Level = 1;
            Experience = new Experience(0);
        }

        public void GainExperience(int amount)
        {
            if (amount <= 0) throw new ArgumentException("Experience amount must be positive");
            
            Experience = Experience.Add(amount);
            CheckForLevelUp();
        }

        private void CheckForLevelUp()
        {
            int newLevel = CalculateLevel(Experience.Value);
            if (newLevel > Level)
            {
                Level = newLevel;
                // Domain event could be raised here
            }
        }

        private int CalculateLevel(int totalExperience)
        {
            return (int)Math.Floor(Math.Sqrt(totalExperience / 100.0)) + 1;
        }
    }
}

// Application Layer - Use cases and business workflows
namespace GameApplication.UseCases
{
    public interface IPlayerProgressionUseCase
    {
        Task<PlayerProgressionResult> AdvancePlayerAsync(PlayerId playerId, int experienceGained);
    }

    public class PlayerProgressionUseCase : IPlayerProgressionUseCase
    {
        private readonly IPlayerRepository _playerRepository;
        private readonly IEventPublisher _eventPublisher;

        public PlayerProgressionUseCase(IPlayerRepository playerRepository, IEventPublisher eventPublisher)
        {
            _playerRepository = playerRepository;
            _eventPublisher = eventPublisher;
        }

        public async Task<PlayerProgressionResult> AdvancePlayerAsync(PlayerId playerId, int experienceGained)
        {
            var player = await _playerRepository.GetByIdAsync(playerId);
            if (player == null)
                return PlayerProgressionResult.Failure("Player not found");

            int previousLevel = player.Level;
            player.GainExperience(experienceGained);

            await _playerRepository.SaveAsync(player);

            if (player.Level > previousLevel)
            {
                await _eventPublisher.PublishAsync(new PlayerLeveledUpEvent(playerId, player.Level));
            }

            return PlayerProgressionResult.Success(player);
        }
    }
}
```

### Repository Pattern with Unity Integration
```csharp
// Infrastructure Layer - Data access
namespace GameInfrastructure.Repositories
{
    public interface IPlayerRepository
    {
        Task<Player> GetByIdAsync(PlayerId id);
        Task SaveAsync(Player player);
        Task<IEnumerable<Player>> GetTopPlayersAsync(int count);
    }

    public class UnityPlayerRepository : IPlayerRepository
    {
        private readonly IDataSerializer _serializer;
        private readonly string _saveDirectory;

        public UnityPlayerRepository(IDataSerializer serializer)
        {
            _serializer = serializer;
            _saveDirectory = Path.Combine(Application.persistentDataPath, "Players");
            Directory.CreateDirectory(_saveDirectory);
        }

        public async Task<Player> GetByIdAsync(PlayerId id)
        {
            string filePath = Path.Combine(_saveDirectory, $"{id.Value}.json");
            
            if (!File.Exists(filePath))
                return null;

            string json = await File.ReadAllTextAsync(filePath);
            var playerData = _serializer.Deserialize<PlayerData>(json);
            return PlayerMapper.ToDomain(playerData);
        }

        public async Task SaveAsync(Player player)
        {
            var playerData = PlayerMapper.ToData(player);
            string json = _serializer.Serialize(playerData);
            string filePath = Path.Combine(_saveDirectory, $"{player.Id.Value}.json");
            await File.WriteAllTextAsync(filePath, json);
        }

        public async Task<IEnumerable<Player>> GetTopPlayersAsync(int count)
        {
            var files = Directory.GetFiles(_saveDirectory, "*.json");
            var players = new List<Player>();

            foreach (var file in files)
            {
                string json = await File.ReadAllTextAsync(file);
                var playerData = _serializer.Deserialize<PlayerData>(json);
                players.Add(PlayerMapper.ToDomain(playerData));
            }

            return players.OrderByDescending(p => p.Level)
                         .ThenByDescending(p => p.Experience.Value)
                         .Take(count);
        }
    }
}
```

## 🚀 Domain-Driven Design in Unity

### Value Objects Implementation
```csharp
namespace GameDomain.ValueObjects
{
    public class Experience : IEquatable<Experience>
    {
        public int Value { get; }

        public Experience(int value)
        {
            if (value < 0)
                throw new ArgumentException("Experience cannot be negative", nameof(value));
            
            Value = value;
        }

        public Experience Add(int amount)
        {
            return new Experience(Value + amount);
        }

        public bool Equals(Experience other)
        {
            return other != null && Value == other.Value;
        }

        public override bool Equals(object obj)
        {
            return obj is Experience other && Equals(other);
        }

        public override int GetHashCode()
        {
            return Value.GetHashCode();
        }

        public static bool operator ==(Experience left, Experience right)
        {
            return Equals(left, right);
        }

        public static bool operator !=(Experience left, Experience right)
        {
            return !Equals(left, right);
        }
    }

    public class PlayerId : IEquatable<PlayerId>
    {
        public Guid Value { get; }

        public PlayerId(Guid value)
        {
            if (value == Guid.Empty)
                throw new ArgumentException("PlayerId cannot be empty", nameof(value));
            
            Value = value;
        }

        public static PlayerId NewId() => new PlayerId(Guid.NewGuid());

        public bool Equals(PlayerId other)
        {
            return other != null && Value.Equals(other.Value);
        }

        public override bool Equals(object obj)
        {
            return obj is PlayerId other && Equals(other);
        }

        public override int GetHashCode()
        {
            return Value.GetHashCode();
        }

        public override string ToString()
        {
            return Value.ToString();
        }
    }
}
```

### Domain Events System
```csharp
namespace GameDomain.Events
{
    public interface IDomainEvent
    {
        Guid Id { get; }
        DateTime OccurredOn { get; }
    }

    public class PlayerLeveledUpEvent : IDomainEvent
    {
        public Guid Id { get; }
        public DateTime OccurredOn { get; }
        public PlayerId PlayerId { get; }
        public int NewLevel { get; }

        public PlayerLeveledUpEvent(PlayerId playerId, int newLevel)
        {
            Id = Guid.NewGuid();
            OccurredOn = DateTime.UtcNow;
            PlayerId = playerId;
            NewLevel = newLevel;
        }
    }

    public interface IEventPublisher
    {
        Task PublishAsync<T>(T domainEvent) where T : IDomainEvent;
    }

    public class UnityEventPublisher : IEventPublisher
    {
        private readonly Dictionary<Type, List<Func<IDomainEvent, Task>>> _handlers
            = new Dictionary<Type, List<Func<IDomainEvent, Task>>>();

        public void Subscribe<T>(Func<T, Task> handler) where T : IDomainEvent
        {
            var eventType = typeof(T);
            if (!_handlers.ContainsKey(eventType))
                _handlers[eventType] = new List<Func<IDomainEvent, Task>>();

            _handlers[eventType].Add(evt => handler((T)evt));
        }

        public async Task PublishAsync<T>(T domainEvent) where T : IDomainEvent
        {
            var eventType = typeof(T);
            if (_handlers.TryGetValue(eventType, out var handlers))
            {
                var tasks = handlers.Select(handler => handler(domainEvent));
                await Task.WhenAll(tasks);
            }
        }
    }
}
```

## 🔧 Dependency Injection Container

### Unity Service Locator Pattern
```csharp
namespace GameInfrastructure.DI
{
    public interface IServiceContainer
    {
        void RegisterSingleton<TInterface, TImplementation>()
            where TImplementation : class, TInterface;
        void RegisterTransient<TInterface, TImplementation>()
            where TImplementation : class, TInterface;
        void RegisterInstance<T>(T instance);
        T Resolve<T>();
        object Resolve(Type type);
    }

    public class UnityServiceContainer : IServiceContainer, IDisposable
    {
        private readonly Dictionary<Type, ServiceDescriptor> _services
            = new Dictionary<Type, ServiceDescriptor>();
        private readonly Dictionary<Type, object> _singletonInstances
            = new Dictionary<Type, object>();

        public void RegisterSingleton<TInterface, TImplementation>()
            where TImplementation : class, TInterface
        {
            _services[typeof(TInterface)] = new ServiceDescriptor
            {
                ServiceType = typeof(TInterface),
                ImplementationType = typeof(TImplementation),
                Lifetime = ServiceLifetime.Singleton
            };
        }

        public void RegisterTransient<TInterface, TImplementation>()
            where TImplementation : class, TInterface
        {
            _services[typeof(TInterface)] = new ServiceDescriptor
            {
                ServiceType = typeof(TInterface),
                ImplementationType = typeof(TImplementation),
                Lifetime = ServiceLifetime.Transient
            };
        }

        public void RegisterInstance<T>(T instance)
        {
            _singletonInstances[typeof(T)] = instance;
        }

        public T Resolve<T>()
        {
            return (T)Resolve(typeof(T));
        }

        public object Resolve(Type type)
        {
            if (_singletonInstances.TryGetValue(type, out var instance))
                return instance;

            if (!_services.TryGetValue(type, out var serviceDescriptor))
                throw new InvalidOperationException($"Service of type {type.Name} is not registered");

            if (serviceDescriptor.Lifetime == ServiceLifetime.Singleton)
            {
                if (!_singletonInstances.TryGetValue(type, out instance))
                {
                    instance = CreateInstance(serviceDescriptor.ImplementationType);
                    _singletonInstances[type] = instance;
                }
                return instance;
            }

            return CreateInstance(serviceDescriptor.ImplementationType);
        }

        private object CreateInstance(Type type)
        {
            var constructors = type.GetConstructors();
            var constructor = constructors.OrderByDescending(c => c.GetParameters().Length).First();
            
            var parameters = constructor.GetParameters();
            var args = new object[parameters.Length];

            for (int i = 0; i < parameters.Length; i++)
            {
                args[i] = Resolve(parameters[i].ParameterType);
            }

            return Activator.CreateInstance(type, args);
        }

        public void Dispose()
        {
            foreach (var instance in _singletonInstances.Values)
            {
                if (instance is IDisposable disposable)
                    disposable.Dispose();
            }
            _singletonInstances.Clear();
        }

        private class ServiceDescriptor
        {
            public Type ServiceType { get; set; }
            public Type ImplementationType { get; set; }
            public ServiceLifetime Lifetime { get; set; }
        }

        private enum ServiceLifetime
        {
            Singleton,
            Transient
        }
    }
}
```

## 🚀 Command Pattern for Game Actions

### Command System Implementation
```csharp
namespace GameApplication.Commands
{
    public interface ICommand
    {
        Task ExecuteAsync();
        Task UndoAsync();
        string Description { get; }
    }

    public class MovePlayerCommand : ICommand
    {
        private readonly PlayerId _playerId;
        private readonly Vector3 _fromPosition;
        private readonly Vector3 _toPosition;
        private readonly IPlayerRepository _playerRepository;

        public string Description => $"Move player {_playerId} from {_fromPosition} to {_toPosition}";

        public MovePlayerCommand(PlayerId playerId, Vector3 fromPosition, Vector3 toPosition, 
                               IPlayerRepository playerRepository)
        {
            _playerId = playerId;
            _fromPosition = fromPosition;
            _toPosition = toPosition;
            _playerRepository = playerRepository;
        }

        public async Task ExecuteAsync()
        {
            var player = await _playerRepository.GetByIdAsync(_playerId);
            if (player != null)
            {
                // Apply movement logic
                await _playerRepository.SaveAsync(player);
            }
        }

        public async Task UndoAsync()
        {
            var player = await _playerRepository.GetByIdAsync(_playerId);
            if (player != null)
            {
                // Revert movement
                await _playerRepository.SaveAsync(player);
            }
        }
    }

    public class CommandInvoker
    {
        private readonly Stack<ICommand> _executedCommands = new Stack<ICommand>();
        private readonly Stack<ICommand> _undoneCommands = new Stack<ICommand>();

        public async Task ExecuteAsync(ICommand command)
        {
            await command.ExecuteAsync();
            _executedCommands.Push(command);
            _undoneCommands.Clear(); // Clear redo stack
        }

        public async Task UndoAsync()
        {
            if (_executedCommands.Count > 0)
            {
                var command = _executedCommands.Pop();
                await command.UndoAsync();
                _undoneCommands.Push(command);
            }
        }

        public async Task RedoAsync()
        {
            if (_undoneCommands.Count > 0)
            {
                var command = _undoneCommands.Pop();
                await command.ExecuteAsync();
                _executedCommands.Push(command);
            }
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Architecture Pattern Generation
```prompt
Generate enterprise C# architecture for Unity game [GAME_TYPE] including:
- Clean Architecture layer separation
- Domain-driven design entities and value objects
- Repository pattern with Unity-specific implementations
- Command/Query pattern for game actions
- Dependency injection setup
- Event-driven architecture for game systems
```

### Code Quality Automation
```prompt
Create comprehensive C# code quality rules for Unity enterprise project:
- Static analysis configuration (SonarQube/Roslyn)
- Automated testing strategies (unit/integration/performance)
- Code review checklist for architecture compliance
- Refactoring guidelines for legacy code
- Performance monitoring and profiling setup
```

## 💡 Key Enterprise Architecture Principles

### 1. Separation of Concerns
- Clear layer boundaries with defined responsibilities
- Domain logic isolated from infrastructure concerns
- UI separated from business logic
- Cross-cutting concerns handled via aspects or decorators

### 2. Dependency Management
- Dependency inversion principle implementation
- Interface-based design for testability
- Composition over inheritance
- Explicit dependency declarations

### 3. Error Handling Strategy
- Centralized exception handling
- Domain-specific exceptions
- Graceful degradation patterns
- Comprehensive logging and monitoring

### 4. Testing Strategy
- Unit tests for domain logic
- Integration tests for infrastructure
- Contract tests for interfaces
- Performance tests for critical paths

This comprehensive guide provides the foundation for building enterprise-level Unity applications with maintainable, scalable, and testable C# architecture.