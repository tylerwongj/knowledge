# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **knowledge management repository** designed as a personal learning resource for career development in Unity game development and AI-enhanced programming. The project generates comprehensive markdown documentation optimized for Obsidian, focusing on actionable learning materials that support 10x productivity through AI/LLM integration.

**Primary Goals:**
1. Create AI/LLM-enhanced work opportunities through quiet automation
2. Secure a Unity Developer position with comprehensive preparation materials
3. Master AI-augmented programming techniques for maximum productivity

## Repository Structure

The repository follows a **numerical categorization system** for organized learning:

```
01-Unity-Engine/               # Unity game development (primary focus)
02-CSharp-Programming/         # C# programming fundamentals
03-Soft-Skills/               # Professional development
04-Career-Job-Search/         # Job search automation and strategies
05-Work-Types-Specializations/ # Career path specializations
06-Game-Development-Math/     # Mathematical foundations
07-Tools-Version-Control/     # Development toolchain
```

**File Naming Convention:**
- Use `@` prefix for core files within categories (e.g., `@a-Core-Concepts.md`)
- Alphabetical sub-categorization for systematic learning progression
- `-NotionFriendly` suffix for alternative formatting when needed

## Content Development Workflow

### Content Generation Commands
Since this is a documentation-focused project, the primary "development" involves content creation:

```bash
# No traditional build commands - content is consumed directly
# Use Obsidian or any markdown viewer to review generated content
```

### Content Creation Process
1. **Planning**: Review `PLAN.md` and `CHATGPT-PLAN.md` for strategic direction
2. **Generation**: Use AI/LLM tools to create comprehensive markdown content
3. **Review**: Manual highlighting and annotation of key information for retention
4. **Organization**: Systematic filing using the numerical category system

### Quality Assurance
- Manual review of generated content for accuracy and relevance
- Highlighting important information for retention
- Cross-referencing with career goals and Unity job requirements

## Content Architecture

### Markdown File Structure
Each learning file follows this format:
```markdown
# @{letter}-{Topic} - {Descriptive Title}

## 🎯 Learning Objectives
- Specific, actionable learning goals

## 🔧 Core Content Sections
- Technical information with code examples
- Practical applications and use cases

## 🚀 AI/LLM Integration Opportunities
- How to use AI tools to accelerate learning in this area
- Specific prompts and automation opportunities

## 💡 Key Highlights
- Critical information for retention and application
```

### Unity-Specific Content (01-Unity-Engine/)
The Unity section contains comprehensive coverage of:
- **Core Concepts**: GameObjects, Components, Transform hierarchy
- **Project Setup**: Folder organization, naming conventions
- **Scripting**: C# in Unity, MonoBehaviour patterns, coroutines
- **Physics & Animation**: Rigidbody, colliders, animation systems
- **UI/UX**: Canvas systems, event handling, responsive design
- **Asset Management**: Import workflows, optimization, organization

## AI/LLM Integration Strategy

This repository is specifically designed to leverage AI tools for:

### Content Generation
- Use Claude Code CLI to generate comprehensive learning materials
- Prompt engineering for Unity-specific educational content
- Automated research compilation for job market analysis

### Learning Acceleration
- AI-generated code examples and explanations
- Automated summarization of complex technical concepts
- Custom prompts for Unity development scenarios

### Career Development Automation
- Resume and cover letter customization
- Job description analysis and keyword extraction
- Interview preparation materials generation

## Development Guidelines

### When Adding New Content
1. **Identify Category**: Place content in appropriate numbered directory
2. **Follow Naming**: Use `@` prefix with alphabetical sub-categorization
3. **Include AI Integration**: Always include AI/LLM opportunity sections
4. **Focus on Action**: Prioritize actionable information over theory
5. **Support Goals**: Ensure content directly supports Unity job preparation or AI-enhanced productivity

### Content Quality Standards
- Each file should be comprehensive enough to serve as a standalone learning resource
- Include practical code examples where applicable
- Provide specific AI prompts for further exploration
- Highlight key information for retention and application

### Git Workflow
- Use descriptive commit messages that indicate content area and purpose
- Follow the global git commit guidelines with `[CC]` prefix for Claude Code generated commits
- Focus commits on logical content groupings rather than individual files

## Future Repository Structure

**NOTE**: This repository is planned for migration to a submodule-based structure for better focus and topic-specific AI interactions. See `FUTURE-SUBMODULE-MIGRATION.md` for detailed migration plan.

### Planned Submodule Organization:
- **unity-knowledge**: Unity development, C#, game development math, tools
- **ai-automation-knowledge**: AI/LLM automation, productivity tools, stealth automation
- **career-skills-knowledge**: Soft skills, job search, professional development
- **Future additions**: bible-knowledge, board-game-knowledge, etc.

Each submodule will have its own focused CLAUDE.md and PLAN.md files for targeted AI interactions and domain-specific goals.

## Key Files Reference

- `PLAN.md` - Original project vision and goals
- `CHATGPT-PLAN.md` - Detailed strategic roadmap with specific learning domains
- `FUTURE-SUBMODULE-MIGRATION.md` - Plan for migrating to topic-focused submodules
- `01-Unity-Engine/@02-Project-Setup.md` - Unity project organization standards
- `01-Unity-Engine/@a-Core-Concepts.md` - Fundamental Unity architecture and systems

## Project Success Metrics

Success is measured by:
1. **Comprehensive Coverage**: All planned learning categories populated with high-quality content
2. **Practical Application**: Content directly applicable to Unity job requirements
3. **AI Integration**: Effective use of AI tools to accelerate learning and productivity
4. **Career Advancement**: Content supporting actual job acquisition and performance improvement
5. **Topic Focus**: Migration to submodule structure enabling laser-focused AI interactions per domain

This repository serves as both a learning system and a productivity multiplier, designed to achieve career goals through systematic knowledge building and AI-enhanced efficiency. The planned submodule migration will enhance this by providing domain-specific AI guidance and cleaner separation of learning objectives.