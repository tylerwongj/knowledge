# Future Submodule Migration Plan

## Overview
This document outlines the plan to migrate from the current monorepo structure to a master repository with topic-specific submodules, each having their own focused goals and Claude Code instructions.

## Current Structure
```
knowledge/ (monorepo)
├── 01-Unity-Engine/
├── 02-CSharp-Programming/
├── 03-Soft-Skills/
├── 04-Career-Job-Search/
├── 05-Work-Types-Specializations/
├── 06-Game-Development-Math/
├── 07-Tools-Version-Control/
├── 08-AI-LLM-Automation/
├── 09-Freelancing-Remote-Work/
├── 10-Web-Development-Automation/
├── 11-Data-Processing-Analytics/
├── 12-Customer-Service-Automation/
├── 13-Content-Creation-Marketing/
├── 14-Business-Process-Automation/
├── 15-Entrepreneurship-AI-Business/
├── CLAUDE.md (general)
└── PLAN.md (general)
```

## Target Structure
```
knowledge-master/                    # Orchestration repo
├── unity-knowledge/                 # Submodule
│   ├── 01-Unity-Engine/
│   ├── 02-CSharp-Programming/
│   ├── 06-Game-Development-Math/
│   ├── 07-Tools-Version-Control/
│   ├── CLAUDE.md                   # Unity job focus
│   └── PLAN.md                     # Unity career goals
├── ai-automation-knowledge/         # Submodule
│   ├── 08-AI-LLM-Automation/
│   ├── 10-Web-Development-Automation/
│   ├── 11-Data-Processing-Analytics/
│   ├── 12-Customer-Service-Automation/
│   ├── 14-Business-Process-Automation/
│   ├── CLAUDE.md                   # Stealth productivity focus
│   └── PLAN.md                     # AI automation goals
├── career-skills-knowledge/         # Submodule
│   ├── 03-Soft-Skills/
│   ├── 04-Career-Job-Search/
│   ├── 05-Work-Types-Specializations/
│   ├── 09-Freelancing-Remote-Work/
│   ├── 13-Content-Creation-Marketing/
│   ├── 15-Entrepreneurship-AI-Business/
│   ├── CLAUDE.md                   # Professional development focus
│   └── PLAN.md                     # Career advancement goals
├── bible-knowledge/                 # Future submodule
│   ├── CLAUDE.md                   # Theological study focus
│   └── PLAN.md                     # Bible study goals
├── board-game-knowledge/            # Future submodule
│   ├── CLAUDE.md                   # Game design focus
│   └── PLAN.md                     # Board game goals
├── README.md                       # Master orchestration guide
└── OBSIDIAN-SETUP.md               # Cross-submodule linking guide
```

## Migration Steps

### Phase 1: Repository Creation
1. Create new GitHub repositories:
   - `unity-knowledge`
   - `ai-automation-knowledge` 
   - `career-skills-knowledge`
   - Keep current `knowledge` repo as future `knowledge-master`

### Phase 2: Content Migration
1. **Unity Knowledge Repo**:
   - Move: 01-Unity-Engine/, 02-CSharp-Programming/, 06-Game-Development-Math/, 07-Tools-Version-Control/
   - Create focused CLAUDE.md: "Primary Goal: Get Unity Developer Job"
   - Create focused PLAN.md with Unity-specific learning objectives

2. **AI Automation Knowledge Repo**:
   - Move: 08-AI-LLM-Automation/, 10-Web-Development-Automation/, 11-Data-Processing-Analytics/, 12-Customer-Service-Automation/, 14-Business-Process-Automation/
   - Create focused CLAUDE.md: "Primary Goal: 10x productivity through stealth AI automation"
   - Create focused PLAN.md with automation opportunities

3. **Career Skills Knowledge Repo**:
   - Move: 03-Soft-Skills/, 04-Career-Job-Search/, 05-Work-Types-Specializations/, 09-Freelancing-Remote-Work/, 13-Content-Creation-Marketing/, 15-Entrepreneurship-AI-Business/
   - Create focused CLAUDE.md: "Primary Goal: Professional development and career advancement"
   - Create focused PLAN.md with soft skills and networking goals

### Phase 3: Master Repository Setup
1. Clear current `knowledge` repo content
2. Add submodules:
   ```bash
   git submodule add https://github.com/username/unity-knowledge.git unity-knowledge
   git submodule add https://github.com/username/ai-automation-knowledge.git ai-automation-knowledge
   git submodule add https://github.com/username/career-skills-knowledge.git career-skills-knowledge
   ```
3. Create master README.md with navigation and purpose
4. Create OBSIDIAN-SETUP.md with cross-submodule linking instructions

### Phase 4: Obsidian Configuration
1. Configure Obsidian vault to include all submodules
2. Set up cross-linking between topics
3. Configure search to span all submodules
4. Test knowledge graph visualization

## Benefits of This Structure

### Topic-Specific Claude Code Interactions
- **Unity Repo**: Focused on Unity job preparation, C# mastery, game development
- **AI Automation Repo**: Focused on stealth productivity, automation tools, LLM integration
- **Career Skills Repo**: Focused on professional development, networking, soft skills

### Independent Development Cycles
- Work intensively on Unity prep without AI automation distractions
- Different update frequencies per topic area
- Topic-specific branching and versioning strategies

### Cleaner AI Context
- Each repo gets laser-focused Claude Code instructions
- No mixed signals or competing priorities
- Domain-specific content generation strategies

## Future Topic Additions
When ready to add new knowledge domains:
1. Create new repository (e.g., `bible-knowledge`, `board-game-knowledge`)
2. Add as submodule to master repo
3. Create topic-specific CLAUDE.md and PLAN.md
4. Update master README.md navigation

## Implementation Timeline
- **Phase 1**: Repository setup (1 day)
- **Phase 2**: Content migration (2-3 days)
- **Phase 3**: Master repo configuration (1 day)  
- **Phase 4**: Obsidian testing and optimization (1 day)

## Rollback Plan
If submodule approach proves too complex:
1. All content remains in individual repos
2. Can merge back to monorepo structure
3. Git history preserved in all cases

---

*This migration plan balances focused domain expertise with practical Git workflow management.*