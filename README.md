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
cyborg/
├── main.tex                    # Main LaTeX document (sigconf format)
├── main-dis.tex                # DIS 2026 submission (single-column, anonymous)
├── references.bib              # Bibliography
├── references-anon.bib         # Anonymous bibliography for review
├── sections/                   # Paper sections
│   ├── 01-introduction-anon.tex
│   ├── 02-related-work-anon.tex
│   ├── 03-methodology-anon.tex
│   ├── 04-findings.tex
│   ├── 05-discussion-anon.tex
│   ├── 06-conclusion-anon.tex
│   └── appendix-anon.tex
├── figures/                    # Visualizations
│   ├── heatmap_*.png           # Analysis heatmaps
│   └── fig*_*.png              # Paper figures
├── scripts/                    # Analysis scripts
│   ├── analyze_sessions.py
│   ├── analyze_devgpt.py
│   ├── analyze_anthropic.py
│   ├── create_heatmaps.py
│   └── advanced_analysis.py
├── data/                       # Aggregate statistics (no PII)
│   ├── aggregate_report.json
│   └── advanced_analysis.json
└── submission/                 # Submission-ready packages
    └── zenodo/
        ├── Cyborg-Developer-DaSilvaAnderson-Preprint.pdf
        ├── cyborg-developer-preprint.tex
        ├── references.bib
        └── zenodo-metadata.json
```

## Preprint

The Zenodo preprint (27 pages) is available at `submission/zenodo/Cyborg-Developer-DaSilvaAnderson-Preprint.pdf`.

This paper extends the **Developer Mental Model Framework (DMMF)**:
- **DMMF**: Analyzes *what* cognitive patterns produce artifacts (historical commits)
- **Cyborg Developer**: Analyzes *how* cognitive work is distributed (real-time interactions)

See: [Da Silva (2025). From Commits to Cognition. Zenodo. doi:10.5281/zenodo.18012186](https://doi.org/10.5281/zenodo.18012186)

## Data Availability

**Included in this repository:**
- Aggregate statistics and analysis results
- Analysis scripts for reproducibility
- All figures and tables

**Not included (privacy):**
- Raw interaction logs (contain project code and personal context)
- Screenshots
- Anthropic data export

**External datasets referenced:**
- [DevGPT Dataset](https://github.com/NAIST-SE/DevGPT) (MSR 2024)

## Building the Paper

```bash
# DIS 2026 version (anonymous, single-column)
pdflatex main-dis.tex
bibtex main-dis
pdflatex main-dis.tex
pdflatex main-dis.tex

# Preprint version
cd submission/zenodo
pdflatex cyborg-developer-preprint.tex
bibtex cyborg-developer-preprint
pdflatex cyborg-developer-preprint.tex
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
