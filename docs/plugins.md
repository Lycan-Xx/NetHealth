# Plugin Development Guide

NetHealth's plugin system allows you to extend functionality with custom features.

## Creating a Plugin

1. Create a new class inheriting from `NetHealthPlugin`:

```python
from nethealth.plugins import NetHealthPlugin, PluginMetadata
from nethealth.domain.interfaces import NetworkReport

class MyPlugin(NetHealthPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="My custom plugin",
            author="Your Name",
            dependencies=[]
        )
    
    def initialize(self) -> None:
        """Set up plugin resources."""
        pass
    
    def process_report(self, report: NetworkReport) -> NetworkReport:
        """Process and modify network report."""
        return report
    
    def cleanup(self) -> None:
        """Clean up resources."""
        pass
```

## Installation

1. Create a Python package
2. Add entry point to `setup.py`:

```python
setup(
    entry_points={
        'nethealth.plugins': [
            'my-plugin = my_package.plugin:MyPlugin',
        ],
    },
)
```

## Best Practices

1. Handle errors gracefully
2. Document all functionality
3. Include tests
4. Follow type hints
5. Clean up resources

## Example Plugins

See `nethealth/plugins/contrib/` for example implementations.