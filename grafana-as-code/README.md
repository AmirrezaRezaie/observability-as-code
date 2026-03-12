# Grafana as Code

> Manage Grafana dashboards, folders, panels, and variables programmatically.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../../LICENSE)

## Overview

**Grafana-as-Code** is a Python-based tool that enables you to manage Grafana dashboards, folders, datasources, panels, and variables programmatically. Whether you prefer a clean Python API or a powerful CLI, this tool makes infrastructure as code (IaC) for observability a reality.

## Features

- **Object-Oriented API** - Intuitive Python API with Folder and Dashboard objects
- **Powerful CLI** - Full-featured command-line interface for automation
- **Component Management** - Add, edit, remove datasources, panels, and variables
- **Batch Operations** - Apply changes across entire folder trees
- **Export/Import** - Backup and restore dashboards as JSON
- **Type-Safe** - Designed with modern Python practices

## Project Structure

```
grafana-as-code/
├── cli.py                      # CLI entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── config/
│   ├── config.yaml             # Configuration file
│   └── datasources.json        # Datasource definitions
├── src/
│   ├── __init__.py             # Main exports
│   ├── client.py               # Grafana API client
│   ├── folder.py               # Folder object
│   ├── dashboard_v2.py         # Dashboard object (OO API)
│   └── components/
│       ├── datasource.py       # Datasource component
│       ├── panel.py            # Panel component
│       └── variable.py         # Variable component
├── scripts/                    # Utility scripts
├── examples/                   # Usage examples
├── docs/
│   └── OO_API_REFERENCE.md     # Complete API documentation
└── tests/                      # Test files
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Grafana instance with API access
- Grafana API key (recommended) or username/password

### Setup

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your Grafana credentials
```

## Quick Start

### Using the CLI

1. **Set your credentials** (optional, can use flags instead)
```bash
export GRAFANA_URL="http://localhost:3000"
export GRAFANA_API_KEY="your-api-key-here"
```

2. **List all folders**
```bash
python cli.py folder list
```

3. **View folder tree**
```bash
python cli.py folder tree
```

4. **Create a dashboard**
```bash
python cli.py dashboard create "My Dashboard" --folder General --tags monitoring,prod
```

### Using the Python API

```python
from src import GrafanaClient, Folder, Dashboard

# Initialize client
client = GrafanaClient(
    url="http://localhost:3000",
    api_key="your-api-key"
)

# Get or create a folder
folder = Folder.get(client, "monitoring")
if not folder:
    folder = Folder.create(client, "Monitoring", uid="monitoring")

# Create a dashboard
dashboard = Dashboard.create(
    client,
    "Server Metrics",
    folder=folder,
    tags=["production"]
)

# Add a variable
datasource = client.get_datasource_by_name("Prometheus")
dashboard.variables.add_interval()
dashboard.variables.add_query(
    name="server",
    query="label_values(instance)",
    datasource_uid=datasource["uid"],
    multi=True
)

# Add a panel
dashboard.panels.add_timeseries(
    title="CPU Usage",
    expr="rate(cpu_usage_total[5m]) * 100",
    datasource_uid=datasource["uid"]
)

# Save changes
dashboard.save("Created initial dashboard")
```

## CLI Usage

### Folder Commands

```bash
# List all folders
python cli.py folder list

# Show folder tree
python cli.py folder tree

# Create folder
python cli.py folder create "Monitoring" --uid monitoring

# List dashboards in folder (recursive)
python cli.py folder list-dashboards Overview --recursive

# Apply operation to all dashboards in folder tree
python cli.py folder apply Overview add-tag "production"
python cli.py folder apply Overview replace-datasource "Old-Prometheus,New-Prometheus"
python cli.py folder apply Monitoring add-variable "env,label_values(environment),ds-uid"
```

### Dashboard Commands

```bash
# List all dashboards
python cli.py dashboard list

# Get dashboard details
python cli.py dashboard get dashboard-uid

# Create dashboard
python cli.py dashboard create "My Dashboard" --folder Monitoring --tags prod,monitoring

# Duplicate dashboard
python cli.py dashboard duplicate source-uid "Staging Dashboard" --folder staging

# Export dashboard
python cli.py dashboard export dashboard-uid backups/dashboard.json

# Delete dashboard
python cli.py dashboard delete dashboard-uid --force
```

### Panel Commands

```bash
# Add timeseries panel
python cli.py panel add-timeseries dashboard-uid "CPU Usage" \
  --expr "rate(cpu_usage_total[5m]) * 100" \
  --datasource prometheus-uid \
  --legend "{{instance}}"

# Add stat panel
python cli.py panel add-stat dashboard-uid "Total Requests" \
  --expr "sum(rate(http_requests_total[5m]))" \
  --datasource prometheus-uid

# Add gauge panel
python cli.py panel add-gauge dashboard-uid "Memory %" \
  --expr "memory_usage_percent" \
  --datasource prometheus-uid \
  --min 0 --max 100

# List panels
python cli.py panel list dashboard-uid

# Remove panel
python cli.py panel remove dashboard-uid --panel_id 1
```

### Variable Commands

```bash
# Add query variable
python cli.py var add-query dashboard-uid job \
  --query "label_values(job)" \
  --datasource prometheus-uid

# Add multi-value query variable
python cli.py var add-query dashboard-uid instance \
  --query "label_values(instance)" \
  --datasource prometheus-uid \
  --multi

# Add custom variable
python cli.py var add-custom dashboard-uid env \
  --values "dev,staging,prod"

# Add interval variable
python cli.py var add-interval dashboard-uid

# Add constant variable
python cli.py var add-constant dashboard-uid region --value "us-west"

# Edit regex on existing variable
python cli.py var edit-regex dashboard-uid namespace "/.*prod.*/"

# List variables
python cli.py var list dashboard-uid
```

## Documentation

- **[CLI Reference](CLI_REFERENCE.md)** - Complete CLI command reference
- **[API Reference](docs/OO_API_REFERENCE.md)** - Full Python API documentation
- **[Refactoring Summary](REFACTORING_SUMMARY.md)** - Architecture and design decisions

## Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
# Grafana Configuration
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=your-api-key-here

# Default folder for new dashboards
DEFAULT_FOLDER=General

# Timeout settings (seconds)
API_TIMEOUT=30
```

### Config File

Edit [`config/config.yaml`](config/config.yaml) for panel defaults and datasource templates.

## Workflows

### Update All Dashboards in a Folder

```bash
# 1. View the folder structure
python cli.py folder tree

# 2. List all dashboards
python cli.py folder list-dashboards Overview --recursive

# 3. Add "production" tag to all
python cli.py folder apply Overview add-tag "production"

# 4. Replace datasource across all
python cli.py folder apply Overview replace-datasource "Test-Prometheus,Prod-Prometheus"
```

### Setup Monitoring Dashboards

```bash
# Create folder structure
python cli.py folder create "Monitoring/Backend"
python cli.py folder create "Monitoring/Frontend"

# Add common variable to all monitoring dashboards
python cli.py folder apply Monitoring add-variable "env,label_values(environment),prometheus-uid"

# Add production tag
python cli.py folder apply Monitoring add-tag "production"
```

### Migrate Datasource

```bash
# Replace datasource in all dashboards
python cli.py folder apply Overview replace-datasource "OldPrometheus,NewPrometheus"

# Verify the change
python cli.py ds list dashboard-uid
```

## Python API Examples

### Creating a Complete Dashboard

```python
from src import GrafanaClient, Folder, Dashboard

client = GrafanaClient()

# Get folder
folder = Folder.get(client, "monitoring")
dashboard = Dashboard.create(client, "API Metrics", folder=folder)

# Get datasource
ds = client.get_datasource_by_name("Prometheus")["uid"]

# Add variables
dashboard.variables.add_interval()
dashboard.variables.add_query("endpoint", "label_values(endpoint)", ds, multi=True)

# Add panels
dashboard.panels.add_timeseries("Request Rate", "rate(http_requests_total[5m])", ds)
dashboard.panels.add_stat("Error Rate", "rate(errors[5m])", ds)
dashboard.panels.add_gauge("P95 Latency", "histogram_quantile(0.95, latency)", ds, min=0, max=1000)

dashboard.save("Initial version")
```

### Batch Update Multiple Dashboards

```python
from src import GrafanaClient, Folder

client = GrafanaClient()
folder = Folder.get(client, "production")

def update_dashboard(dashboard):
    dashboard.datasources.replace("Old-DS", "New-DS")
    dashboard.add_tag("migrated")
    return "updated"

results = folder.apply_to_all_dashboards(update_dashboard)

for result in results:
    print(f"{result['dashboard']}: {result['status']}")
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project uses Black for code formatting:

```bash
black src/ tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Acknowledgments

- Built for managing Grafana dashboards as code
- Inspired by Infrastructure as Code principles
- Supports Grafana's HTTP API

## Support

For issues, questions, or contributions, please visit the [GitHub Issues](https://github.com/AmirrezaRezaie/observability-as-code/issues).

## Author

**Amirreza Rezaie** - [GitHub](https://github.com/AmirrezaRezaie) | [LinkedIn](https://linkedin.com/in/amirreza-rezaie-)

---

**Made with ❤️ for the observability community**
