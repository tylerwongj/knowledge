# @b-Probability Mathematics - Statistical Analysis for Optimal Yahtzee Play

## 🎯 Learning Objectives
- Master probability calculations for all Yahtzee scenarios
- Understand combinatorics and expected value in dice games
- Apply statistical analysis to improve decision-making
- Build intuition for complex probability situations

## 🎲 Fundamental Dice Probabilities

### Single Die Probabilities
- **Any specific number**: 1/6 ≈ 16.67%
- **Not a specific number**: 5/6 ≈ 83.33%
- **Any of two numbers**: 2/6 ≈ 33.33%
- **Any of three numbers**: 3/6 = 50%

### Five Dice Probabilities (Initial Roll)
- **Yahtzee (all same)**: (1/6)^4 × 6 = 6/1296 ≈ 0.46%
- **Four of a Kind**: C(5,4) × 6 × 5 × (1/6)^4 ≈ 1.93%
- **Full House**: C(5,3) × C(2,2) × 6 × 5 × (1/6)^5 ≈ 3.86%
- **Large Straight**: 240/7776 ≈ 3.09%
- **Small Straight**: 1980/7776 ≈ 25.46%

## 📊 Category-Specific Probability Analysis

### Yahtzee Probabilities by Game State

#### Starting with One Pair (after Roll 1)
```
Two rolls remaining:
- Keep the pair, reroll 3 dice
- P(Three of a Kind on Roll 2) = C(3,1) × (1/6) × (5/6)^2 ≈ 34.72%
- P(Yahtzee on Roll 3 | Three of a Kind on Roll 2) = (1/6)^2 ≈ 2.78%
- Total P(Yahtzee) ≈ 4.63%
```

#### Starting with Three of a Kind (after Roll 1)
```
Two rolls remaining:
- P(Four of a Kind on Roll 2) = C(2,1) × (1/6) ≈ 33.33%
- P(Yahtzee on Roll 3 | Four of a Kind on Roll 2) = 1/6 ≈ 16.67%
- P(Yahtzee directly on Roll 2) = (1/6)^2 ≈ 2.78%
- Total P(Yahtzee) ≈ 25.93%
```

### Straight Probabilities

#### Large Straight (1-2-3-4-5 or 2-3-4-5-6)
```
After Roll 1 with 4 consecutive:
- Missing one number from sequence
- P(completion in 2 rolls) = 1 - (5/6)^2 ≈ 30.56%

After Roll 1 with 3 consecutive + 2 extras:
- Need specific number and avoid duplicates
- P(completion in 2 rolls) ≈ 12.35%
```

#### Small Straight (any 4 consecutive)
```
After Roll 1 with 3 consecutive:
- Multiple ways to complete (adding to either end)
- P(completion in 2 rolls) ≈ 43.52%

After Roll 1 with 2 consecutive + extras:
- Need 2 specific numbers in sequence
- P(completion in 2 rolls) ≈ 15.28%
```

## 🧮 Expected Value Calculations

### Upper Section Expected Values
```
Ones (keeping all 1s):
- E[1 die] = 1/6 × 1 = 0.167
- E[5 dice] = 5 × 0.167 = 0.833

Sixes (keeping all 6s):
- E[1 die] = 1/6 × 6 = 1.0
- E[5 dice] = 5 × 1.0 = 5.0
```

### Three/Four of a Kind Expected Values
```
With three 6s, rerolling 2 dice:
- Base score: 18 points
- Expected additional: 2 × 3.5 = 7 points
- Total expected: 25 points

With four 6s, rerolling 1 die:
- Base score: 24 points
- Expected additional: 1 × 3.5 = 3.5 points
- Total expected: 27.5 points
```

## 🎯 Decision Tree Analysis

### Roll 1 Decision Framework
```
Given dice: [d1, d2, d3, d4, d5]

1. Calculate E[Yahtzee] for each possible keep pattern
2. Calculate E[Four of a Kind] for high-value dice
3. Calculate E[Straight] for sequential patterns
4. Calculate E[Upper Section] for each number
5. Compare all expected values
6. Choose maximum expected value strategy
```

### Mathematical Decision Model
```python
def optimal_keep_decision(dice, empty_categories):
    strategies = []
    
    for keep_pattern in all_possible_keeps(dice):
        for category in empty_categories:
            ev = calculate_expected_value(keep_pattern, category)
            strategies.append((keep_pattern, category, ev))
    
    return max(strategies, key=lambda x: x[2])
```

## 📈 Advanced Probability Concepts

### Conditional Probability Chains
```
P(Yahtzee | current state) = 
P(Yahtzee on Roll 2 | current) + 
P(Yahtzee on Roll 3 | miss on Roll 2) × P(miss on Roll 2)
```

### Markov Chain Analysis
- Each roll represents a state transition
- Probability of reaching target state from current state
- Optimal policy for each state based on expected rewards

### Risk-Adjusted Expected Value
```
Adjusted EV = Standard EV × Risk Factor

Risk Factor considerations:
- Turn number (early game = higher risk tolerance)
- Score differential (behind = higher risk tolerance)
- Category availability (fewer options = lower risk tolerance)
```

## 🚀 AI/LLM Integration Opportunities

### Probability Calculator Prompts
```
"Calculate the exact probability of achieving Yahtzee given dice state: 
[2,2,2,4,6] with 2 rolls remaining. Show step-by-step calculation."
```

### Expected Value Analysis
```
"Compare expected values for keeping [2,2,2] vs [2,2,2,4] vs [2,2,2,6] 
for remaining categories: [Yahtzee, Four of a Kind, Three of a Kind, Chance]"
```

### Strategy Optimization
```
"Given game state [current score, empty categories, turn number], 
calculate optimal strategy using dynamic programming approach."
```

## 💡 Key Mathematical Insights

### Probability Hierarchies
1. **Small improvements have big impacts**: 25% → 30% win rate = 20% relative improvement
2. **Rare events compound**: Multiple low-probability plays create significant advantages
3. **Expected value beats intuition**: Mathematical optimal often feels wrong

### Common Probability Mistakes
- **Gambler's fallacy**: Previous rolls don't affect future probabilities
- **Hot hand fallacy**: Streaks are statistical noise, not skill
- **Sunk cost fallacy**: Previous rolls don't justify continuing bad strategies

### Combinatorial Shortcuts
```
C(n,k) = n! / (k!(n-k)!)

Common values:
C(5,1) = 5
C(5,2) = 10  
C(5,3) = 10
C(5,4) = 5
C(5,5) = 1
```

## 🔢 Practical Calculation Tools

### Quick Mental Math Approximations
- **1/6 ≈ 0.17** (exact: 0.1667)
- **(5/6)^2 ≈ 0.69** (exact: 0.6944)
- **(1/6)^2 ≈ 0.03** (exact: 0.0278)
- **Expected die value = 3.5**

### Probability Tables for Quick Reference
```
Dice Remaining | P(specific number)
1              | 16.67%
2              | 30.56%  
3              | 42.13%
4              | 51.77%
5              | 59.81%
```

## 📊 Statistical Validation Methods

### Monte Carlo Simulation
- Run thousands of game simulations
- Compare theoretical vs. observed probabilities
- Validate strategy effectiveness through statistical testing

### Regression Analysis  
- Correlate decision patterns with score outcomes
- Identify which probability calculations matter most
- Optimize strategy based on empirical results