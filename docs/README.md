# Claude Project Planner Documentation

> AI-powered project planning toolkit that generates comprehensive, research-backed project plans with architecture documents, sprint plans, cost analyses, and implementation roadmaps.

---

## 🚀 Getting Started

**New to Claude Project Planner?** Start here:

### 1. Installation (2 minutes)

```bash
# Install as Claude Code plugin (recommended)
claude plugin install flight505/claude-project-planner

# Restart Claude Code when prompted
```

### 2. Understand How It Works

Read **[How It Works](../README.md#-how-it-works)** to understand the 4-step workflow:
- **Fill Template** - Describe your project
- **Validate Setup** - Check dependencies
- **Configure Options** - Answer 8 questions
- **Generate Plan** - AI creates comprehensive plan

### 3. First Planning Session

```bash
# Start comprehensive planning
/full-plan my-project

# Answer the 8 interactive questions
# Get 50+ documents in 30 min - 2 hours
```

### 4. Explore Capabilities

Browse **[Skills Reference](SKILLS.md)** to see all 19+ planning capabilities.

---

## 📖 Documentation Sections

### For End Users

| Guide | Description | When to Read |
|-------|-------------|--------------|
| **[Features Overview](FEATURES.md)** | Complete feature documentation with examples | To understand what's possible |
| **[Workflows](WORKFLOWS.md)** | End-to-end usage examples with progress tracking | Advanced usage patterns |
| **[Skills Reference](SKILLS.md)** | All 19+ skills with detailed descriptions | To learn available capabilities |
| **[User Flow](USER_FLOW.md)** | User interaction patterns and flows | UX understanding |
| **[Parallelization Guide](PARALLELIZATION_GUIDE.md)** | Performance optimization (14% time savings) | Speed optimization |
| **[API Reference](API.md)** | Python API for programmatic use | When using Python API |
| **[Troubleshooting](TROUBLESHOOTING.md)** | Common issues and solutions | When you encounter problems |

### For Developers

| Guide | Description | Audience |
|-------|-------------|----------|
| **[Development Guide](DEVELOPMENT.md)** | Architecture, plugin development, contributing | Contributors, maintainers |
| **[Dependencies](DEPENDENCIES.md)** | System requirements and optional dependencies | Installation help |
| **[Releasing](RELEASING.md)** | Version management, PyPI publishing | Maintainers |

---

## 🎯 Quick Navigation by Use Case

### I want to create a comprehensive project plan

1. **Install**: [Quick Start](../README.md#-quick-start)
2. **Run**: `/full-plan my-project`
3. **Configure**: Answer 8 questions about AI provider, research depth, phases, quality checks
4. **Review**: Check `planning_outputs/` for 50+ documents

### I want to understand the planning process

1. **Read**: [How It Works](../README.md#-how-it-works) - ELI5 + technical deep dive
2. **Explore**: [The 8 Questions](../README.md#the-8-questions-no-flags-to-remember) - Interactive configuration
3. **Learn**: [What Happens Under the Hood](../README.md#what-happens-under-the-hood) - 3-layer architecture

### I want to optimize performance

1. **Enable Parallelization**: [Parallelization Guide](PARALLELIZATION_GUIDE.md)
2. **Choose Research Depth**: Quick (15 min) vs Balanced (1 hour) vs Comprehensive (2 hours)
3. **Monitor Progress**: [Workflows](WORKFLOWS.md) - External monitoring and resume

### I want to use the Python API

1. **Quick Start**: [API Reference](API.md#quick-start)
2. **Examples**: [API Examples](API.md#examples)
3. **Reference**: [API Documentation](API.md#complete-api-reference)

### I'm encountering issues

1. **Check**: [Troubleshooting Guide](TROUBLESHOOTING.md)
2. **Search**: [GitHub Issues](https://github.com/flight505/claude-project-planner/issues)
3. **Report**: Create new issue with details

---

## 💡 Key Features

### Interactive Question-Based Configuration
No command-line flags to remember! Answer **8 question groups** covering:
- AI Provider (Gemini Deep Research vs Perplexity)
- Research Depth (Quick/Balanced/Comprehensive)
- Parallelization (14% faster)
- Approval Gates (review after each phase)
- Core & Optional Phases
- Quality Checks & Output Formats

### Multi-Provider AI Research
- **Gemini Deep Research**: 60 min, comprehensive multi-step reasoning, 1M context
- **Perplexity Sonar**: 30 sec, fast web search with citations
- **Automatic fallback**: Gemini → Perplexity if API fails

### 3-Tier Progress Tracking
- **Tier 1**: Streaming progress (Perplexity ~30s)
- **Tier 2**: Progress files with external monitoring (Deep Research ~60 min)
- **Tier 3**: Phase checkpoints (resume from 15%/30%/50%)

### Comprehensive Output
After running `/full-plan`, you get:
- **50+ documents**: Market research, architecture, costs, sprints, marketing
- **10+ diagrams**: C4 models, sequence diagrams, ERDs, deployment
- **1 PDF report**: Professional compilation with IEEE citations

---

## 🔍 Quick Links

- **[GitHub Repository](https://github.com/flight505/claude-project-planner)** - Source code and issues
- **[PyPI Package](https://pypi.org/project/project-planner/)** - Python package
- **[Changelog](../CHANGELOG.md)** - Version history
- **[Documentation Index](DOCUMENTATION_INDEX.md)** - Complete documentation map

---

## 🎓 Learning Paths

### Beginner Path (First-Time Users)

1. **Read**: [Main README](../README.md) → 5 minutes
2. **Install**: Follow [Quick Start](../README.md#-quick-start) → 2 minutes
3. **Try**: Create your first plan → 30-120 minutes
4. **Explore**: Browse [Skills Overview](SKILLS.md) → 10 minutes

### Intermediate Path (Regular Users)

1. **Master**: [The 8 Questions](../README.md#the-8-questions-no-flags-to-remember)
2. **Learn**: [Workflows](WORKFLOWS.md) - Progress tracking and resume
3. **Optimize**: [Parallelization Guide](PARALLELIZATION_GUIDE.md)
4. **Customize**: [When to Use Each Mode](../README.md#when-to-use-each-mode)

### Advanced Path (Power Users)

1. **API**: Read [API Reference](API.md)
2. **Understand**: [What Happens Under the Hood](../README.md#what-happens-under-the-hood)
3. **Extend**: Learn [Development Guide](DEVELOPMENT.md)
4. **Contribute**: Follow [Contributing Guide](DEVELOPMENT.md#contributing)

---

## 📊 Documentation Status

**Current Version**: v1.4.4
**Last Updated**: January 2026
**Status**: ✅ Complete and Current

### Coverage
- ✅ Installation guides (Plugin, CLI, API)
- ✅ Usage examples (all document types)
- ✅ API reference (complete with examples)
- ✅ Skills documentation (19+ skills)
- ✅ Troubleshooting guide
- ✅ Development guide
- ✅ Release process
- ✅ Workflow examples with progress tracking

---

## 💬 Get Help

**Found an issue?**
1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [GitHub Issues](https://github.com/flight505/claude-project-planner/issues)
3. Create new issue with "documentation" label
4. For urgent help, mention in issue

**Want to contribute?**
1. Read [Development Guide](DEVELOPMENT.md)
2. Check [open issues](https://github.com/flight505/claude-project-planner/issues)
3. Submit pull request

---

<p align="center">
  <strong>Ready to start planning?</strong><br>
  <a href="../README.md#-quick-start">Get Started in 2 Minutes →</a>
</p>
