# SentinelCI Refactoring Summary

## New Modular Architecture

### Core Modules (`sentinelci/core/`)

1. **auth.py** - GitHub authentication management
   - PAT validation and storage
   - User authentication checks
   - Clean error handling

2. **discovery.py** - Repository discovery and organization scanning
   - Fetch user repositories
   - Fetch organization repositories
   - Advanced filtering (search, visibility, language, stars)
   - Repository normalization

3. **remediation.py** - Automated PR and Issue generation
   - Create security issues
   - Generate pull requests with fixes
   - Branch management
   - File updates via GitHub API
   - Pre-built templates for:
     - Secret removal PRs
     - Dependency pinning PRs
     - Workflow permission tightening PRs

4. **visualization.py** - Security incident graphs and heatmaps
   - Incident graph builder
   - Attack chain timeline generation
   - Relationship mapping (commits → secrets → workflows → alerts)
   - Organization-wide risk heatmap
   - Rich terminal visualization

### New Features Implemented

#### 1. Automated Remediation
```python
from sentinelci.core.remediation import RemediationEngine

engine = RemediationEngine()

# Generate PR for secret removal
pr = engine.generate_secret_removal_pr(
    "owner/repo",
    finding,
    fixed_content
)

# Generate PR for dependency pinning
pr = engine.generate_dependency_pinning_pr(
    "owner/repo",
    finding,
    fixed_content
)

# Generate PR for workflow permissions
pr = engine.generate_workflow_permission_pr(
    "owner/repo",
    workflow_file,
    fixed_content
)
```

#### 2. Incident Graph Visualization
```python
from sentinelci.core.visualization import IncidentGraph

graph = IncidentGraph()
graph.build_from_findings(findings, repo_data)

# Render visual graph
graph.render_graph()

# Show attack chain timeline
graph.render_attack_chain()

# Export to JSON
graph.export_json("incident_graph.json")
```

#### 3. Organization-Wide Scanning
```bash
# Scan entire organization
sci github scan-org my-org --output org_report.json

# Features:
# - Aggregate risk heatmap
# - Rank riskiest repositories
# - Cross-repo secret reuse detection
# - Repeated vulnerable workflow patterns
# - Org-wide policy violations
```

#### 4. Modern CLI with Typer
```bash
# Interactive onboarding
sci onboard

# GitHub commands
sci github auth
sci github setup
sci github repos --search myproject --visibility private
sci github scan-org my-org

# Repository actions (interactive menu):
# 1. Analyze Security Configuration
# 2. Run AI Security Analysis
# 3. Simulate Autonomous Decisions
# 4. Generate Security PR
# 5. View Incident Graph
# 6. Full Analysis + Visualization
```

### Existing Modules (Kept & Enhanced)

- **scanner.py** - Core scanning engine (secrets, URLs, CVEs)
- **agent.py** - AI-powered analysis
- **ai_analyzer.py** - Advanced AI security analysis
- **autonomous_engine.py** - Decision engine
- **github_security.py** - GitHub security analysis
- **config.py** - Configuration management
- **fixer.py** - Automated fixes

### CLI Structure

```
sci
├── onboard              # Interactive setup wizard
├── scan                 # Code scanning (existing)
├── watch                # Real-time monitoring (existing)
├── fix                  # Auto-fix issues (existing)
├── github
│   ├── auth            # Check authentication
│   ├── setup           # Configure GitHub PAT
│   ├── repos           # List & analyze repositories
│   └── scan-org        # Scan entire organization
├── hook                # Git hooks (existing)
├── report              # Generate reports (existing)
└── version             # Version info
```

### Onboarding Flow

1. **Welcome & Introduction**
   - Explain SentinelCI capabilities
   - Set expectations

2. **AI API Key Setup**
   - Check for existing key
   - Prompt for Groq API key
   - Validate and store

3. **GitHub Integration (Optional)**
   - Explain benefits
   - Guide through PAT creation
   - Validate and store

4. **Scanning Preferences**
   - Severity threshold (low/medium/high/critical)
   - Enable/disable firmware scanning
   - Enable/disable URL detection

5. **Completion & Next Steps**
   - Show available commands
   - Suggest first actions

### Key Improvements

1. **Modularity**
   - Clear separation of concerns
   - Reusable components
   - Easy to test and maintain

2. **User Experience**
   - Interactive onboarding
   - Rich terminal UI
   - Clear error messages
   - Helpful prompts

3. **Automation**
   - Automated PR generation
   - Issue creation
   - Branch management
   - File updates

4. **Visualization**
   - Incident graphs
   - Attack chain timelines
   - Risk heatmaps
   - Relationship mapping

5. **Organization Support**
   - Scan all org repositories
   - Aggregate risk analysis
   - Cross-repo pattern detection
   - Policy violation tracking

### Migration Path

1. **Phase 1: Core Modules** ✅
   - Created `sentinelci/core/` directory
   - Implemented auth, discovery, remediation, visualization

2. **Phase 2: New CLI** ✅
   - Created `cli_new.py` with Typer
   - Implemented interactive commands
   - Added onboarding wizard

3. **Phase 3: Integration** (Next)
   - Update `cli.py` to use new modules
   - Add missing commands
   - Test end-to-end flows

4. **Phase 4: Cleanup** (Next)
   - Remove duplicate code
   - Consolidate modules
   - Update documentation

### Usage Examples

#### Onboarding
```bash
sci onboard
```

#### Scan Organization
```bash
sci github scan-org acme-corp --output acme_security_report.json
```

#### Analyze Repository with Full Visualization
```bash
sci github repos --search "api-gateway"
# Select repository
# Choose "Full Analysis + Visualization"
```

#### Generate Security PR
```bash
sci github repos
# Select repository
# Choose "Generate Security PR"
# Select finding to fix
```

#### View Incident Graph
```bash
sci github repos
# Select repository
# Choose "View Incident Graph"
```

### Dependencies

New dependencies added:
- `typer` - Modern CLI framework
- `questionary` - Interactive prompts
- `rich` - Terminal formatting (already used)

### Testing

Test the new modules:
```bash
# Test authentication
python -c "from sentinelci.core.auth import GitHubAuth; auth = GitHubAuth(); print(auth.has_pat())"

# Test discovery
python -c "from sentinelci.core.discovery import RepositoryDiscovery; d = RepositoryDiscovery(); print(len(d.fetch_user_repositories()))"

# Test visualization
python -c "from sentinelci.core.visualization import IncidentGraph; g = IncidentGraph(); g.render_graph()"
```

### Next Steps

1. **Install new dependencies**:
   ```bash
   pip install typer questionary
   ```

2. **Test new CLI**:
   ```bash
   python -m sentinelci.cli_new onboard
   ```

3. **Integrate with existing CLI**:
   - Update `cli.py` to import from `core/`
   - Add new commands
   - Maintain backward compatibility

4. **Update documentation**:
   - README.md
   - API documentation
   - Usage examples

5. **Add tests**:
   - Unit tests for core modules
   - Integration tests for CLI
   - End-to-end tests

### Benefits

✅ **Modular Architecture** - Easy to maintain and extend
✅ **Better UX** - Interactive onboarding and menus
✅ **Automation** - PR and issue generation
✅ **Visualization** - Incident graphs and heatmaps
✅ **Organization Support** - Scan entire orgs
✅ **Clean Code** - Separated concerns, reusable components
✅ **Type Safety** - Better type hints and validation
✅ **Error Handling** - Clear error messages and recovery
