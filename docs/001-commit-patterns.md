# Evidence: Commit Message Patterns

**Source:** GitHub repository analysis
**Date Collected:** 2025-12-30
**Repositories Analyzed:** cidadao.ai-backend (200 commits), telepatia (100 commits)

---

## Summary

Anderson follows **Conventional Commits** specification consistently across projects, with clear patterns in type distribution and scope organization.

---

## Quantitative Analysis

### Cidadão.AI Backend (200 commits)

| Type | Count | Percentage |
|------|-------|------------|
| fix | 68 | 34% |
| feat | 57 | 28.5% |
| docs | 38 | 19% |
| refactor | 18 | 9% |
| test | 10 | 5% |
| ci | 3 | 1.5% |
| chore | 3 | 1.5% |
| security | 1 | 0.5% |
| style | 1 | 0.5% |
| release | 1 | 0.5% |

**Top Scopes:**
1. `(agents)` - 39 commits (core domain)
2. `(chat)` - 22 commits
3. `(tests)` - 10 commits
4. `(api)` - 4 commits
5. `(investigations)` - 4 commits

### Telepatia (100 commits)

| Type | Count | Percentage |
|------|-------|------------|
| feat | 36 | 36% |
| fix | 28 | 28% |
| docs | 14 | 14% |
| refactor | 8 | 8% |
| chore | 7 | 7% |
| ci | 2 | 2% |

---

## Identified Patterns

### 1. Fix-First Development
- Higher `fix` ratio in mature projects (cidadao.ai: 34%)
- Lower `fix` ratio in newer projects (telepatia: 28%)
- **Implication:** Development cycle involves rapid iteration with continuous bug fixing

### 2. Documentation Integration
- Consistent 14-19% of commits are documentation
- Documentation treated as first-class citizen, not afterthought
- **Implication:** Technical writing is integral part of workflow

### 3. Domain-Driven Scoping
- Scopes reflect domain concepts (`agents`, `chat`, `investigations`)
- Not infrastructure-focused (`db`, `api`, `config`)
- **Implication:** Commits organized around business value, not technical layers

### 4. Refactoring Discipline
- 8-9% of commits are pure refactoring
- Separated from feature development
- **Implication:** Technical debt is actively managed, not accumulated

### 5. Testing as Explicit Activity
- 5% dedicated test commits in cidadao.ai
- Tests often bundled with features
- **Implication:** Testing is conscious decision, not automatic

---

## Effective Commit Examples

### Feature Commits
```
feat(monitoring): implement Grafana Cloud remote write integration
feat(auth): implement proper API key validation
feat(ui): add CookieBanner component for LGPD consent
```

**Pattern:** `feat(scope): imperative action + clear outcome`

### Fix Commits
```
fix(chat): route zumbi target to DB persistence path
fix(investigations): convert timezone-aware datetime to naive for PostgreSQL
fix(ci): resolve GitHub Actions workflow failures
```

**Pattern:** `fix(scope): specific action addressing specific problem`

### Documentation Commits
```
docs(readme): update commit count to 1,229+
docs(planning): add medical feedback system architecture for RLHF
docs(architecture): add mermaid diagrams with interactive viewer
```

**Pattern:** `docs(target): action + what was documented`

---

## Antipatterns Avoided

1. **No vague commits:** Never "fix bug" or "update code"
2. **No WIP commits:** Commits are atomic and complete
3. **No tool mentions:** No AI/Claude references in messages
4. **No multi-purpose commits:** Each commit has single purpose

---

## Recommendations for Prompt Engineering

### When Asking for Commits
```
✅ "Commit this change following conventional commits, scope: agents"
✅ "Create a fix commit for the datetime issue"
❌ "Commit the changes"
❌ "Make a commit"
```

### When Reviewing Work
- Expect domain-focused scopes
- Expect imperative mood
- Expect 60-char limit on summary
- Expect English, professional tone

---

## Evidence Quality

- **Sample Size:** 300 commits across 2 major projects
- **Time Span:** ~6 months of active development
- **Confidence:** High - patterns are consistent
- **Update Frequency:** Re-analyze quarterly

---

*Next Analysis: Include contributions/ repositories for open-source pattern comparison*
