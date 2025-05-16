"""Network speed testing implementation."""
import logging
from typing import Optional, Tuple

import speedtest
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.console import Console

from nethealth.domain.interfaces import NetworkSpeed

logger = logging.getLogger(__name__)

class SpeedTestError(Exception):
    """Base exception for speed testing errors."""
    pass

class SpeedTestAdapter:
    """Speed test implementation using speedtest-cli."""
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        self.console = Console()
        
    def measure_speed(self) -> NetworkSpeed:
        """Perform speed test measurements."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ) as progress:
                
                # Initialize speedtest
                main_task = progress.add_task("Running speed test...", total=100)
                client = self._init_speedtest(progress, main_task)
                
                # Get best server
                progress.update(main_task, description="Finding best server...", completed=20)
                server = client.get_best_server()
                logger.info(f"Selected server: {server['host']} ({server['country']})")
                
                # Download test
                progress.update(main_task, description="Testing download speed...", completed=40)
                download = client.download() / 1_000_000  # Convert to Mbps
                
                # Upload test
                progress.update(main_task, description="Testing upload speed...", completed=70)
                upload = client.upload() / 1_000_000  # Convert to Mbps
                
                # Get ping
                progress.update(main_task, description="Measuring latency...", completed=90)
                ping = client.results.ping
                
                progress.update(main_task, description="Speed test complete!", completed=100)
                
                return NetworkSpeed(
                    download_mbps=round(download, 2),
                    upload_mbps=round(upload, 2),
                    ping_ms=round(ping, 2)
                )
                
        except speedtest.SpeedtestException as e:
            logger.error(f"Speed test failed: {str(e)}")
            raise SpeedTestError(f"Speed test failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during speed test: {str(e)}")
            raise SpeedTestError(f"Unexpected error during speed test: {str(e)}")
    
    def _init_speedtest(self, progress: Progress, task: TaskID) -> speedtest.Speedtest:
        """Initialize speedtest client with proper configuration."""
        try:
            progress.update(task, description="Initializing speed test...", completed=10)
            
            client = speedtest.Speedtest(timeout=self.timeout)
            client.get_servers()
            
            return client
            
        except speedtest.ConfigRetrievalError:
            raise SpeedTestError("Failed to retrieve speedtest configuration")
        except speedtest.NoMatchedServers:
            raise SpeedTestError("No available speedtest servers found")