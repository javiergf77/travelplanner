# CrewAI Project Structure

## 📁 Two Approaches Available

This project supports **both** CrewAI configuration styles:

### ⭐ Approach 1: YAML Configuration (Recommended)

**Like your debate app** - Clean separation of configuration and code.

```
travelplanner/
├── config/
│   ├── agents.yaml          # Agent definitions
│   └── tasks.yaml           # Task definitions
└── crew.py                  # Crew class with @agent/@task decorators
```

**Advantages:**
- ✅ Clean separation: config vs logic
- ✅ Easy to edit without touching code
- ✅ Better for non-developers to modify
- ✅ CrewAI's recommended structure
- ✅ Easier to maintain and version

**Usage:**
```python
# crew_setup_new.py uses YAML by default
use_yaml_config=True  # Default
```

### Approach 2: Programmatic (Legacy)

**Pure Python** - Everything defined in code.

```
travelplanner/
└── agents/
    └── travel_agents.py     # Agents, tasks, and crew in Python
```

**Advantages:**
- ✅ Everything in one place
- ✅ More dynamic/flexible
- ✅ Easier for Python developers

**Usage:**
```python
# In crew_setup_new.py
use_yaml_config=False
```

---

## 🔧 YAML Configuration Structure

### `config/agents.yaml`

Defines agent roles, goals, and backstories:

```yaml
travel_planner:
  role: >
    Travel Planning Coordinator
  goal: >
    Create comprehensive travel plans
  backstory: >
    You are an expert with 15 years experience...

policy_officer:
  role: >
    Policy Compliance Officer
  goal: >
    Ensure policy compliance
  backstory: >
    You are a detail-oriented specialist...
```

### `config/tasks.yaml`

Defines tasks with parameters and context:

```yaml
search_options:
  description: >
    Plan a business trip with these parameters:
    - Origin: {origin}
    - Destination: {destination}
    - Budget: ${budget}
  expected_output: >
    List of 5 travel packages with details
  agent: travel_planner

check_policy:
  description: >
    Review packages for policy compliance
  expected_output: >
    Compliance report with violations
  agent: policy_officer
  context:
    - search_options  # Uses output from search_options
```

**Parameter Injection:**
- Use `{parameter_name}` in YAML
- Pass via `crew.kickoff(inputs={...})`

### `crew.py`

Main crew class with decorators:

```python
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class TravelPlannerCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def travel_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['travel_planner'],
            tools=[...],
            llm=self.llm
        )
    
    @task
    def search_options(self) -> Task:
        return Task(
            config=self.tasks_config['search_options'],
            agent=self.travel_planner()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Auto-collected from @agent
            tasks=self.tasks,    # Auto-collected from @task
            process=Process.sequential
        )
```

---

## 🎯 Comparison with Debate App

### Debate App Structure

```
debate/
├── config/
│   ├── agents.yaml          # Proposer, Opposer, Judge
│   └── tasks.yaml           # Propose, Oppose, Judge tasks
└── crew.py                  # DebateCrew class
```

### Travel App Structure (YAML)

```
travelplanner/
├── config/
│   ├── agents.yaml          # Planner, Policy, Research, Booking
│   └── tasks.yaml           # Search, Policy, Research, Final
└── crew.py                  # TravelPlannerCrew class
```

**Same pattern!** ✅

---

## 🚀 How to Use

### Run with YAML Config (Default)

```python
python app_gradio_enhanced.py
# Check "Use CrewAI Agents"
# YAML config is used by default
```

### Switch to Programmatic

Edit `crew_setup_new.py`:
```python
use_yaml_config = False  # Line 24
```

### Modify Agents (YAML)

Just edit `config/agents.yaml`:
```yaml
travel_planner:
  role: >
    Senior Travel Coordinator  # <-- Change here
  goal: >
    Your new goal here
```

No code changes needed!

### Modify Tasks (YAML)

Edit `config/tasks.yaml`:
```yaml
search_options:
  description: >
    Your new task description with {parameters}
```

---

## 📊 When to Use Each Approach

### Use YAML Configuration When:
- ✅ Multiple team members will edit prompts
- ✅ Non-developers need to adjust agent behavior
- ✅ You want clean separation of concerns
- ✅ You're building a production system
- ✅ You need easy version control of prompts

### Use Programmatic When:
- ✅ Agents/tasks are highly dynamic
- ✅ Configuration depends on runtime logic
- ✅ You're prototyping quickly
- ✅ Everything is managed by developers
- ✅ You need complex conditional logic

---

## 🔄 Migration Guide

### From Programmatic → YAML

1. **Extract agent definitions** to `config/agents.yaml`:
```python
# Before (agents/travel_agents.py)
Agent(
    role="Travel Planning Coordinator",
    goal="Create travel plans",
    backstory="You are an expert..."
)

# After (config/agents.yaml)
travel_planner:
  role: >
    Travel Planning Coordinator
  goal: >
    Create travel plans
  backstory: >
    You are an expert...
```

2. **Extract task definitions** to `config/tasks.yaml`:
```python
# Before
Task(
    description="Plan a trip...",
    expected_output="List of packages",
    agent=planner
)

# After
search_options:
  description: >
    Plan a trip...
  expected_output: >
    List of packages
  agent: travel_planner
```

3. **Create crew class** with decorators in `crew.py`

4. **Update orchestrator** to use new crew

---

## 🎓 Best Practices

### YAML Files
- Use `>` for multi-line strings (removes line breaks)
- Use `|` to preserve line breaks
- Keep descriptions clear and concise
- Use `{parameter}` for dynamic values

### Crew Class
- One `@agent` method per agent
- One `@task` method per task
- One `@crew` method (returns the crew)
- Use meaningful names for methods

### Tools
- Define tools separately
- Attach to agents in `@agent` methods
- Keep tool code modular

### Context
- Use `context: [task1, task2]` in YAML
- Tasks run sequentially
- Later tasks can access earlier outputs

---

## 📚 Resources

- **CrewAI Docs**: https://docs.crewai.com/concepts/crews
- **YAML Syntax**: https://yaml.org/
- **Your Debate App**: `c:\projects\debate` (reference implementation)

---

## ✅ Summary

**Current Setup:**
- ✅ **YAML Configuration**: `config/agents.yaml` + `config/tasks.yaml` + `crew.py` (ACTIVE)
- ✅ **Programmatic**: `agents/travel_agents.py` (LEGACY, still works)
- ✅ **Simple Mode**: Direct tools, no LLM (FAST)

**Switch Between:**
```python
# In crew_setup_new.py line 24
use_yaml_config = True   # YAML (like debate app)
use_yaml_config = False  # Programmatic
use_crewai = False       # Simple mode (no agents)
```

The YAML structure is **recommended** for maintainability and matches your debate app's pattern! 🎯

