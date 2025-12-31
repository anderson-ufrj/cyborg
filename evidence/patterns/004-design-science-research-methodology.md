# Evidence: Design Science Research Methodology (DSRM)

**Source:** Foundational Papers on Design Science Research
**Authors:**
- Hevner, March, Park & Ram (2004) - "Design Science in Information Systems Research"
- Peffers, Tuunanen, Rothenberger & Chatterjee (2007) - "A Design Science Research Methodology"
**Date Collected:** 2025-12-30
**Citations:** 9,143+ (Hevner et al., 2004)

---

## Summary

Design Science Research (DSR) is a research paradigm focused on creating and evaluating IT artifacts to solve identified problems. Unlike behavioral science (which seeks to understand phenomena), design science seeks to create innovations that define ideas, practices, and technical capabilities.

This methodology forms the scientific foundation for the Prompt Engineering Lab and the DMMF research.

---

## Two Complementary Paradigms

### Behavioral Science
- **Goal:** Truth - understand and predict human/organizational behavior
- **Method:** Observation, hypothesis testing, empirical validation
- **Output:** Theories explaining phenomena

### Design Science
- **Goal:** Utility - create artifacts that serve human purposes
- **Method:** Build-and-evaluate iterative cycle
- **Output:** Artifacts that extend human/organizational capabilities

```
┌─────────────────────────────────────────────────────────────┐
│                     IS Research Framework                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Environment          IS Research           Knowledge Base   │
│  ┌─────────┐         ┌─────────────┐        ┌───────────┐   │
│  │ People  │         │  Develop    │        │Foundations│   │
│  │ Orgs    │ ──────► │  Build      │ ◄───── │ Theories  │   │
│  │ Tech    │ Relevance│  Justify    │ Rigor  │ Methods   │   │
│  └─────────┘         └─────────────┘        └───────────┘   │
│       ▲                     │                     ▲          │
│       │                     ▼                     │          │
│   Needs              Application              Additions      │
│                      in Context              to Knowledge    │
└─────────────────────────────────────────────────────────────┘
```

---

## Hevner's 7 Guidelines for Design Science Research

### Guideline 1: Design as an Artifact
> *"Design-science research must produce a viable artifact in the form of a construct, a model, a method, or an instantiation."*

**Types of IT Artifacts:**
| Type | Description | Example in Prompt Engineering |
|------|-------------|------------------------------|
| **Constructs** | Vocabulary and symbols | DMMF dimensions (Cognitive, Affective, Conative, Reflective) |
| **Models** | Abstractions and representations | Mental model framework, skill composition model |
| **Methods** | Algorithms and practices | Cognitive workflow patterns (chain, parallel, route) |
| **Instantiations** | Implemented systems | Prompt Engineering Lab, skill system |

---

### Guideline 2: Problem Relevance
> *"The objective of design-science research is to develop technology-based solutions to important and relevant business problems."*

**Problem Space for Prompt Engineering Lab:**
- Fragmented human-AI collaboration approaches
- Lack of personalized context in AI interactions
- No systematic way to evolve prompts based on evidence
- Gap between cognitive research and practical AI use

---

### Guideline 3: Design Evaluation
> *"The utility, quality, and efficacy of a design artifact must be rigorously demonstrated via well-executed evaluation methods."*

**Evaluation Methods:**
| Method | Description | Application |
|--------|-------------|-------------|
| **Observational** | Case study, field study | Track prompt effectiveness over time |
| **Analytical** | Static/dynamic analysis | Architecture evaluation |
| **Experimental** | Controlled experiment | A/B testing prompts |
| **Testing** | Functional, structural | Skill validation |
| **Descriptive** | Informed argument, scenarios | Use case documentation |

---

### Guideline 4: Research Contributions
> *"Effective design-science research must provide clear and verifiable contributions in the areas of the design artifact, design foundations, and/or design methodologies."*

**Contribution Types:**
1. **Artifact contribution** - Novel, generalizable solution
2. **Foundation contribution** - New constructs, models, methods
3. **Methodology contribution** - Evaluation methods, metrics

---

### Guideline 5: Research Rigor
> *"Design-science research relies upon the application of rigorous methods in both the construction and evaluation of the design artifact."*

**Rigor Requirements:**
- Theoretical foundations from reference disciplines
- Prior research grounding
- Appropriate evaluation methodologies
- Mathematical formalisms where applicable

---

### Guideline 6: Design as a Search Process
> *"The search for an effective artifact requires utilizing available means to reach desired ends while satisfying laws in the problem environment."*

**Key Concepts:**
- **Means** - Resources to construct artifact (components, actions)
- **Ends** - Goals and constraints defining meta-requirements
- **Laws** - Environmental constraints

The build-and-evaluate loop is inherently iterative:
```
Problem → Design → Build → Evaluate → Learn → Redesign → ...
```

---

### Guideline 7: Communication of Research
> *"Design-science research must be presented effectively both to technology-oriented as well as management-oriented audiences."*

**Two Audiences:**
1. **Technical** - Implementation details, architecture
2. **Managerial** - Business value, problem solved

---

## DSRM Process Model (Peffers et al.)

Six activities in the design science research methodology:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DSRM Process Model                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐             │
│  │  1.      │   │  2.      │   │  3.      │   │  4.      │             │
│  │ Problem  │──►│ Objectives│──►│ Design & │──►│ Demon-  │             │
│  │ Identify │   │ Solution │   │ Develop  │   │ stration │             │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘             │
│       │                              │              │                    │
│       │                              │              ▼                    │
│       │                              │        ┌──────────┐              │
│       │                              │        │  5.      │              │
│       │                              └───────►│ Evaluate │              │
│       │                                       └──────────┘              │
│       │                                             │                    │
│       │                                             ▼                    │
│       │                                       ┌──────────┐              │
│       │                                       │  6.      │              │
│       └──────────────────────────────────────►│Communicate│             │
│                                               └──────────┘              │
│                                                                          │
│  Entry Points:                                                           │
│  • Problem-centered (Activity 1)                                         │
│  • Objective-centered (Activity 2)                                       │
│  • Design-centered (Activity 3)                                          │
│  • Client/Context-centered (Activity 4)                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Activity Descriptions

| Activity | Description | Prompt Engineering Lab Application |
|----------|-------------|-----------------------------------|
| **1. Problem Identification** | Define problem and justify value | Fragmented prompt engineering practices |
| **2. Objectives of Solution** | Infer from problem, quantify if possible | Personalized, evidence-based prompt system |
| **3. Design & Development** | Create artifact (constructs, models, methods) | DMMF framework, skill system, evidence patterns |
| **4. Demonstration** | Use artifact in experiment, simulation, proof | Apply system to real tasks, cognitive workflows |
| **5. Evaluation** | Compare objectives to observed results | Measure effectiveness, iterate on prompts |
| **6. Communication** | Publish results to relevant audiences | Documentation, papers, reproducible artifacts |

---

## Research Entry Points

Different starting points for DSR projects:

| Entry Point | Trigger | Example |
|-------------|---------|---------|
| **Problem-centered** | New problem identified | AI collaboration lacks personalization |
| **Objective-centered** | Industry/research need | Need evidence-based prompt engineering |
| **Design-centered** | Existing artifact to extend | Improve Anthropic patterns for personal use |
| **Client-centered** | Consulting engagement | Build system for specific user needs |

---

## Application to Prompt Engineering Lab

### Artifact Mapping

| DSRM Concept | Lab Implementation |
|--------------|-------------------|
| **Constructs** | DMMF dimensions, skill vocabulary, pattern names |
| **Models** | Cognitive profile model, skill composition model |
| **Methods** | Cognitive workflows (chain, parallel, route, orchestrator, evaluator) |
| **Instantiation** | prompt-engineering/ repository structure |

### Research Cycle

```
1. PROBLEM: Fragmented human-AI interaction approaches
           ↓
2. OBJECTIVES: Create personalized, evidence-based prompt system
           ↓
3. DESIGN: DMMF framework + skill system + evidence base
           ↓
4. DEMONSTRATION: Apply to real development tasks
           ↓
5. EVALUATION: Measure effectiveness, gather feedback
           ↓
6. COMMUNICATION: CLAUDE.md, skills, patterns documentation
           ↓
   (iterate)
```

---

## Connection to DMMF Research

The DMMF (Developer Mental Model Framework) research by Silva (2025) follows DSRM:

| DSRM Activity | DMMF Research Implementation |
|---------------|------------------------------|
| Problem ID | Gap in understanding developer mental models |
| Objectives | Map cognitive profiles across 4 dimensions |
| Design | Mixed-methods approach (40 repos, 2,799 commits) |
| Demonstration | Cidadão.AI case study with 22 agents |
| Evaluation | Quantitative metrics + qualitative analysis |
| Communication | Research paper + prompt engineering lab |

---

## Key Insights for Evidence-Based Prompt Engineering

### 1. Build-Evaluate Cycle
Prompts should be treated as artifacts subject to iterative refinement:
```
Write Prompt → Test → Observe Results → Analyze → Improve → Repeat
```

### 2. Relevance Over Novelty
Focus on solving real problems, not creating novel solutions for their own sake.

### 3. Rigor Through Evidence
Document what works and why. Maintain evidence base of effective patterns.

### 4. Multiple Evaluation Methods
Don't rely on single metrics. Use observational, analytical, and experimental methods.

### 5. Communication is Essential
Knowledge not shared is knowledge lost. Document everything systematically.

---

## Source Files

| File | Location | Description |
|------|----------|-------------|
| `DSRM.pdf` | `docs/` | Peffers et al. (2007-8) - DSRM process model |
| `Design_Science_in_Information_Systems_Research.pdf` | `docs/` | Hevner et al. (2004) - 7 Guidelines |

---

## References

- Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design Science in Information Systems Research. *MIS Quarterly*, 28(1), 75-105.
- Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A Design Science Research Methodology for Information Systems Research. *Journal of Management Information Systems*, 24(3), 45-77.
- Silva, A. H. (2025). Developer Mental Model Framework. *DMMF Research*.

---

*This evidence document connects design science methodology to the prompt engineering lab's scientific foundation.*
