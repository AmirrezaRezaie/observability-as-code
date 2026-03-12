# Claude AI Assistant Context

This file contains important context for Claude (or other AI assistants) working on this project.

## Project Overview

**Observability-as-Code** is a monorepo for automating observability platforms with code. Currently, it contains:

- **grafana-as-code/**: Active Python tool for managing Grafana dashboards, folders, panels, variables, and datasources programmatically
- **Future**: prometheus-as-code/, loki-as-code/, tempo-as-code/ (planned)

## Project Structure

```
observability-as-code/
├── grafana-as-code/              # Grafana component (active)
│   ├── grafana_as_code/          # Main Python package
│   │   ├── __init__.py           # Package exports
│   │   ├── cli.py                # CLI entry point (main function)
│   │   ├── client.py             # GrafanaClient class
│   │   ├── folder.py             # Folder class
│   │   ├── dashboard.py          # Dashboard class
│   │   ├── dashboard_v2.py       # OO Dashboard implementation
│   │   └── components/           # Component managers
│   │       ├── datasource.py
│   │       ├── panel.py
│   │       └── variable.py
│   ├── config/                   # Configuration files
│   ├── docs/                     # Documentation
│   ├── examples/                 # Usage examples
│   ├── scripts/                  # Utility scripts
│   ├── tests/                    # Test files
│   ├── .env.example              # Environment template
│   ├── requirements.txt          # Dependencies
│   └── README.md                 # Component docs
├── .github/                      # GitHub resources
│   ├── workflows/                # CI/CD workflows
│   ├── dependabot.yml            # Dependency updates
│   └── ISSUE_TEMPLATE/           # Issue templates
├── pyproject.toml                # Project configuration (root)
├── README.md                     # Main project README
├── LICENSE                       # MIT License
├── CONTRIBUTING.md               # Contribution guidelines
├── CODE_OF_CONDUCT.md            # Community guidelines
└── SECURITY.md                   # Security policy
```

## Key Technical Details

### Package Configuration

- **Root package name**: `observability-as-code`
- **Version**: 2.0.0
- **Python requirement**: >= 3.8
- **Active component**: `grafana_as_code` (located in `grafana-as-code/`)
- **CLI entry point**: `grafana-cli = "grafana_as_code.cli:main"`

### CLI Usage

The CLI is installed via pip and can be invoked with:

```bash
grafana-cli [command] [subcommand] [options]
```

**Example commands:**
```bash
# List folders
grafana-cli folder list

# Show folder tree
grafana-cli folder tree

# Create dashboard
grafana-cli dashboard create "My Dashboard" --folder Monitoring --tags prod

# Add panel
grafana-cli panel add-timeseries dashboard-uid "CPU Usage" --expr "rate(cpu_usage_total[5m]) * 100" --datasource prometheus-uid
```

### Python API Usage

```python
from grafana_as_code import GrafanaClient, Folder, Dashboard

# Initialize client
client = GrafanaClient(url="http://localhost:3000", api_key="your-api-key")

# Get or create folder
folder = Folder.get(client, "monitoring")
if not folder:
    folder = Folder.create(client, "Monitoring", uid="monitoring")

# Create dashboard
dashboard = Dashboard.create(client, "Server Metrics", folder=folder, tags=["production"])

# Add components
dashboard.variables.add_interval()
dashboard.panels.add_timeseries("CPU Usage", "rate(cpu_usage_total[5m]) * 100", datasource_uid)

# Save changes
dashboard.save("Initial dashboard version")
```

## Coding Conventions

### Python Style

- **Formatter**: Black (line length: 100)
- **Import sorting**: isort (profile: black)
- **Type checking**: mypy (disabled for some legacy code)
- **Docstrings**: Google style preferred

### File Organization

- Use relative imports within packages (`from . import Module`)
- Place public API exports in `__init__.py`
- Keep CLI separate from API logic
- Component managers handle specific dashboard features

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `GrafanaClient`, `Dashboard`)
- **Functions/methods**: `snake_case` (e.g., `create_dashboard`, `list_all`)
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

## Development Workflow

### Running Tests

```bash
cd grafana-as-code
pytest tests/ -v
```

### Code Formatting

```bash
# Format code
black grafana_as_code/

# Check imports
isort --check-only grafana_as_code/
```

### Building the Package

```bash
pip install build
python -m build
```

## Important Notes

1. **Package Structure**: The grafana-as-code directory contains the `grafana_as_code` Python package. Do not confuse these.
2. **CLI Location**: The CLI is in `grafana_as_code/cli.py`, not at the root of grafana-as-code.
3. **Config Files**: The `config/` directory is outside the package and contains reference configurations, not package data.
4. **Environment**: Use `.env` file for credentials (create from `.env.example`).
5. **API Client**: All API interactions go through `GrafanaClient` class.

## Common Tasks

### Adding a New CLI Command

1. Add command function in `grafana_as_code/cli.py`
2. Add subparser in `main()` function
3. Test with: `grafana-cli [command] --help`

### Adding New Component Type

1. Create component class in `grafana_as_code/components/`
2. Add to `Dashboard` class as property
3. Export from `grafana_as_code/__init__.py`
4. Add CLI commands if needed
5. Add tests and documentation

### Updating Dependencies

1. Update `requirements.txt` or `pyproject.toml`
2. Test thoroughly
3. Update version in `grafana_as_code/__init__.py`
4. Update CHANGELOG if applicable

## Git Workflow

- **Main branch**: `main`
- **Feature branches**: `feature/feature-name`
- **Create PRs** for all changes
- **Use PR template** in `.github/pull_request_template.md`

## Security Considerations

- Never commit API keys or credentials
- Use environment variables for secrets
- See `SECURITY.md` for security policy
- API key strength should be validated
- Input validation is critical for all API parameters

## Contact

- **Author**: Amirreza Rezaie
- **GitHub**: https://github.com/AmirrezaRezaie/observability-as-code
- **Issues**: https://github.com/AmirrezaRezaie/observability-as-code/issues
