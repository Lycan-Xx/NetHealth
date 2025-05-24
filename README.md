# NetHealth

A comprehensive network analysis tool for monitoring and diagnosing network conditions.

## Features

- Network speed testing (download, upload, latency)
- Network fingerprinting (IP, ISP, location)
- VPN detection and analysis
- Network interface monitoring
- Historical data tracking
- Plugin system for extensibility

## Installation

```bash
pip install nethealth
```

## Quick Start

```bash
# Run a network analysis
nethealth analyze

# View historical data
nethealth history

# Run with specific plugins
nethealth analyze --plugins security,performance
```

## Documentation

Full documentation is available at [https://nethealth.readthedocs.io](https://nethealth.readthedocs.io)

## Plugin Development

NetHealth supports custom plugins for extending functionality. See the [Plugin Development Guide](docs/plugins.md) for details.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.



------------------------------------------------------------------------------------


In the project main directory run

#### Installation

```bash


pip install poetry

poetry install

poetry run nethealth analyze

## Running the script


poetry run nethealth analyze

# View historical data

poetry run nethealth history

# Run with specific plugins

nethealth analyze --plugins security,performance