# Evidence: Anthropic Agent Patterns

**Source:** Anthropic Cookbook - Building Effective Agents
**Authors:** Erik Schluntz, Barry Zhang (Anthropic)
**Date Collected:** 2025-12-30
**Reference:** https://anthropic.com/research/building-effective-agents

---

## Summary

Official Anthropic patterns for building multi-LLM agent systems. These are production-tested approaches from Anthropic's research team.

---

## Basic Building Blocks

### 1. Prompt Chaining

**What:** Sequential LLM calls where each step builds on previous results.

**When to use:**
- Complex transformations requiring multiple steps
- Data processing pipelines
- When intermediate results need validation

**Implementation:**
```python
def chain(input: str, prompts: list[str]) -> str:
    result = input
    for prompt in prompts:
        result = llm_call(f"{prompt}\nInput: {result}")
    return result
```

**Example:** Data extraction → Normalization → Sorting → Formatting

---

### 2. Parallelization

**What:** Distribute independent subtasks across multiple LLM calls concurrently.

**When to use:**
- Multiple perspectives on same data
- Stakeholder analysis
- Batch processing

**Implementation:**
```python
def parallel(prompt: str, inputs: list[str], n_workers: int = 3) -> list[str]:
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(llm_call, f"{prompt}\nInput: {x}") for x in inputs]
        return [f.result() for f in futures]
```

**Example:** Analyze impact on Customers, Employees, Investors, Suppliers simultaneously

---

### 3. Routing

**What:** Dynamically select specialized LLM path based on input classification.

**When to use:**
- Customer support ticket handling
- Multi-domain queries
- Specialized expertise required

**Implementation:**
```python
def route(input: str, routes: dict[str, str]) -> str:
    # First: classify input to determine route
    route_key = llm_call(f"Classify into: {list(routes.keys())}\nInput: {input}")
    # Then: process with specialized prompt
    return llm_call(f"{routes[route_key]}\nInput: {input}")
```

**Example:** Route tickets to billing, technical, account, or product teams

---

## Advanced Workflows

### 4. Orchestrator-Workers

**What:** Central orchestrator analyzes task and delegates to specialized workers.

**When to use:**
- Tasks requiring multiple perspectives
- Optimal subtasks depend on specific input
- Need to compare different strategies

**When NOT to use:**
- Simple, single-output tasks
- Latency-critical applications
- Subtasks are predictable (use simple parallelization)

**Two Phases:**
1. **Analysis & Planning:** Orchestrator determines what approaches are valuable
2. **Execution:** Workers receive original task + specific instructions

**Key Prompts:**

```python
ORCHESTRATOR_PROMPT = """
Analyze this task and break it down into 2-3 distinct approaches:
Task: {task}

<analysis>Explain your understanding...</analysis>
<tasks>
    <task>
        <type>formal</type>
        <description>Write precise, technical version...</description>
    </task>
</tasks>
"""

WORKER_PROMPT = """
Generate content based on:
Task: {original_task}
Style: {task_type}
Guidelines: {task_description}

<response>Your content here...</response>
"""
```

---

### 5. Evaluator-Optimizer

**What:** Iterative loop that evaluates outputs and refines them.

**When to use:**
- Quality is critical
- Clear evaluation criteria exist
- Willing to trade latency for quality

**Pattern:**
```
Generate → Evaluate → Improve → Re-evaluate → (repeat until satisfied)
```

---

## Design Principles from Anthropic

### 1. XML for Structured Output
- Reliable and language-model-friendly
- Easy to parse with regex
- Clear boundaries for content

### 2. Context Preservation
- Workers receive both original task AND specific instructions
- Full context enables better results

### 3. Error Handling
- Validate worker responses
- Handle empty outputs gracefully
- Provide meaningful error messages

### 4. Cost Optimization
- Use Haiku for simple workers
- Use Sonnet/Opus for orchestrators
- Consider latency vs quality tradeoffs

---

## Prompt Engineering Insights

### Orchestrator Design
- Ask for specific number of approaches (2-3)
- Require analysis before task breakdown
- Use XML structure for reliable parsing

### Worker Design
- Provide full context (original task + specific role)
- Clear output format requirements
- Style/tone guidance

### Routing Design
- Include chain-of-thought reasoning
- List all available routes explicitly
- Validate route selection before processing

---

## Application to Personal Prompt Engineering

| Anthropic Pattern | Personal Application |
|-------------------|---------------------|
| Chaining | Sequential context loading (identity → goals → mode) |
| Parallelization | Multi-perspective analysis of decisions |
| Routing | Context-dependent prompt selection (debug vs explore) |
| Orchestrator-Workers | Complex task decomposition with specialized modes |
| Evaluator-Optimizer | Prompt refinement through interaction feedback |

---

## Files Downloaded

| File | Description |
|------|-------------|
| `basic_workflows.ipynb` | Chain, Parallel, Route implementations |
| `orchestrator_workers.ipynb` | Full orchestrator pattern |
| `evaluator_optimizer.ipynb` | Iterative refinement pattern |
| `util.py` | Helper functions for LLM calls |

---

## Key Takeaways for Prompt Engineering Lab

1. **Structure enables reliability** - Use XML/structured output for parsing
2. **Context is king** - Always provide full context to workers
3. **Adapt dynamically** - Let orchestrators decide subtasks at runtime
4. **Validate outputs** - Handle failures gracefully
5. **Optimize for use case** - Balance cost, latency, and quality

---

*Source: Anthropic Cookbook, MIT License*
*Full implementation: evidence/sources/anthropic-patterns/*
