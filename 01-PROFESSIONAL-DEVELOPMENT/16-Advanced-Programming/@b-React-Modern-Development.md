# @b-React Modern Development - Components, Hooks, and Unity Integration

## 🎯 Learning Objectives
- Master React functional components and modern hooks
- Implement state management for Unity WebGL integration
- Build responsive UI components for game portfolios
- Create AI-automated React development workflows
- Develop Unity-specific React components and tools

## ⚛️ Modern React Fundamentals

### Functional Components with Hooks
```jsx
import React, { useState, useEffect, useCallback, useMemo } from 'react';

// Unity Game Portfolio Component
const UnityGameShowcase = ({ gameData, onGameLoad }) => {
    const [loadingState, setLoadingState] = useState('idle');
    const [unityInstance, setUnityInstance] = useState(null);
    const [gameMetrics, setGameMetrics] = useState({
        fps: 0,
        loadTime: 0,
        memoryUsage: 0
    });

    // Memoized game configuration
    const gameConfig = useMemo(() => ({
        dataUrl: `${gameData.buildPath}/${gameData.id}.data`,
        frameworkUrl: `${gameData.buildPath}/${gameData.id}.framework.js`,
        codeUrl: `${gameData.buildPath}/${gameData.id}.wasm`,
        streamingAssetsUrl: "StreamingAssets",
        companyName: "YourCompany",
        productName: gameData.title,
        productVersion: gameData.version || "1.0"
    }), [gameData]);

    // Load Unity game with error handling
    const loadUnityGame = useCallback(async () => {
        if (loadingState !== 'idle') return;
        
        setLoadingState('loading');
        const startTime = performance.now();

        try {
            const canvas = document.querySelector(`#unity-canvas-${gameData.id}`);
            if (!canvas) throw new Error('Canvas element not found');

            // Load Unity build
            const script = document.createElement('script');
            script.src = `${gameData.buildPath}/${gameData.id}.loader.js`;
            
            await new Promise((resolve, reject) => {
                script.onload = resolve;
                script.onerror = () => reject(new Error('Failed to load Unity loader'));
                document.head.appendChild(script);
            });

            const instance = await createUnityInstance(canvas, gameConfig, {
                onProgress: (progress) => {
                    setLoadingState(`loading-${Math.round(progress * 100)}`);
                }
            });

            const loadTime = performance.now() - startTime;
            setUnityInstance(instance);
            setGameMetrics(prev => ({ ...prev, loadTime }));
            setLoadingState('loaded');
            onGameLoad?.(instance, loadTime);

        } catch (error) {
            console.error('Unity game loading failed:', error);
            setLoadingState('error');
        }
    }, [gameData, gameConfig, loadingState, onGameLoad]);

    // Performance monitoring
    useEffect(() => {
        if (!unityInstance) return;

        const monitorPerformance = () => {
            // Monitor FPS (if Unity provides this data)
            if (unityInstance.Module && unityInstance.Module.fps) {
                setGameMetrics(prev => ({
                    ...prev,
                    fps: unityInstance.Module.fps
                }));
            }

            // Monitor memory usage
            if (performance.memory) {
                setGameMetrics(prev => ({
                    ...prev,
                    memoryUsage: performance.memory.usedJSHeapSize / 1048576 // MB
                }));
            }
        };

        const interval = setInterval(monitorPerformance, 1000);
        return () => clearInterval(interval);
    }, [unityInstance]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (unityInstance) {
                unityInstance.Quit?.();
            }
        };
    }, [unityInstance]);

    const getLoadingProgress = () => {
        if (loadingState.startsWith('loading-')) {
            return parseInt(loadingState.split('-')[1]) || 0;
        }
        return loadingState === 'loaded' ? 100 : 0;
    };

    return (
        <div className="unity-game-showcase">
            <div className="game-header">
                <h3>{gameData.title}</h3>
                <div className="tech-stack">
                    {gameData.technologies?.map(tech => (
                        <span key={tech} className="tech-tag">{tech}</span>
                    ))}
                </div>
            </div>

            <div className="game-container">
                {loadingState === 'idle' && (
                    <div className="game-preview" onClick={loadUnityGame}>
                        <img 
                            src={gameData.thumbnail} 
                            alt={`${gameData.title} preview`}
                            className="preview-image"
                        />
                        <div className="play-overlay">
                            <button className="play-button">
                                ▶ Launch Game
                            </button>
                        </div>
                    </div>
                )}

                {loadingState.startsWith('loading') && (
                    <div className="loading-container">
                        <div className="loading-bar">
                            <div 
                                className="loading-progress"
                                style={{ width: `${getLoadingProgress()}%` }}
                            />
                        </div>
                        <p>Loading... {getLoadingProgress()}%</p>
                    </div>
                )}

                {loadingState === 'loaded' && (
                    <div className="game-canvas-container">
                        <canvas 
                            id={`unity-canvas-${gameData.id}`}
                            className="unity-canvas"
                        />
                        <GameMetrics metrics={gameMetrics} />
                    </div>
                )}

                {loadingState === 'error' && (
                    <div className="error-container">
                        <p>Failed to load game. Please try again.</p>
                        <button onClick={() => setLoadingState('idle')}>
                            Retry
                        </button>
                    </div>
                )}
            </div>

            <div className="game-description">
                <p>{gameData.description}</p>
                {gameData.githubUrl && (
                    <a 
                        href={gameData.githubUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="source-link"
                    >
                        View Source Code
                    </a>
                )}
            </div>
        </div>
    );
};

// Performance metrics display component
const GameMetrics = ({ metrics }) => {
    const [showMetrics, setShowMetrics] = useState(false);

    return (
        <div className="game-metrics">
            <button 
                className="metrics-toggle"
                onClick={() => setShowMetrics(!showMetrics)}
            >
                📊 Performance
            </button>
            
            {showMetrics && (
                <div className="metrics-panel">
                    <div className="metric">
                        <span>Load Time:</span>
                        <span>{(metrics.loadTime / 1000).toFixed(2)}s</span>
                    </div>
                    <div className="metric">
                        <span>FPS:</span>
                        <span>{metrics.fps}</span>
                    </div>
                    <div className="metric">
                        <span>Memory:</span>
                        <span>{metrics.memoryUsage.toFixed(1)}MB</span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UnityGameShowcase;
```

### Custom Hooks for Unity Integration
```jsx
import { useState, useEffect, useCallback, useRef } from 'react';

// Custom hook for Unity WebGL management
export const useUnityWebGL = (gameConfig) => {
    const [instance, setInstance] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [metrics, setMetrics] = useState({
        loadTime: 0,
        fps: 0,
        memoryUsage: 0
    });
    
    const canvasRef = useRef(null);
    const metricsIntervalRef = useRef(null);

    const loadGame = useCallback(async () => {
        if (isLoading || instance) return;
        
        setIsLoading(true);
        setError(null);
        const startTime = performance.now();

        try {
            // Ensure canvas is available
            if (!canvasRef.current) {
                throw new Error('Canvas ref not available');
            }

            // Load Unity loader script
            const loaderScript = document.createElement('script');
            loaderScript.src = gameConfig.loaderUrl;
            
            await new Promise((resolve, reject) => {
                loaderScript.onload = resolve;
                loaderScript.onerror = () => reject(new Error('Failed to load Unity loader'));
                document.head.appendChild(loaderScript);
            });

            // Create Unity instance
            const unityInstance = await window.createUnityInstance(
                canvasRef.current,
                gameConfig,
                {
                    onProgress: (progress) => {
                        // Progress callback can be used to update loading state
                        setMetrics(prev => ({ ...prev, loadProgress: progress }));
                    }
                }
            );

            const loadTime = performance.now() - startTime;
            setInstance(unityInstance);
            setMetrics(prev => ({ ...prev, loadTime }));
            
            // Start performance monitoring
            startPerformanceMonitoring(unityInstance);

        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    }, [gameConfig, isLoading, instance]);

    const startPerformanceMonitoring = useCallback((unityInstance) => {
        metricsIntervalRef.current = setInterval(() => {
            setMetrics(prev => ({
                ...prev,
                fps: unityInstance.Module?.fps || 0,
                memoryUsage: performance.memory 
                    ? performance.memory.usedJSHeapSize / 1048576 
                    : 0
            }));
        }, 1000);
    }, []);

    const unload = useCallback(() => {
        if (instance) {
            instance.Quit?.();
            setInstance(null);
        }
        if (metricsIntervalRef.current) {
            clearInterval(metricsIntervalRef.current);
        }
    }, [instance]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            unload();
        };
    }, [unload]);

    return {
        instance,
        isLoading,
        error,
        metrics,
        loadGame,
        unload,
        canvasRef
    };
};

// Custom hook for game portfolio management
export const useGamePortfolio = () => {
    const [games, setGames] = useState([]);
    const [filter, setFilter] = useState('all');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Load games data
    useEffect(() => {
        const loadGames = async () => {
            try {
                setLoading(true);
                // This could be from API, local JSON, or static import
                const response = await fetch('/api/games.json');
                if (!response.ok) throw new Error('Failed to load games');
                
                const gamesData = await response.json();
                setGames(gamesData);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        loadGames();
    }, []);

    // Filter games based on current filter
    const filteredGames = useMemo(() => {
        if (filter === 'all') return games;
        return games.filter(game => game.category === filter);
    }, [games, filter]);

    // Get unique categories for filter options
    const categories = useMemo(() => {
        const cats = [...new Set(games.map(game => game.category))];
        return ['all', ...cats];
    }, [games]);

    return {
        games: filteredGames,
        allGames: games,
        categories,
        filter,
        setFilter,
        loading,
        error
    };
};
```

### Context API for Global State Management
```jsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Portfolio theme and settings context
const PortfolioContext = createContext();

// State reducer
const portfolioReducer = (state, action) => {
    switch (action.type) {
        case 'SET_THEME':
            return { ...state, theme: action.payload };
        
        case 'SET_VIEW_MODE':
            return { ...state, viewMode: action.payload };
        
        case 'ADD_GAME_METRICS':
            return {
                ...state,
                gameMetrics: {
                    ...state.gameMetrics,
                    [action.gameId]: action.payload
                }
            };
        
        case 'SET_PERFORMANCE_MODE':
            return { ...state, performanceMode: action.payload };
        
        case 'UPDATE_SETTINGS':
            return { ...state, settings: { ...state.settings, ...action.payload } };
        
        default:
            return state;
    }
};

// Initial state
const initialState = {
    theme: 'dark',
    viewMode: 'grid',
    performanceMode: 'balanced',
    gameMetrics: {},
    settings: {
        autoLoadGames: false,
        showPerformanceMetrics: true,
        enableAnimations: true,
        preferredQuality: 'high'
    }
};

// Context provider component
export const PortfolioProvider = ({ children }) => {
    const [state, dispatch] = useReducer(portfolioReducer, initialState);

    // Persist settings to localStorage
    useEffect(() => {
        const savedSettings = localStorage.getItem('portfolioSettings');
        if (savedSettings) {
            try {
                const settings = JSON.parse(savedSettings);
                dispatch({ type: 'UPDATE_SETTINGS', payload: settings });
            } catch (error) {
                console.error('Failed to load saved settings:', error);
            }
        }
    }, []);

    // Save settings when they change
    useEffect(() => {
        localStorage.setItem('portfolioSettings', JSON.stringify(state.settings));
    }, [state.settings]);

    // Action creators
    const actions = {
        setTheme: (theme) => dispatch({ type: 'SET_THEME', payload: theme }),
        setViewMode: (mode) => dispatch({ type: 'SET_VIEW_MODE', payload: mode }),
        addGameMetrics: (gameId, metrics) => 
            dispatch({ type: 'ADD_GAME_METRICS', gameId, payload: metrics }),
        setPerformanceMode: (mode) => 
            dispatch({ type: 'SET_PERFORMANCE_MODE', payload: mode }),
        updateSettings: (settings) => 
            dispatch({ type: 'UPDATE_SETTINGS', payload: settings })
    };

    return (
        <PortfolioContext.Provider value={{ state, actions }}>
            {children}
        </PortfolioContext.Provider>
    );
};

// Custom hook to use portfolio context
export const usePortfolio = () => {
    const context = useContext(PortfolioContext);
    if (!context) {
        throw new Error('usePortfolio must be used within PortfolioProvider');
    }
    return context;
};
```

## 🚀 AI/LLM Integration for React Development

### AI-Powered Component Generation
```javascript
// AI prompt templates for React component generation
const reactPrompts = {
    generateComponent: (componentName, requirements) => `
Generate a modern React functional component for ${componentName} with these requirements:
${requirements.join('\n- ')}

Technical specifications:
- Use modern React hooks (useState, useEffect, useCallback, useMemo)
- Implement eye-friendly dark mode styling with CSS-in-JS or styled-components
- Include proper TypeScript types and interfaces
- Add comprehensive error handling and loading states
- Follow React best practices and performance optimization
- Include accessibility attributes (ARIA labels, keyboard navigation)
- Add responsive design for mobile/tablet/desktop
- Implement proper cleanup in useEffect hooks

Color scheme (from COLOR-SCHEME.md):
- Background: #1e1e1e (primary), #2d2d2d (secondary)
- Text: #e8e8e8 (primary), #c0c0c0 (secondary)
- Accents: #4a9eff (blue), #5cb85c (green)
- Borders: #404040 (default)

Return complete component code with imports and exports.
`,

    optimizeComponent: (componentCode) => `
Optimize this React component for better performance and maintainability:

\`\`\`jsx
${componentCode}
\`\`\`

Focus on:
1. Memoization opportunities (React.memo, useMemo, useCallback)
2. Prevent unnecessary re-renders
3. Optimize expensive computations
4. Improve bundle size (dynamic imports, code splitting)
5. Better error boundaries and error handling
6. Accessibility improvements
7. TypeScript type safety
8. Modern React patterns and hooks

Provide the optimized code with explanations for each optimization.
`,

    generateUnityIntegration: (gameSpecs) => `
Create a React component that integrates Unity WebGL build with these specifications:
${JSON.stringify(gameSpecs, null, 2)}

Requirements:
- Handle Unity WebGL loading and initialization
- Implement loading progress with visual feedback
- Add performance monitoring (FPS, memory usage, load time)
- Include error handling and retry mechanisms
- Support responsive canvas sizing
- Add game controls overlay (fullscreen, settings, etc.)
- Implement proper cleanup on component unmount
- Include TypeScript types for Unity instance

Additional features:
- Screenshot capture functionality
- Game state persistence
- Performance analytics tracking
- Social sharing integration
`
};

// Automated component generation workflow
class ReactComponentGenerator {
    constructor(aiService) {
        this.aiService = aiService;
    }

    async generateComponent(spec) {
        const prompt = reactPrompts.generateComponent(spec.name, spec.requirements);
        
        try {
            const generatedCode = await this.aiService.generateCode(prompt);
            
            // Validate generated code
            const validation = await this.validateComponent(generatedCode);
            
            if (validation.isValid) {
                return {
                    code: generatedCode,
                    fileName: `${spec.name}.jsx`,
                    tests: await this.generateTests(generatedCode),
                    storybook: await this.generateStorybook(generatedCode)
                };
            } else {
                throw new Error(`Generated component validation failed: ${validation.errors}`);
            }
        } catch (error) {
            console.error('Component generation failed:', error);
            throw error;
        }
    }

    async validateComponent(code) {
        // Basic validation checks
        const validations = [
            { check: code.includes('import React'), error: 'Missing React import' },
            { check: code.includes('export default'), error: 'Missing default export' },
            { check: !code.includes('class '), error: 'Should use functional components' },
            { check: code.includes('useState') || code.includes('useEffect'), error: 'Should use hooks' }
        ];

        const errors = validations
            .filter(v => !v.check)
            .map(v => v.error);

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    async generateTests(componentCode) {
        const testPrompt = `
Generate comprehensive Jest/React Testing Library tests for this component:

\`\`\`jsx
${componentCode}
\`\`\`

Include tests for:
- Component rendering
- User interactions
- Error states
- Loading states
- Accessibility
- Unity WebGL integration (if applicable)
- Performance considerations
`;
        
        return await this.aiService.generateCode(testPrompt);
    }

    async generateStorybook(componentCode) {
        const storybookPrompt = `
Generate Storybook stories for this React component:

\`\`\`jsx
${componentCode}
\`\`\`

Include stories for:
- Default state
- Loading state
- Error state
- Different prop variations
- Interactive examples
- Unity game integration examples (if applicable)
`;
        
        return await this.aiService.generateCode(storybookPrompt);
    }
}
```

## 💡 Key Highlights

### React Skills for Unity Developers
- **Component Architecture**: Modular, reusable UI components for game portfolios
- **State Management**: Complex game state handling with Context API and custom hooks
- **Performance Optimization**: Memoization and optimization techniques for smooth UX
- **WebGL Integration**: Seamless Unity WebGL embedding and interaction

### Modern React Patterns
- **Functional Components**: Leverage hooks for cleaner, more maintainable code
- **Custom Hooks**: Extract and reuse Unity-specific logic across components
- **Context API**: Global state management for portfolio settings and game data
- **Error Boundaries**: Robust error handling for Unity WebGL failures

### Unity-Specific Benefits
- **Professional Portfolios**: Showcase Unity games with interactive web interfaces
- **Performance Monitoring**: Real-time metrics for Unity WebGL builds
- **Asset Management**: React-based tools for Unity asset organization
- **Developer Tools**: Custom Unity editor extensions with React frontends

### AI Automation Opportunities
- **Component Generation**: AI-powered React component creation
- **Code Optimization**: Automated performance improvements
- **Test Generation**: Comprehensive test suite creation
- **Documentation**: Auto-generated component documentation and Storybook stories

## 🎯 Next Steps for Unity Integration
1. **Build Game Portfolio**: Create React-based Unity game showcase
2. **Develop Unity Tools**: React components for Unity development workflows  
3. **Implement Analytics**: Performance tracking for Unity WebGL games
4. **Create Asset Browser**: React interface for Unity asset management
5. **Automate Development**: AI-powered React component generation workflows