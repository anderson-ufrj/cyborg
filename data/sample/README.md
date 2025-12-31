# Sample Data

This folder contains anonymized sample data to demonstrate the data structure
and enable reproducibility of the analysis pipeline.

## Structure

```
sample/
├── sessions/           # Individual interaction session metrics
│   └── example_session.json
├── aggregated/         # Aggregated analysis results
│   └── example_analysis.json
└── README.md
```

## Data Schema

### Session Data (`sessions/*.json`)

| Field | Type | Description |
|-------|------|-------------|
| timestamp | ISO 8601 | Session timestamp |
| prompt_tokens | int | Input token count |
| response_tokens | int | Output token count |
| response_time_ms | int | Response latency in ms |
| quality_score | float | Quality metric (0-1) |
| iteration_count | int | Number of refinement iterations |
| context_used | array | Active context modules |
| pattern_applied | string | Interaction pattern used |
| success_indicators | array | Success metrics achieved |

### Aggregated Data (`aggregated/*.json`)

Contains statistical summaries across multiple sessions.

## Privacy Note

Real session data is stored locally in `data/01_processed/` and `data/02_aggregated/`
but is NOT committed to version control to protect privacy.

Only this sample data is included in the repository for reproducibility.
