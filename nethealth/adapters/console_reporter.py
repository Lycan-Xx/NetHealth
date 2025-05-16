"""Console reporting implementation using Rich."""
from datetime import datetime
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nethealth.domain.interfaces import NetworkReport, Reporter


class ConsoleReporter(Reporter):
    """Rich-based console reporter for network analysis results."""
    
    def __init__(self):
        self.console = Console()
    
    def report(self, data: NetworkReport) -> None:
        """Display network analysis results in the console."""
        # Main panel with timestamp
        self.console.print(
            Panel(
                f"Network Health Report - {data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                style="bold blue"
            )
        )
        
        # Speed test results
        speed_table = Table(title="Speed Test Results", show_header=True)
        speed_table.add_column("Metric", style="cyan")
        speed_table.add_column("Value", style="green")
        
        speed_table.add_row("Download Speed", f"{data.speed.download_mbps} Mbps")
        speed_table.add_row("Upload Speed", f"{data.speed.upload_mbps} Mbps")
        speed_table.add_row("Ping", f"{data.speed.ping_ms} ms")
        
        self.console.print(speed_table)
        
        # Network fingerprint
        fp_table = Table(title="Network Fingerprint", show_header=True)
        fp_table.add_column("Property", style="cyan")
        fp_table.add_column("Value", style="green")
        
        fp_table.add_row("Public IP", data.fingerprint.public_ip)
        fp_table.add_row("ISP", data.fingerprint.isp)
        fp_table.add_row("Location", f"{data.fingerprint.city}, {data.fingerprint.country}")
        
        # Security status with colored indicators
        vpn_status = Text("✓ Active", "green") if data.vpn_status.is_active else Text("✗ Inactive", "red")
        proxy_status = Text("⚠ Detected", "yellow") if data.fingerprint.is_proxy else Text("✓ None", "green")
        tor_status = Text("⚠ Detected", "yellow") if data.fingerprint.is_tor else Text("✓ None", "green")
        
        fp_table.add_row("VPN", vpn_status)
        fp_table.add_row("Proxy", proxy_status)
        fp_table.add_row("Tor", tor_status)
        
        self.console.print(fp_table)
        
        # Network interfaces
        if data.fingerprint.interfaces:
            interface_table = Table(title="Network Interfaces", show_header=True)
            interface_table.add_column("Name", style="cyan")
            interface_table.add_column("IP Address", style="green")
            interface_table.add_column("MAC Address", style="blue")
            interface_table.add_column("Status", style="yellow")
            
            for interface in data.fingerprint.interfaces:
                status = "Active" if interface.is_active else "Inactive"
                interface_table.add_row(
                    interface.name,
                    interface.ip_address,
                    interface.mac_address,
                    status
                )
            
            self.console.print(interface_table)