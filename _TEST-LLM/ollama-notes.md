# Ollama Investigation Notes

## 🔧 Quick Reference Commands

```bash
# Model Management
ollama list                    # Show installed models
ollama pull llama3.1:8b        # Download better reasoning model
ollama rm llama3.2:1b          # Remove bad 1b model
ollama --version               # Check Ollama version

# Using Models
ollama run llama3.2:3b         # Fast model for quick tasks
ollama run llama3.1:8b         # Better reasoning model
ollama run model-name "question" # One-off question

# Testing Knowledge System Scoring
ollama run llama3.1:8b "Rate 0.0-1.0: Q: What is Sola Scriptura? A: I don't know. Format: SCORE: [number]"

# Interactive Chat (exit with /bye or Ctrl+C)
ollama run llama3.1:8b
```

## 🎯 Recommended Model Setup

**Download these 2 models:**
```bash
ollama pull llama3.1:8b        # Better reasoning (4.7 GB)
# Keep llama3.2:3b (already have)  # Fast responses (2.0 GB)
ollama rm llama3.2:1b          # Remove problematic model
```

**Usage Strategy:**
- **Quick tasks**: `ollama run llama3.2:3b` 
- **Knowledge system evaluation**: `ollama run llama3.1:8b`
- **Complex reasoning**: `ollama run llama3.1:8b`

---

## 🎯 Original Problem
User's AI-Powered Knowledge Testing System was giving terrible scores:
- "I don't know" answers getting 80-90% scores 
- System saying answers were wrong when they were clearly correct
- Local LLM evaluation was completely unreliable

## 🔍 What We Discovered

### Architecture Understanding
**Ollama has 2 parts:**
1. **Ollama Server** (global) - The actual LLM runner/daemon
2. **ollama Python package** (per-project venv) - Client to talk to server

**Models are stored globally**: `~/.ollama/models/` (not in venv)

### Current Setup
- **Ollama Version**: 0.9.6
- **Models Installed**: 
  - llama3.2:1b (1.3 GB) - Fast but poor reasoning
  - llama3.2:3b (2.0 GB) - Better balance
- **Python Package**: Only in `_TESTING-SYSTEM/venv/`

### Who Made What
- **Llama models**: Created by Meta/Facebook (the AI brains)
- **Ollama tool**: Created by Ollama Inc. (makes running Llama easy)
- **Different companies, similar names!**

### Why It's Free
**Meta's Strategy:**
- Compete with OpenAI/Google
- Drive adoption of their AI stack
- Strategic business move, not charity

**Ollama Inc. Strategy:**
- VC-funded growth phase
- Likely planning enterprise features later
- Classic freemium model

**Key Insight**: Running locally = $0 server costs for everyone!

## 🧪 Testing Results

### Test Setup Created
- Simple Python script in `_TEST-LLM/test_llm.py`
- Only needs `ollama>=0.3.0` in requirements.txt
- Tests basic chat, scoring format, and bad answer handling

### Critical Findings
✅ **Basic Chat Works**: Model responds properly
✅ **Format Following**: Can output "SCORE: 0.8" format  
✅ **Some Logic**: Correctly scored "I don't know" as 0.0

❌ **Major Logic Failure**: For 2+2=4 question, responded:
> "The student's answer, 4, is incorrect because the correct calculation is 2 + 2 = 4, not 4."

**This is completely nonsensical reasoning!**

### Root Cause
The `llama3.2:1b` model is **too small for reliable logical reasoning**:
- Good at following format instructions
- Terrible at actual evaluation logic
- Explains the 80-90% scores for wrong theology answers

## 🎯 Solutions Identified

### 1. Keep Keyword-Only Scoring (Current Working Solution)
**Pros:**
- Fast and reliable
- No AI weirdness
- Already working well

**Implementation:**
- Disabled LLM evaluation in answer_evaluator.py
- Enhanced keyword matching with semantic hints
- Proper scoring for "I don't know" answers (10%)

### 2. Try Better Model
**Option**: Use `llama3.2:3b` (already installed)
- Better reasoning than 1b version
- Still fast enough
- Might fix logic issues

### 3. Add OpenAI API (Most Reliable)
- Costs money but very reliable
- Would need API key setup
- Professional-grade evaluation

## 🔧 Terminal Commands Learned

```bash
# Check Ollama version and models
ollama --version
ollama list

# Interactive chat
ollama run llama3.2:1b
ollama run llama3.2:3b

# Quick one-off questions  
ollama run llama3.2:1b "What is 2+2?"

# Download new models
ollama pull llama3.1:8b

# Remove models
ollama rm model-name
```

## 📊 Final Status

**Knowledge Testing System Status:**
✅ **Question Generation**: Works perfectly - extracts real theology definitions
✅ **Answer Evaluation**: Keyword-based scoring works reliably  
✅ **User Interface**: Clean, immediate feedback
✅ **Overall System**: Ready for use!

**AI Evaluation Status:**
❌ **Local LLM**: Disabled due to poor reasoning
⚠️ **OpenAI API**: Not configured (no API key)
✅ **Keyword Matching**: Enhanced and working well

## 💡 Key Takeaways

1. **Small models (1b) are unreliable** for complex reasoning tasks
2. **Local AI isn't always better** - sometimes simple algorithms work better
3. **Ollama makes local LLMs easy** but doesn't fix model limitations  
4. **Virtual environments work correctly** - no global package pollution
5. **The "AI-Powered" label was misleading** - keyword matching is the reliable part

## 🎯 Next Steps

1. **System is ready to use** with keyword-only evaluation
2. **Optional**: Test llama3.2:3b for better reasoning
3. **Optional**: Add OpenAI API key for premium evaluation
4. **Continue using** the working knowledge testing system as-is

The investigation successfully identified and fixed the core scoring issues!