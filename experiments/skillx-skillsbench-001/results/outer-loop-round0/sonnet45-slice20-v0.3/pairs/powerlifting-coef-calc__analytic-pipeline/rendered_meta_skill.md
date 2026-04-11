[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: analytic-pipeline
Semantic intent: Run an ordered analysis pipeline where intermediate processing quality strongly affects final correctness.
Emphasize:
- stage decomposition and stage ordering
- explicit intermediate artifacts / checkpoints
- handoff integrity between stages
- final output tied back to pipeline evidence
Avoid:
- collapsing multiple sensitive transforms into one vague step
- skipping intermediate validation
- overly generic prose-only guidance
Expected good fit:
- scientific / signal / video / security analysis workflows
- ordered transformation + measurement tasks
Expected bad fit:
- simple one-shot artifact tasks
- pure code patch / compile-test loops
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for an analytic-pipeline task.
Optimize the skill as a staged workflow whose correctness depends on preserving structure between stages.

Prioritize:
1. stage-by-stage decomposition,
2. explicit intermediate artifacts or checks when a later step depends on earlier processing quality,
3. clear handoff rules between extraction, transformation, analysis, and final reporting,
4. a final output step that summarizes the pipeline result without dropping critical constraints.

Strengthen stage contracts before adding more generic scaffolding.
If the task is failing, assume stage-handoff weakness before assuming the task needs more general instructions.

[Task context block]
Task name: powerlifting-coef-calc
Task summary: You need to calculate the lifting scores for International Powerlifting Federation competitions in the file `/root/data/openipf.xlsx`. The workbook contains two sheets:
Task constraints:
- seed schema prior: artifact-generation
- verifier mode: deterministic-artifact-plus-stage-check
- workflow topology: staged-multi-step
- tool surface regime: tool-medium
- primary pattern: pipeline
- annotation confidence: high
- secondary patterns: generator, reviewer
Task output requirements:
- verifier note: deterministic-artifact-plus-stage-check
- current skill count: 3

[Current Task skill block]
Current Task skill:
## powerlifting
---
name: powerlifting
description: "Calculating powerlifting scores to determine the performance of lifters across different weight classes. "
---

# Calculating Powerlifting Scores as a Professional Coach

## Dynamic Objective Team Scoring (Dots)

In the world of powerlifting, comparing lifters across different body weights is essential to /determine relative strength and fairness in competition. This is where the **DOTS score**—short for “Dynamic Objective Team Scoring”—comes into play. It’s a widely-used formula that helps level the playing field by standardizing performances regardless of a lifter’s body weight. Whether you’re new to powerlifting or a seasoned competitor, understanding the DOTS score is crucial for evaluating progress and competing effectively.
This section is from [powerliftpro](https://powerliftpro.app/understanding-the-dots-score-in-powerlifting-a-comprehensive-guide/).


### What is the DOTS Score?

The DOTS score is a mathematical formula used to normalize powerlifting totals based on a lifter’s body weight. It provides a single number that represents a lifter’s relative strength, allowing for fair comparisons across all weight classes.

The score takes into account:

- **The lifter's total:** The combined weight lifted in the [squat](https://powerliftpro.app/exercises/low-bar-squat/), [bench press](https://powerliftpro.app/exercises/comp-bench-press/), and [deadlift](https://powerliftpro.app/exercises/conventional-deadlift/).
- **Body weight:** The lifter’s weight on competition day.

### The DOTS Formula

For real powerlifting nerds who want to calculate their DOTS longhand (remember to show all work! sorry, old math class joke), the DOTS formula is as follows:

DOTS Score=Total Weight Lifted (kg)×a+b(BW)+c(BW2)+d(BW3)+e(BW4)500

Here:

- **Total Weight Lifted (kg):** Your combined total from the squat, bench press, and deadlift.
- **BW:** Your body weight in kilograms.
- **a, b, c, d, e:** Coefficients derived from statistical modeling to ensure accurate scaling across various body weights.

These coefficients are carefully designed to balance the advantage heavier lifters might have in absolute strength and the lighter lifters’ advantage in relative strength.

```rust
use crate::poly4;
use opltypes::*;

pub fn dots_coefficient_men(bodyweightkg: f64) -> f64 {
    const A: f64 = -0.0000010930;
    const B: f64 = 0.0007391293;
    const C: f64 = -0.1918759221;
    const D: f64 = 24.0900756;
    const E: f64 = -307.75076;

    // Bodyweight bounds are defined; bodyweights out of range match the boundaries.
    let adjusted = bodyweightkg.clamp(40.0, 210.0);
    500.0 / poly4(A, B, C, D, E, adjusted)
}

pub fn dots_coefficient_women(bodyweightkg: f64) -> f64 {
    const A: f64 = -0.0000010706;
    const B: f64 = 0.0005158568;
    const C: f64 = -0.1126655495;
    const D: f64 = 13.6175032;
    const E: f64 = -57.96288;

    // Bodyweight bounds are defined; bodyweights out of range match the boundaries.
    let adjusted = bodyweightkg.clamp(40.0, 150.0);
    500.0 / poly4(A, B, C, D, E, adjusted)
}

/// Calculates Dots points.
///
/// Dots were introduced by the German IPF Affiliate BVDK after the IPF switched to
/// IPF Points, which do not allow comparing between sexes. The BVDK hosts team
/// competitions that allow lifters of all sexes to compete on a singular team.
///
/// Since Wilks points have been ostracized from the IPF, and IPF Points are
/// unsuitable, German lifters therefore came up with their own formula.
///
/// The author of the Dots formula is Tim Konertz <tim.konertz@outlook.com>.
///
/// Tim says that Dots is an acronym for "Dynamic Objective Team Scoring,"
/// but that they chose the acronym before figuring out the expansion.
pub fn dots(sex: Sex, bodyweight: WeightKg, total: WeightKg) -> Points {
    if bodyweight.is_zero() || total.is_zero() {
        return Points::from_i32(0);
    }
    let coefficient: f64 = match sex {
        Sex::M | Sex::Mx => dots_coefficient_men(f64::from(bodyweight)),
        Sex::F => dots_coefficient_women(f64::from(bodyweight)),
    };
    Points::from(coefficient * f64::from(total))
}
```

## IPF Good Lift Coefficient

The **IPF Good Lift Coefficient** calculator computes the comparative weight coefficient between weight lifters based on the weight of the lifter (x), the type of lift and the gender of the lifter, all combined in the IPF GL Coefficient formula. Information about this is from [IPF](https://www.powerlifting.sport/fileadmin/ipf/data/ipf-formula/IPF_GL_Coefficients-2020.pdf).

**INSTRUCTIONS:** Choose units and enter the following:

- (**x**)  Weigh of Person
- (**g**) Gender of Person
- (LT) lift type
  - Equipped Power Lift
  - Classic Power Lift
  - Equipped Bench Press
  - Classic Bench Press

**IPFL GL Coefficient (IPC):** The calculator returns the coefficient as a real number (decimal).

### The Math / Science

The International Powerlifting Federation GL coefficient formula is:

  IPC=100A−B⋅e−C⋅BWT

where:

- IPC = IPF GL coefficient
- BWT = body weight of the lifter
- A, B, C = f(gender, lift type), see below



```rust
use opltypes::*;

/// Hardcoded formula parameters: `(A, B, C)`.
type Parameters = (f64, f64, f64);

/// Gets formula parameters from what is effectively a lookup table.
fn parameters(sex: Sex, equipment: Equipment, event: Event) -> Parameters {
    // Since the formula was made for the IPF, it only covers Raw and Single-ply.
    // We do our best and just reuse those for Wraps and Multi-ply, respectively.
    let equipment = match equipment {
        Equipment::Raw | Equipment::Wraps | Equipment::Straps => Equipment::Raw,
        Equipment::Single | Equipment::Multi | Equipment::Unlimited => Equipment::Single,
    };

    // Points are only specified for Sex::M and Sex::F.
    let dichotomous_sex = match sex {
        Sex::M | Sex::Mx => Sex::M,
        Sex::F => Sex::F,
    };

    const SBD: Event = Event::sbd();
    const B: Event = Event::b();

    match (event, dichotomous_sex, equipment) {
        (SBD, Sex::M, Equipment::Raw) => (1199.72839, 1025.18162, 0.009210),
        (SBD, Sex::M, Equipment::Single) => (1236.25115, 1449.21864, 0.01644),
        (SBD, Sex::F, Equipment::Raw) => (610.32796, 1045.59282, 0.03048),
        (SBD, Sex::F, Equipment::Single) => (758.63878, 949.31382, 0.02435),

        (B, Sex::M, Equipment::Raw) => (320.98041, 281.40258, 0.01008),
        (B, Sex::M, Equipment::Single) => (381.22073, 733.79378, 0.02398),
        (B, Sex::F, Equipment::Raw) => (142.40398, 442.52671, 0.04724),
        (B, Sex::F, Equipment::Single) => (221.82209, 357.00377, 0.02937),

        _ => (0.0, 0.0, 0.0),
    }
}

/// Calculates IPF GOODLIFT Points.
pub fn goodlift(
    sex: Sex,
    equipment: Equipment,
    event: Event,
    bodyweight: WeightKg,
    total: WeightKg,
) -> Points {
    // Look up parameters.
    let (a, b, c) = parameters(sex, equipment, event);

    // Exit early for undefined cases.
    if a == 0.0 || bodyweight < WeightKg::from_i32(35) || total.is_zero() {
        return Points::from_i32(0);
    }

    // A - B * e^(-C * Bwt).
    let e_pow = (-c * f64::from(bodyweight)).exp();
    let denominator = a - (b * e_pow);

    // Prevent division by zero.
    if denominator == 0.0 {
        return Points::from_i32(0);
    }

    // Calculate GOODLIFT points.
    // We add the requirement that the value be non-negative.
    let points: f64 = f64::from(total) * (0.0_f64).max(100.0 / denominator);
    Points::from(points)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn published_examples() {
        // Dmitry Inzarkin from 2019 IPF World Open Men's Championships.
        let weight = WeightKg::from_f32(92.04);
        let total = WeightKg::from_f32(1035.0);
        assert_eq!(
            goodlift(Sex::M, Equipment::Single, Event::sbd(), weight, total),
            Points::from(112.85)
        );

        // Susanna Torronen from 2019 World Open Classic Bench Press Championships.
        let weight = WeightKg::from_f32(70.50);
        let total = WeightKg::from_f32(122.5);
        assert_eq!(
            goodlift(Sex::F, Equipment::Raw, Event::b(), weight, total),
            Points::from(96.78)
        );
    }
}
```

## Wilks coefficient

The following [equation](https://en.wikipedia.org/wiki/Equation) is used to calculate the Wilks coefficient:
$$
\text{Coef} = \frac{500}{a + bx + cx^2 + dx^3 + ex^4 + fx^5}
$$
where $x$ is the body weightof the lifter in kilograms.

The total weight lifted (in kg) is multiplied by the coefficient to find the standard amount lifted, normalised across all body weights.

|      |     *Men*      |     *Women*     |
| :--: | :------------: | :-------------: |
| *a*  |  -216.0475144  | 594.31747775582 |
| *b*  |   16.2606339   | −27.23842536447 |
| *c*  |  -0.002388645  |  0.82112226871  |
| *d*  |  -0.00113732   | −0.00930733913  |
| *e*  | 7.01863 × 10−6 | 4.731582 × 10−5 |
| *f*  | −1.291 × 10−8  |  −9.054 × 10−8  |



```rust
use crate::poly5;
use opltypes::*;

pub fn wilks_coefficient_men(bodyweightkg: f64) -> f64 {
    // Wilks defines its polynomial backwards:
    // A + Bx + Cx^2 + ...
    const A: f64 = -216.0475144;
    const B: f64 = 16.2606339;
    const C: f64 = -0.002388645;
    const D: f64 = -0.00113732;
    const E: f64 = 7.01863E-06;
    const F: f64 = -1.291E-08;

    // Upper bound avoids asymptote.
    // Lower bound avoids children with huge coefficients.
    let adjusted = bodyweightkg.clamp(40.0, 201.9);

    500.0 / poly5(F, E, D, C, B, A, adjusted)
}

pub fn wilks_coefficient_women(bodyweightkg: f64) -> f64 {
    const A: f64 = 594.31747775582;
    const B: f64 = -27.23842536447;
    const C: f64 = 0.82112226871;
    const D: f64 = -0.00930733913;
    const E: f64 = 0.00004731582;
    const F: f64 = -0.00000009054;

    // Upper bound avoids asymptote.
    // Lower bound avoids children with huge coefficients.
    let adjusted = bodyweightkg.clamp(26.51, 154.53);

    500.0 / poly5(F, E, D, C, B, A, adjusted)
}

/// Calculates Wilks points.
pub fn wilks(sex: Sex, bodyweight: WeightKg, total: WeightKg) -> Points {
    if bodyweight.is_zero() || total.is_zero() {
        return Points::from_i32(0);
    }
    let coefficient: f64 = match sex {
        Sex::M | Sex::Mx => wilks_coefficient_men(f64::from(bodyweight)),
        Sex::F => wilks_coefficient_women(f64::from(bodyweight)),
    };
    Points::from(coefficient * f64::from(total))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn coefficients() {
        // Coefficients taken verbatim from the old Python implementation.
        assert_eq!(wilks_coefficient_men(100.0), 0.6085890719066511);
        assert_eq!(wilks_coefficient_women(100.0), 0.8325833167368228);
    }

    #[test]
    fn points() {
        // Point values taken (rounded) from the old Python implementation.
        assert_eq!(
            wilks(Sex::M, WeightKg::from_i32(100), WeightKg::from_i32(1000)),
            Points::from(608.58907)
        );
        assert_eq!(
            wilks(Sex::F, WeightKg::from_i32(60), WeightKg::from_i32(500)),
            Points::from(557.4434)
        );
    }
}
```

## Glossbrenner

When Powerlifting began having 'masters', it quickly became apparent that some sort of age allowance or 'handicap' was needed by this group to sort them out, one from another. How much better must a 40-yr-old be, than a 50-yr-old, to be considered a better lifter? How much better than a 55-yr-old, a 60-yr-old, etc? So, a set of age multipliers, or 'handicap numbers', was issued for Master Lifters year-by-year, from 40 through 80. Since then, however, the number of Master Lifters in the 50+ and 60+ group has become so large that a revision (based on extensive study and years of backup data) was needed. These new numbers are based on comparison of the totals of actual lifters over the past seven years, and a chart for their usage is on the final page of this [section](https://worldpowerliftingcongress.com/wp-content/uploads/2015/02/Glossbrenner.htm).

The formula is: (LT) times (GBC) = (PN)

LT  - Lifter's Total
GBC – Glossbrenner Bodyweight Coefficient *
PN  - Product Number

```rust
use opltypes::*;

use crate::schwartzmalone::{malone_coefficient, schwartz_coefficient};
use crate::wilks::{wilks_coefficient_men, wilks_coefficient_women};

fn glossbrenner_coefficient_men(bodyweightkg: f64) -> f64 {
    // Glossbrenner is defined piecewise.
    if bodyweightkg < 153.05 {
        (schwartz_coefficient(bodyweightkg) + wilks_coefficient_men(bodyweightkg)) / 2.0
    } else {
        // Linear coefficients found by fitting to a table.
        const A: f64 = -0.000821668402557;
        const B: f64 = 0.676940740094416;
        (schwartz_coefficient(bodyweightkg) + A * bodyweightkg + B) / 2.0
    }
}

fn glossbrenner_coefficient_women(bodyweightkg: f64) -> f64 {
    // Glossbrenner is defined piecewise.
    if bodyweightkg < 106.3 {
        (malone_coefficient(bodyweightkg) + wilks_coefficient_women(bodyweightkg)) / 2.0
    } else {
        // Linear coefficients found by fitting to a table.
        const A: f64 = -0.000313738002024;
        const B: f64 = 0.852664892884785;
        (malone_coefficient(bodyweightkg) + A * bodyweightkg + B) / 2.0
    }
}

/// Calculates Glossbrenner points.
///
/// Glossbrenner is the average of two older systems, Schwartz-Malone and Wilks,
/// with a piecewise linear section.
///
/// This points system is most often used by GPC affiliates.
pub fn glossbrenner(sex: Sex, bodyweight: WeightKg, total: WeightKg) -> Points {
    if bodyweight.is_zero() || total.is_zero() {
        return Points::from_i32(0);
    }
    let coefficient: f64 = match sex {
        Sex::M | Sex::Mx => glossbrenner_coefficient_men(f64::from(bodyweight)),
        Sex::F => glossbrenner_coefficient_women(f64::from(bodyweight)),
    };
    Points::from(coefficient * f64::from(total))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn coefficients() {
        // Coefficients taken verbatim from the old Python implementation.
        assert_eq!(glossbrenner_coefficient_men(100.0), 0.5812707859533183);
        assert_eq!(glossbrenner_coefficient_women(100.0), 0.7152488066040259);
    }

    #[test]
    fn points() {
        // Point values taken (rounded) from the old Python implementation.
        assert_eq!(
            glossbrenner(Sex::M, WeightKg::from_i32(100), WeightKg::from_i32(1000)),
            Points::from(581.27)
        );
        assert_eq!(
            glossbrenner(Sex::F, WeightKg::from_i32(60), WeightKg::from_i32(500)),
            Points::from(492.53032)
        );

        // Zero bodyweight should be treated as "unknown bodyweight".
        assert_eq!(
            glossbrenner(Sex::M, WeightKg::from_i32(0), WeightKg::from_i32(500)),
            Points::from_i32(0)
        );
    }
}
```

## senior-data-scientist
---
name: senior-data-scientist
description: World-class data science skill for statistical modeling, experimentation, causal inference, and advanced analytics. Expertise in Python (NumPy, Pandas, Scikit-learn), R, SQL, statistical methods, A/B testing, time series, and business intelligence. Includes experiment design, feature engineering, model evaluation, and stakeholder communication. Use when designing experiments, building predictive models, performing causal analysis, or driving data-driven decisions.
---

# Senior Data Scientist

World-class senior data scientist skill for production-grade AI/ML/Data systems.

## Quick Start

### Main Capabilities

```bash
# Core Tool 1
python scripts/experiment_designer.py --input data/ --output results/

# Core Tool 2  
python scripts/feature_engineering_pipeline.py --target project/ --analyze

# Core Tool 3
python scripts/model_evaluation_suite.py --config config.yaml --deploy
```

## Core Expertise

This skill covers world-class capabilities in:

- Advanced production patterns and architectures
- Scalable system design and implementation
- Performance optimization at scale
- MLOps and DataOps best practices
- Real-time processing and inference
- Distributed computing frameworks
- Model deployment and monitoring
- Security and compliance
- Cost optimization
- Team leadership and mentoring

## Tech Stack

**Languages:** Python, SQL, R, Scala, Go
**ML Frameworks:** PyTorch, TensorFlow, Scikit-learn, XGBoost
**Data Tools:** Spark, Airflow, dbt, Kafka, Databricks
**LLM Frameworks:** LangChain, LlamaIndex, DSPy
**Deployment:** Docker, Kubernetes, AWS/GCP/Azure
**Monitoring:** MLflow, Weights & Biases, Prometheus
**Databases:** PostgreSQL, BigQuery, Snowflake, Pinecone

## Reference Documentation

### 1. Statistical Methods Advanced

Comprehensive guide available in `references/statistical_methods_advanced.md` covering:

- Advanced patterns and best practices
- Production implementation strategies
- Performance optimization techniques
- Scalability considerations
- Security and compliance
- Real-world case studies

### 2. Experiment Design Frameworks

Complete workflow documentation in `references/experiment_design_frameworks.md` including:

- Step-by-step processes
- Architecture design patterns
- Tool integration guides
- Performance tuning strategies
- Troubleshooting procedures

### 3. Feature Engineering Patterns

Technical reference guide in `references/feature_engineering_patterns.md` with:

- System design principles
- Implementation examples
- Configuration best practices
- Deployment strategies
- Monitoring and observability

## Production Patterns

### Pattern 1: Scalable Data Processing

Enterprise-scale data processing with distributed computing:

- Horizontal scaling architecture
- Fault-tolerant design
- Real-time and batch processing
- Data quality validation
- Performance monitoring

### Pattern 2: ML Model Deployment

Production ML system with high availability:

- Model serving with low latency
- A/B testing infrastructure
- Feature store integration
- Model monitoring and drift detection
- Automated retraining pipelines

### Pattern 3: Real-Time Inference

High-throughput inference system:

- Batching and caching strategies
- Load balancing
- Auto-scaling
- Latency optimization
- Cost optimization

## Best Practices

### Development

- Test-driven development
- Code reviews and pair programming
- Documentation as code
- Version control everything
- Continuous integration

### Production

- Monitor everything critical
- Automate deployments
- Feature flags for releases
- Canary deployments
- Comprehensive logging

### Team Leadership

- Mentor junior engineers
- Drive technical decisions
- Establish coding standards
- Foster learning culture
- Cross-functional collaboration

## Performance Targets

**Latency:**
- P50: < 50ms
- P95: < 100ms
- P99: < 200ms

**Throughput:**
- Requests/second: > 1000
- Concurrent users: > 10,000

**Availability:**
- Uptime: 99.9%
- Error rate: < 0.1%

## Security & Compliance

- Authentication & authorization
- Data encryption (at rest & in transit)
- PII handling and anonymization
- GDPR/CCPA compliance
- Regular security audits
- Vulnerability management

## Common Commands

```bash
# Development
python -m pytest tests/ -v --cov
python -m black src/
python -m pylint src/

# Training
python scripts/train.py --config prod.yaml
python scripts/evaluate.py --model best.pth

# Deployment
docker build -t service:v1 .
kubectl apply -f k8s/
helm upgrade service ./charts/

# Monitoring
kubectl logs -f deployment/service
python scripts/health_check.py
```

## Resources

- Advanced Patterns: `references/statistical_methods_advanced.md`
- Implementation Guide: `references/experiment_design_frameworks.md`
- Technical Reference: `references/feature_engineering_patterns.md`
- Automation Scripts: `scripts/` directory

## Senior-Level Responsibilities

As a world-class senior professional:

1. **Technical Leadership**
   - Drive architectural decisions
   - Mentor team members
   - Establish best practices
   - Ensure code quality

2. **Strategic Thinking**
   - Align with business goals
   - Evaluate trade-offs
   - Plan for scale
   - Manage technical debt

3. **Collaboration**
   - Work across teams
   - Communicate effectively
   - Build consensus
   - Share knowledge

4. **Innovation**
   - Stay current with research
   - Experiment with new approaches
   - Contribute to community
   - Drive continuous improvement

5. **Production Excellence**
   - Ensure high availability
   - Monitor proactively
   - Optimize performance
   - Respond to incidents

## xlsx
---
name: xlsx
description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. When Claude needs to work with spreadsheets (.xlsx, .xlsm, .csv, .tsv, etc) for: (1) Creating new spreadsheets with formulas and formatting, (2) Reading or analyzing data, (3) Modify existing spreadsheets while preserving formulas, (4) Data analysis and visualization in spreadsheets, or (5) Recalculating formulas"
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel files

### Zero Formula Errors
- Every Excel model MUST be delivered with ZERO formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates (when updating templates)
- Study and EXACTLY match existing format, style, and conventions when modifying files
- Never impose standardized formatting on files with established patterns
- Existing template conventions ALWAYS override these guidelines

## Financial models

### Color Coding Standards
Unless otherwise stated by the user or existing template

#### Industry-Standard Color Conventions
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, and numbers users will change for scenarios
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links pulling from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention or cells that need to be updated

### Number Formatting Standards

#### Required Format Rules
- **Years**: Format as text strings (e.g., "2024" not "2,024")
- **Currency**: Use $#,##0 format; ALWAYS specify units in headers ("Revenue ($mm)")
- **Zeros**: Use number formatting to make all zeros "-", including percentages (e.g., "$#,##0;($#,##0);-")
- **Percentages**: Default to 0.0% format (one decimal)
- **Multiples**: Format as 0.0x for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses (123) not minus -123

### Formula Construction Rules

#### Assumptions Placement
- Place ALL assumptions (growth rates, margins, multiples, etc.) in separate assumption cells
- Use cell references instead of hardcoded values in formulas
- Example: Use =B5*(1+$B$6) instead of =B5*1.05

#### Formula Error Prevention
- Verify all cell references are correct
- Check for off-by-one errors in ranges
- Ensure consistent formulas across all projection periods
- Test with edge cases (zero values, negative numbers)
- Verify no unintended circular references

#### Documentation Requirements for Hardcodes
- Comment or in cells beside (if end of table). Format: "Source: [System/Document], [Date], [Specific Reference], [URL if applicable]"
- Examples:
  - "Source: Company 10-K, FY2024, Page 45, Revenue Note, [SEC EDGAR URL]"
  - "Source: Company 10-Q, Q2 2025, Exhibit 99.1, [SEC EDGAR URL]"
  - "Source: Bloomberg Terminal, 8/15/2025, AAPL US Equity"
  - "Source: FactSet, 8/20/2025, Consensus Estimates Screen"

# XLSX creation, editing, and analysis

## Overview

A user may ask you to create, edit, or analyze the contents of an .xlsx file. You have different tools and workflows available for different tasks.

## Important Requirements

**LibreOffice Required for Formula Recalculation**: You can assume LibreOffice is installed for recalculating formula values using the `recalc.py` script. The script automatically configures LibreOffice on first run

## Reading and analyzing data

### Data analysis with pandas
For data analysis, visualization, and basic operations, use **pandas** which provides powerful data manipulation capabilities:

```python
import pandas as pd

# Read Excel
df = pd.read_excel('file.xlsx')  # Default: first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # All sheets as dict

# Analyze
df.head()      # Preview data
df.info()      # Column info
df.describe()  # Statistics

# Write Excel
df.to_excel('output.xlsx', index=False)
```

## Excel File Workflows

## CRITICAL: Use Formulas, Not Hardcoded Values

**Always use Excel formulas instead of calculating values in Python and hardcoding them.** This ensures the spreadsheet remains dynamic and updateable.

### ❌ WRONG - Hardcoding Calculated Values
```python
# Bad: Calculating in Python and hardcoding result
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000

# Bad: Computing growth rate in Python
growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
sheet['C5'] = growth  # Hardcodes 0.15

# Bad: Python calculation for average
avg = sum(values) / len(values)
sheet['D20'] = avg  # Hardcodes 42.5
```

### ✅ CORRECT - Using Excel Formulas
```python
# Good: Let Excel calculate the sum
sheet['B10'] = '=SUM(B2:B9)'

# Good: Growth rate as Excel formula
sheet['C5'] = '=(C4-C2)/C2'

# Good: Average using Excel function
sheet['D20'] = '=AVERAGE(D2:D19)'
```

This applies to ALL calculations - totals, percentages, ratios, differences, etc. The spreadsheet should be able to recalculate when source data changes.

## Common Workflow
1. **Choose tool**: pandas for data, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas (MANDATORY IF USING FORMULAS)**: Use the recalc.py script
   ```bash
   python recalc.py output.xlsx
   ```
6. **Verify and fix any errors**:
   - The script returns JSON with error details
   - If `status` is `errors_found`, check `error_summary` for specific error types and locations
   - Fix the identified errors and recalculate again
   - Common errors to fix:
     - `#REF!`: Invalid cell references
     - `#DIV/0!`: Division by zero
     - `#VALUE!`: Wrong data type in formula
     - `#NAME?`: Unrecognized formula name

### Creating new Excel files

```python
# Using openpyxl for formulas and formatting
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# Add data
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])

# Add formula
sheet['B2'] = '=SUM(A1:A10)'

# Formatting
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# Column width
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

### Editing existing Excel files

```python
# Using openpyxl to preserve formulas and formatting
from openpyxl import load_workbook

# Load existing file
wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName'] for specific sheet

# Working with multiple sheets
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"Sheet: {sheet_name}")

# Modify cells
sheet['A1'] = 'New Value'
sheet.insert_rows(2)  # Insert row at position 2
sheet.delete_cols(3)  # Delete column 3

# Add new sheet
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## Recalculating formulas

Excel files created or modified by openpyxl contain formulas as strings but not calculated values. Use the provided `recalc.py` script to recalculate formulas:

```bash
python recalc.py <excel_file> [timeout_seconds]
```

Example:
```bash
python recalc.py output.xlsx 30
```

The script:
- Automatically sets up LibreOffice macro on first run
- Recalculates all formulas in all sheets
- Scans ALL cells for Excel errors (#REF!, #DIV/0!, etc.)
- Returns JSON with detailed error locations and counts
- Works on both Linux and macOS

## Formula Verification Checklist

Quick checks to ensure formulas work correctly:

### Essential Verification
- [ ] **Test 2-3 sample references**: Verify they pull correct values before building full model
- [ ] **Column mapping**: Confirm Excel columns match (e.g., column 64 = BL, not BK)
- [ ] **Row offset**: Remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)

### Common Pitfalls
- [ ] **NaN handling**: Check for null values with `pd.notna()`
- [ ] **Far-right columns**: FY data often in columns 50+
- [ ] **Multiple matches**: Search all occurrences, not just first
- [ ] **Division by zero**: Check denominators before using `/` in formulas (#DIV/0!)
- [ ] **Wrong references**: Verify all cell references point to intended cells (#REF!)
- [ ] **Cross-sheet references**: Use correct format (Sheet1!A1) for linking sheets

### Formula Testing Strategy
- [ ] **Start small**: Test formulas on 2-3 cells before applying broadly
- [ ] **Verify dependencies**: Check all cells referenced in formulas exist
- [ ] **Test edge cases**: Include zero, negative, and very large values

### Interpreting recalc.py Output
The script returns JSON with error details:
```json
{
  "status": "success",           // or "errors_found"
  "total_errors": 0,              // Total error count
  "total_formulas": 42,           // Number of formulas in file
  "error_summary": {              // Only present if errors found
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

## Best Practices

### Library Selection
- **pandas**: Best for data analysis, bulk operations, and simple data export
- **openpyxl**: Best for complex formatting, formulas, and Excel-specific features

### Working with openpyxl
- Cell indices are 1-based (row=1, column=1 refers to cell A1)
- Use `data_only=True` to read calculated values: `load_workbook('file.xlsx', data_only=True)`
- **Warning**: If opened with `data_only=True` and saved, formulas are replaced with values and permanently lost
- For large files: Use `read_only=True` for reading or `write_only=True` for writing
- Formulas are preserved but not evaluated - use recalc.py to update values

### Working with pandas
- Specify data types to avoid inference issues: `pd.read_excel('file.xlsx', dtype={'id': str})`
- For large files, read specific columns: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates properly: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## Code Style Guidelines
**IMPORTANT**: When generating Python code for Excel operations:
- Write minimal, concise Python code without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements

**For Excel files themselves**:
- Add comments to cells with complex formulas or important assumptions
- Document data sources for hardcoded values
- Include notes for key calculations and model sections

[Evidence block]
No Skills: `100`
With Skills: `100`
Delta: `0`
Failure summary: existing workbook must be extended in-place with selected columns and Excel formulas for TotalKg and Dots coefficients
Competing schema note: No prior round-0 pair evidence available.

[Output contract block]
Return YAML with fields:
revised_task_skill, change_summary{keep/add/remove/sharpen}, rationale

```yaml
revised_task_skill: |
  ...
change_summary:
  keep:
    - ...
  add:
    - ...
  remove:
    - ...
  sharpen:
    - ...
rationale: |
  ...
```
