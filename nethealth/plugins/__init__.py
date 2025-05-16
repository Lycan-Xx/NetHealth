"""Plugin system for NetHealth."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Type
import importlib
import inspect
import logging
import pkg_resources
from pathlib import Path

from nethealth.domain.interfaces import NetworkReport

logger = logging.getLogger(__name__)

@dataclass
class PluginMetadata:
    """Metadata for a NetHealth plugin."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]

class NetHealthPlugin(ABC):
    """Base class for all NetHealth plugins."""
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass
    
    @abstractmethod
    def process_report(self, report: NetworkReport) -> NetworkReport:
        """Process a network report and optionally modify it."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up any resources used by the plugin."""
        pass

class PluginManager:
    """Manages NetHealth plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, NetHealthPlugin] = {}
        self._load_plugins()
    
    def _load_plugins(self) -> None:
        """Discover and load available plugins."""
        # Load from entry points
        for entry_point in pkg_resources.iter_entry_points('nethealth.plugins'):
            try:
                plugin_class = entry_point.load()
                if not issubclass(plugin_class, NetHealthPlugin):
                    logger.warning(f"Invalid plugin {entry_point.name}: Not a NetHealthPlugin subclass")
                    continue
                
                plugin = plugin_class()
                self.register_plugin(plugin)
                
            except Exception as e:
                logger.error(f"Failed to load plugin {entry_point.name}: {str(e)}")
        
        # Load from plugins directory
        plugins_dir = Path(__file__).parent / "contrib"
        if plugins_dir.exists():
            for plugin_file in plugins_dir.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                
                try:
                    module_name = f"nethealth.plugins.contrib.{plugin_file.stem}"
                    module = importlib.import_module(module_name)
                    
                    # Find plugin classes in module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, NetHealthPlugin) and 
                            obj != NetHealthPlugin):
                            plugin = obj()
                            self.register_plugin(plugin)
                            
                except Exception as e:
                    logger.error(f"Failed to load plugin from {plugin_file}: {str(e)}")
    
    def register_plugin(self, plugin: NetHealthPlugin) -> None:
        """Register a new plugin."""
        try:
            plugin.initialize()
            self.plugins[plugin.metadata.name] = plugin
            logger.info(f"Registered plugin: {plugin.metadata.name} v{plugin.metadata.version}")
            
        except Exception as e:
            logger.error(f"Failed to register plugin {plugin.metadata.name}: {str(e)}")
    
    def process_report(self, report: NetworkReport) -> NetworkReport:
        """Process a report through all active plugins."""
        current_report = report
        
        for plugin in self.plugins.values():
            try:
                current_report = plugin.process_report(current_report)
            except Exception as e:
                logger.error(f"Plugin {plugin.metadata.name} failed to process report: {str(e)}")
        
        return current_report
    
    def cleanup(self) -> None:
        """Clean up all plugins."""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Failed to cleanup plugin {plugin.metadata.name}: {str(e)}")