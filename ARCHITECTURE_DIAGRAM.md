# SentinelCI Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         SentinelCI                               │
│                  Security Automation Platform                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │          CLI Interface (Typer)          │
        │  • Interactive Onboarding               │
        │  • Command Routing                      │
        │  • Rich Terminal UI                     │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌──────────────────┐                    ┌──────────────────┐
│  Code Scanning   │                    │ GitHub Integration│
│  • Secrets       │                    │  • Auth          │
│  • URLs          │                    │  • Discovery     │
│  • CVEs          │                    │  • Analysis      │
└──────────────────┘                    └──────────────────┘
        │                                           │
        └─────────────────────┬─────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │           Core Modules                   │
        │  ┌────────────────────────────────────┐ │
        │  │  auth.py                           │ │
        │  │  • PAT Management                  │ │
        │  │  • Validation                      │ │
        │  └────────────────────────────────────┘ │
        │  ┌────────────────────────────────────┐ │
        │  │  discovery.py                      │ │
        │  │  • Repository Fetching             │ │
        │  │  • Organization Scanning           │ │
        │  │  • Filtering                       │ │
        │  └────────────────────────────────────┘ │
        │  ┌────────────────────────────────────┐ │
        │  │  remediation.py                    │ │
        │  │  • PR Generation                   │ │
        │  │  • Issue Creation                  │ │
        │  │  • Branch Management               │ │
        │  └────────────────────────────────────┘ │
        │  ┌────────────────────────────────────┐ │
        │  │  visualization.py                  │ │
        │  │  • Incident Graphs                 │ │
        │  │  • Attack Chains                   │ │
        │  │  • Risk Heatmaps                   │ │
        │  └────────────────────────────────────┘ │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌──────────────────┐                    ┌──────────────────┐
│  AI Analysis     │                    │ Autonomous Engine│
│  • Threat        │                    │  • Decision      │
│    Detection     │                    │    Making        │
│  • Risk Scoring  │                    │  • Automation    │
└──────────────────┘                    └──────────────────┘
        │                                           │
        └─────────────────────┬─────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │            Output Layer                  │
        │  • Terminal (Rich)                       │
        │  • JSON Reports                          │
        │  • Markdown Reports                      │
        │  • GitHub PRs/Issues                     │
        └─────────────────────────────────────────┘
```

## Data Flow

### 1. Code Scanning Flow

```
User Input
    │
    ▼
┌─────────────┐
│  CLI Scan   │
│  Command    │
└─────────────┘
    │
    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Secret    │      │  Homograph  │      │     CVE     │
│  Scanner    │──────│   Detector  │──────│   Scanner   │
└─────────────┘      └─────────────┘      └─────────────┘
    │                     │                     │
    └─────────────────────┴─────────────────────┘
                          │
                          ▼
                  ┌─────────────┐
                  │   Findings  │
                  │ Aggregation │
                  └─────────────┘
                          │
                          ▼
                  ┌─────────────┐
                  │ AI Analysis │
                  │  (Optional) │
                  └─────────────┘
                          │
                          ▼
                  ┌─────────────┐
                  │   Output    │
                  │  Rendering  │
                  └─────────────┘
```

### 2. GitHub Repository Analysis Flow

```
User Selection
    │
    ▼
┌─────────────────┐
│  Repository     │
│  Discovery      │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  GitHub API     │
│  Data Fetch     │
│  • Workflows    │
│  • Alerts       │
│  • Protection   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Security       │
│  Analysis       │
│  • Config       │
│  • Risks        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  AI Analysis    │
│  • Threats      │
│  • Patterns     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Autonomous     │
│  Decisions      │
│  • Actions      │
│  • Priorities   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Visualization  │
│  • Graphs       │
│  • Timelines    │
└─────────────────┘
```

### 3. Automated Remediation Flow

```
Security Finding
    │
    ▼
┌─────────────────┐
│  Decision       │
│  Engine         │
│  • Severity     │
│  • Type         │
│  • Context      │
└─────────────────┘
    │
    ├─────────────────┬─────────────────┬─────────────────┐
    │                 │                 │                 │
    ▼                 ▼                 ▼                 ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  Warn   │    │ Require │    │  Block  │    │ Generate│
│  Only   │    │Approval │    │Pipeline │    │   PR    │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
                                                    │
                                                    ▼
                                            ┌─────────────┐
                                            │   Create    │
                                            │   Branch    │
                                            └─────────────┘
                                                    │
                                                    ▼
                                            ┌─────────────┐
                                            │   Update    │
                                            │    File     │
                                            └─────────────┘
                                                    │
                                                    ▼
                                            ┌─────────────┐
                                            │   Create    │
                                            │     PR      │
                                            └─────────────┘
```

### 4. Organization Scanning Flow

```
Organization Name
    │
    ▼
┌─────────────────┐
│  Fetch All      │
│  Repositories   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Parallel       │
│  Analysis       │
│  ┌───────────┐  │
│  │  Repo 1   │  │
│  │  Repo 2   │  │
│  │  Repo 3   │  │
│  │   ...     │  │
│  └───────────┘  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Risk           │
│  Aggregation    │
│  • Scores       │
│  • Patterns     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Heatmap        │
│  Generation     │
│  • Ranking      │
│  • Visualization│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Report         │
│  Export         │
│  • JSON         │
│  • Dashboard    │
└─────────────────┘
```

## Module Dependencies

```
┌─────────────────────────────────────────────────────────┐
│                      cli_new.py                         │
│                   (CLI Interface)                       │
└─────────────────────────────────────────────────────────┘
    │
    ├──────────────┬──────────────┬──────────────┬────────────────┐
    │              │              │              │                │
    ▼              ▼              ▼              ▼                ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐
│  auth   │  │discovery│  │remediate│  │visualize│  │   config     │
└─────────┘  └─────────┘  └─────────┘  └─────────┘  └──────────────┘
    │              │              │              │                │
    └──────────────┴──────────────┴──────────────┴────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │    External Services     │
                    │  • GitHub API            │
                    │  • Groq AI API           │
                    │  • NVD API               │
                    └──────────────────────────┘
```

## Component Interactions

### Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   User   │────▶│   CLI    │────▶│   Auth   │────▶│  GitHub  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                        │
                                        ▼
                                  ┌──────────┐
                                  │  Config  │
                                  │  Storage │
                                  └──────────┘
```

### Repository Analysis Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   User   │────▶│Discovery │────▶│ Security │────▶│    AI    │
└──────────┘     └──────────┘     │ Analysis │     │ Analysis │
                                  └──────────┘     └──────────┘
                                        │                │
                                        ▼                ▼
                                  ┌──────────┐     ┌──────────┐
                                  │Autonomous│────▶│Visualize │
                                  │  Engine  │     └──────────┘
                                  └──────────┘
                                        │
                                        ▼
                                  ┌──────────┐
                                  │Remediate │
                                  └──────────┘
```

### PR Generation Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Finding  │────▶│ Decision │────▶│  Branch  │────▶│   File   │
└──────────┘     │  Engine  │     │  Create  │     │  Update  │
                 └──────────┘     └──────────┘     └──────────┘
                                                          │
                                                          ▼
                                                    ┌──────────┐
                                                    │    PR    │
                                                    │  Create  │
                                                    └──────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
│  • Typer (CLI Framework)                                │
│  • Questionary (Interactive Prompts)                    │
│  • Rich (Terminal UI)                                   │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                     │
│  • Python 3.11+                                         │
│  • Async/Await                                          │
│  • Type Hints                                           │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    Core Modules                         │
│  • Authentication                                       │
│  • Discovery                                            │
│  • Remediation                                          │
│  • Visualization                                        │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                  External Services                      │
│  • GitHub API (REST)                                    │
│  • Groq AI API                                          │
│  • NVD API                                              │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                   Data Storage                          │
│  • TOML Config Files                                    │
│  • JSON Reports                                         │
│  • Environment Variables                                │
└─────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Security Layers                       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Authentication & Authorization                   │ │
│  │  • PAT Validation                                 │ │
│  │  • Secure Storage                                 │ │
│  │  • Token Refresh                                  │ │
│  └───────────────────────────────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Data Protection                                  │ │
│  │  • No Secrets in Logs                             │ │
│  │  • Encrypted Config                               │ │
│  │  • Secure API Calls                               │ │
│  └───────────────────────────────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Input Validation                                 │ │
│  │  • Parameter Validation                           │ │
│  │  • Type Checking                                  │ │
│  │  • Sanitization                                   │ │
│  └───────────────────────────────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Error Handling                                   │ │
│  │  • Graceful Failures                              │ │
│  │  • Audit Logging                                  │ │
│  │  • Rate Limiting                                  │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Development                           │
│  • Local Installation                                   │
│  • pip install -e .                                     │
│  • Development Mode                                     │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    Testing                              │
│  • Unit Tests (pytest)                                  │
│  • Integration Tests                                    │
│  • E2E Tests                                            │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                   Production                            │
│  • PyPI Package                                         │
│  • pip install sentinelci                               │
│  • System-wide Installation                             │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                   CI/CD Integration                     │
│  • GitHub Actions                                       │
│  • GitLab CI                                            │
│  • Jenkins                                              │
└─────────────────────────────────────────────────────────┘
```

---

**Legend:**
- `│` - Vertical connection
- `─` - Horizontal connection
- `▼` - Data flow direction
- `┌─┐` - Component boundary
- `└─┘` - Component boundary
