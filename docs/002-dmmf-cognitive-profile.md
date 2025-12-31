# Evidence: DMMF Cognitive Profile

**Source:** "From Commits to Cognition" research paper (Silva, 2025)
**Date Collected:** 2025-12-30
**Dataset:** 40 repositories, 2,799 commits (Nov 2022 - Dec 2025)

---

## Summary

This document extracts the key findings from the DMMF research to inform prompt engineering decisions. The four dimensions provide a scientific basis for calibrating AI interactions.

---

## Cognitive Dimension Profile

### Key Finding: Hierarchical Modularity
- Average directory depth: **4.2 levels**
- Consistent functional separation patterns
- Field-independent cognitive style

### Implication for Prompts
```
✅ Present information in hierarchical structures
✅ Use clear boundaries between concepts
✅ Allow compartmentalized thinking
❌ Don't mix concerns in single responses
❌ Don't flatten complex topics into linear lists
```

### Autoethnographic Insight (from paper)
> "I experience anxiety when code lacks clear boundaries. The act of creating a new directory feels like creating mental space—each folder is a container that lets me forget what's inside while working elsewhere."

---

## Affective Dimension Profile

### Key Finding: Quality as Non-Negotiable
- Test coverage average: **76%** in main projects
- Strict linting in **85%** of active repositories
- Tests = anxiety management, not just quality assurance

### Sentiment Analysis (BERT)
| Commit Type | Positive Sentiment |
|-------------|-------------------|
| feat | 50.3% |
| style | 42.1% |
| docs | 16.5% |
| refactor | 11.5% |
| test | 5.3% |
| fix | 4.8% |
| chore | 3.7% |

### Implication for Prompts
```
✅ Acknowledge quality concerns seriously
✅ Suggest tests when implementing features
✅ Match emotional tone to task type (feat = positive, fix = focused)
❌ Don't dismiss quality concerns as "over-engineering"
❌ Don't skip validation steps
```

### Autoethnographic Insight (from paper)
> "Shipping without tests feels physically uncomfortable—like leaving home without locking the door."

---

## Conative Dimension Profile

### Key Finding: Technology as Civic Tool
- Flagship project: Cidadão.AI (government transparency)
- 22 AI agents named after Brazilian historical figures
- Values: ethics, transparency, social impact

### Implication for Prompts
```
✅ Connect technical decisions to broader impact
✅ Reference ethical considerations when relevant
✅ Acknowledge Brazilian cultural context
❌ Don't treat technology as value-neutral
❌ Don't ignore social implications of technical choices
```

---

## Reflective Dimension Profile

### Key Finding: Continuous Course-Correction
- **41.9%** of commits are refactor-related (fix, refactor, cleanup, simplify)
- **83.4%** of refactors occur in clusters (reflection-in-action)
- **16.6%** are isolated refactors (reflection-on-action)

### Temporal Patterns
- Peak activity: weekday evenings (18:00-23:00 local)
- Reduced weekend activity
- Minimal commits during sleeping hours

### Implication for Prompts
```
✅ Support iterative refinement (expect multiple passes)
✅ Encourage Schön-style reflection (both in-action and on-action)
✅ Acknowledge that first solutions will be refined
❌ Don't present solutions as final/perfect
❌ Don't resist when asked to iterate
```

---

## Failed Hypotheses (Falsifiability Evidence)

The research tested and rejected several intuitive hypotheses:

### Hypothesis 1: Longer commit messages at night
- **Expected:** More deliberate reflection during quiet hours
- **Result:** Not statistically significant (p = 0.091)
- **Status:** REJECTED

### Hypothesis 2: Weekend commits more experimental
- **Expected:** Higher feat ratio without deadline pressure
- **Result:** Weekend feat 11.1% vs. weekday 17.0% (opposite!)
- **Status:** REJECTED

### Implication for Prompts
```
✅ Trust empirical data over intuition
✅ Test assumptions before encoding them
❌ Don't assume nocturnal = more thoughtful
❌ Don't assume weekends = experimental
```

---

## Synthesized Profile for AI Interactions

Based on DMMF analysis, optimal AI interaction should:

### 1. Structure
- Present information hierarchically
- Maintain clear conceptual boundaries
- Support modular thinking

### 2. Quality
- Never suggest shipping without tests
- Acknowledge quality as emotional, not just technical
- Match tone to task type

### 3. Values
- Connect work to broader purpose
- Acknowledge ethical dimensions
- Respect Brazilian cultural context

### 4. Process
- Expect and support iteration
- Don't present solutions as final
- Balance reflection-in-action with reflection-on-action

---

## Connection to Prompt Engineering

This profile directly informs:

| DMMF Dimension | Prompt Engineering Application |
|----------------|-------------------------------|
| Cognitive | Structure of responses, information hierarchy |
| Affective | Tone calibration, quality emphasis |
| Conative | Value alignment, purpose connection |
| Reflective | Iteration support, refinement cycles |

---

## Evidence Quality

- **Methodology:** Mixed-methods (MSR + Thematic Analysis + Autoethnography)
- **Sample Size:** 2,799 commits across 40 repositories
- **Time Span:** ~3 years of development
- **Validation:** Quantitative anchoring with qualitative interpretation
- **Limitations:** Single subject (N=1), requires external validation

---

*Reference: Silva, A.H. (2025). "From Commits to Cognition: A Mixed-Methods Framework for Inferring Developer Mental Models from Repository Artifacts"*
