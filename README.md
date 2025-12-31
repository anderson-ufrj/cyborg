# The Cyborg Developer

**Empirical Analysis of Cognitive Extension Through Human-AI Collaborative Programming**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18099559.svg)](https://doi.org/10.5281/zenodo.18099559)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Abstract

AI coding assistants are transforming software development, yet empirical understanding of how developers integrate these tools into cognitive workflows remains limited. Through computational autoethnography, we analyze 802 collaborative sessions (85,370 messages, 27,672 tool invocations) across 47 projects over 30 days.

**Key findings:**
- Cognitive delegation score of **0.71** indicates substantial offloading to AI
- Intentional model selection shows complex sessions averaging **7.59×** longer than routine sessions
- Tool usage hierarchy reveals AI primarily extends execution (36%) and exploration (33.5%)
- Sustained intensity (2,846 messages/day) suggests integrated partnership

We introduce **Cyborg Cognition**—the emergent cognitive system formed when developer mental processes integrate with AI capabilities through sustained collaboration.

## Repository Structure

```
cyborg-developer/
│
├── paper/                          # Manuscript
│   ├── main.tex                    # Main document (sigconf format)
│   ├── main-dis.tex                # DIS 2026 submission (anonymous)
│   ├── references.bib              # Bibliography
│   ├── sections/                   # Paper sections (.tex files)
│   └── figures/                    # Visualizations (.png, .pdf)
│
├── src/                            # Analysis code
│   ├── analysis/                   # Core analysis modules
│   │   ├── cyborg_developer_analysis.py    # Main analysis pipeline
│   │   ├── compute_weekly_delegation.py    # Weekly delegation scores
│   │   ├── extract_micro_examples.py       # Interaction pattern extraction
│   │   └── analyze_verification_patterns.py # Rejection/verification analysis
│   ├── metrics/                    # Metric calculation
│   │   └── interaction_analyzer.py
│   ├── import/                     # Data importers
│   │   └── history_importer.py     # Claude Code JSONL importer
│   ├── calibration/                # Calibration tools
│   ├── pipeline/                   # Data processing pipelines
│   ├── experiments/                # Experiment runners
│   └── versioning/                 # Version management
│
├── evidence/                       # Supporting evidence
│   ├── metrics/                    # Session metrics (535 files)
│   │   ├── data/                   # Individual session data
│   │   ├── historical/             # Aggregate reports
│   │   └── sessions/               # Session-level summaries
│   ├── analysis/                   # Analysis outputs
│   │   ├── verification_analysis.json
│   │   └── micro_examples/         # Extracted interaction patterns
│   └── patterns/                   # Pattern documentation
│
├── data/                           # Sample data
│   └── sample/                     # Anonymized examples
│
├── docs/                           # Documentation
│   ├── 001-commit-patterns.md
│   ├── 002-dmmf-cognitive-profile.md
│   ├── 003-anthropic-agent-patterns.md
│   └── 004-design-science-research-methodology.md
│
├── submission/                     # Publication files
│   └── zenodo/                     # Preprint
│       ├── Cyborg-Developer-DaSilvaAnderson-Preprint.pdf
│       └── zenodo-metadata.json
│
├── CITATION.cff                    # Citation metadata
├── LICENSE                         # CC BY 4.0 (paper) + MIT (code)
├── README.md                       # This file
└── requirements.txt                # Python dependencies
```

## Running the Analysis

### Prerequisites

```bash
pip install -r requirements.txt
```

### Import Claude Code History

```bash
# Import from ~/.claude/projects (default location)
python src/import/history_importer.py

# Import from custom location
python src/import/history_importer.py --source /path/to/projects --output evidence/metrics/historical
```

### Run Main Analysis

```bash
# Full analysis pipeline
python src/analysis/cyborg_developer_analysis.py

# Weekly delegation scores
python src/analysis/compute_weekly_delegation.py
```

### Extract Interaction Patterns

```bash
# Extract micro-level interaction examples (Execute-Explore-Modify cycles)
python src/analysis/extract_micro_examples.py

# Analyze verification/rejection patterns
python src/analysis/analyze_verification_patterns.py
```

### Generate Visualizations

```bash
python src/create_heatmaps.py
python src/create_enhanced_figures.py
```

## Preprint

The Zenodo preprint (27 pages) is available at `submission/zenodo/Cyborg-Developer-DaSilvaAnderson-Preprint.pdf`.

This paper extends the **Developer Mental Model Framework (DMMF)**:
- **DMMF**: Analyzes *what* cognitive patterns produce artifacts (historical commits)
- **Cyborg Developer**: Analyzes *how* cognitive work is distributed (real-time interactions)

See: [Da Silva (2025). From Commits to Cognition. Zenodo. doi:10.5281/zenodo.18012186](https://doi.org/10.5281/zenodo.18012186)

## Data Availability

**Included in this repository:**
- Session metrics (535 anonymized session files)
- Aggregate statistics and analysis results
- Analysis scripts for reproducibility
- All figures and tables

**Not included (privacy):**
- Raw interaction logs (contain project code and personal context)
- Screenshots
- Anthropic data export

## Building the Paper

```bash
# Main version (sigconf format)
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# DIS 2026 version (anonymous)
pdflatex main-dis.tex
bibtex main-dis
pdflatex main-dis.tex
pdflatex main-dis.tex

# Preprint version
cd submission/zenodo
pdflatex cyborg-developer-preprint.tex
bibtex cyborg-developer-preprint
pdflatex cyborg-developer-preprint.tex
```

## Citation

```bibtex
@misc{silva2025cyborg,
  title={The Cyborg Developer: Empirical Analysis of Cognitive Extension
         Through Human-AI Collaborative Programming},
  author={Da Silva, Anderson Henrique},
  year={2025},
  howpublished={Zenodo},
  doi={10.5281/zenodo.18099559},
  url={https://doi.org/10.5281/zenodo.18099559}
}
```

## License

- **Paper**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Code**: [MIT License](LICENSE)

## Author

**Anderson Henrique da Silva**
Independent Researcher
IFSULDEMINAS – Campus Muzambinho
Minas Gerais, Brazil
ORCID: [0009-0001-7144-4974](https://orcid.org/0009-0001-7144-4974)
GitHub: [anderson-ufrj](https://github.com/anderson-ufrj)
