# Observability as Code

> A collection of tools for automating observability platforms with code.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

**Observability as Code** is a monorepo containing tools to manage various observability platforms programmatically. Each component provides both a Python API and CLI for managing infrastructure as code.

## Components

| Component | Description | Status |
|-----------|-------------|--------|
| [**Grafana-as-Code**](grafana-as-code/) | Manage Grafana dashboards, folders, panels, and variables | ✅ Active |
| *Prometheus-as-Code* | Manage Prometheus rules and alerts | 🚧 Planned |
| *Loki-as-Code* | Manage Loki log queries and rules | 🚧 Planned |
| *Tempo-as-Code* | Manage Tempo tracing configurations | 🚧 Planned |

## Quick Start

Each component is self-contained. Navigate to the component directory to get started:

```bash
# For Grafana management
cd grafana-as-code
cat README.md
```

## Project Structure

```
observability-as-code/
├── grafana-as-code/          # Grafana dashboard and alert management
│   ├── README.md             # Component-specific documentation
│   ├── cli.py                # CLI entry point
│   ├── src/                  # Source code
│   ├── docs/                 # API documentation
│   └── examples/             # Usage examples
├── prometheus-as-code/       # (Planned) Prometheus rules management
├── loki-as-code/             # (Planned) Loki queries management
├── .github/                  # GitHub templates and workflows
├── CONTRIBUTING.md           # Contribution guidelines
├── CODE_OF_CONDUCT.md        # Community guidelines
├── LICENSE                   # MIT License
└── SECURITY.md               # Security policy
```

## Documentation

- **[Grafana-as-Code README](grafana-as-code/README.md)** - Grafana component documentation
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community guidelines

## Installation

Each component has its own dependencies. Install them per-component:

```bash
cd grafana-as-code
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

For security issues, please see our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For component-specific issues, please check the component directory. For general project issues, visit [GitHub Issues](https://github.com/AmirrezaRezaie/observability-as-code/issues).

## Author

**Amirreza Rezaie** - [GitHub](https://github.com/AmirrezaRezaie) | [LinkedIn](https://linkedin.com/in/amirreza-rezaie-)

---
