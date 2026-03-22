#!/usr/bin/env python3
"""
Analytics & Reporting System
Track campaign metrics, payload success rates, and generate reports
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import Counter


class Campaign:
    """Track a single operation campaign"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.created_at = datetime.now().isoformat()
        self.events: List[Dict] = []
        self.stats = {
            'payloads_embedded': 0,
            'payloads_extracted': 0,
            'payloads_executed': 0,
            'exfiltrations_successful': 0,
            'exfiltrations_failed': 0,
            'targets_compromised': set()
        }
    
    def add_event(self, event_type: str, details: Dict):
        """Add event to campaign timeline"""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.events.append(event)
        
        # Update stats
        if event_type == 'payload_embedded':
            self.stats['payloads_embedded'] += 1
        elif event_type == 'payload_extracted':
            self.stats['payloads_extracted'] += 1
        elif event_type == 'payload_executed':
            self.stats['payloads_executed'] += 1
        elif event_type == 'exfiltration_success':
            self.stats['exfiltrations_successful'] += 1
        elif event_type == 'exfiltration_failed':
            self.stats['exfiltrations_failed'] += 1
        elif event_type == 'target_compromised':
            target = details.get('target', 'unknown')
            self.stats['targets_compromised'].add(target)
    
    def to_dict(self) -> Dict:
        """Export campaign to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'events': self.events,
            'stats': {
                **self.stats,
                'targets_compromised': list(self.stats['targets_compromised'])
            }
        }


class AnalyticsEngine:
    """Central analytics engine for tracking all operations"""
    
    def __init__(self, data_dir: str = None):
        """Initialize analytics engine"""
        if data_dir is None:
            data_dir = os.path.join(str(Path.home()), '.echodead', 'analytics')
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.campaigns: Dict[str, Campaign] = {}
        self.load_campaigns()
    
    def create_campaign(self, name: str, description: str = "") -> Campaign:
        """Create new campaign"""
        campaign = Campaign(name, description)
        self.campaigns[campaign.id] = campaign
        self.save_campaign(campaign)
        return campaign
    
    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign by ID"""
        return self.campaigns.get(campaign_id)
    
    def save_campaign(self, campaign: Campaign):
        """Save campaign to disk"""
        filepath = self.data_dir / f"{campaign.id}.json"
        with open(filepath, 'w') as f:
            json.dump(campaign.to_dict(), f, indent=2)
    
    def load_campaigns(self):
        """Load all campaigns from disk"""
        for filepath in self.data_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                campaign = Campaign(data['name'], data['description'])
                campaign.id = data['id']
                campaign.created_at = data['created_at']
                campaign.events = data['events']
                
                stats = data['stats']
                campaign.stats = {
                    **stats,
                    'targets_compromised': set(stats['targets_compromised'])
                }
                
                self.campaigns[campaign.id] = campaign
            except:
                pass
    
    def get_overall_stats(self) -> Dict:
        """Get aggregated stats across all campaigns"""
        total_stats = {
            'total_campaigns': len(self.campaigns),
            'payloads_embedded': 0,
            'payloads_executed': 0,
            'exfiltrations_successful': 0,
            'exfiltrations_failed': 0,
            'unique_targets': set(),
            'success_rate': 0.0
        }
        
        for campaign in self.campaigns.values():
            total_stats['payloads_embedded'] += campaign.stats['payloads_embedded']
            total_stats['payloads_executed'] += campaign.stats['payloads_executed']
            total_stats['exfiltrations_successful'] += campaign.stats['exfiltrations_successful']
            total_stats['exfiltrations_failed'] += campaign.stats['exfiltrations_failed']
            total_stats['unique_targets'].update(campaign.stats['targets_compromised'])
        
        # Calculate success rate
        total_exfil = total_stats['exfiltrations_successful'] + total_stats['exfiltrations_failed']
        if total_exfil > 0:
            total_stats['success_rate'] = (total_stats['exfiltrations_successful'] / total_exfil) * 100
        
        total_stats['unique_targets'] = len(total_stats['unique_targets'])
        
        return total_stats
    
    def generate_report(self, campaign_id: Optional[str] = None, format: str = 'text') -> str:
        """
        Generate report for campaign or overall stats
        
        Args:
            campaign_id: Optional campaign ID (None for overall)
            format: 'text', 'json', or 'html'
        
        Returns:
            Report string
        """
        if campaign_id:
            return self._generate_campaign_report(campaign_id, format)
        else:
            return self._generate_overall_report(format)
    
    def _generate_campaign_report(self, campaign_id: str, format: str) -> str:
        """Generate report for specific campaign"""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return f"Campaign {campaign_id} not found"
        
        if format == 'json':
            return json.dumps(campaign.to_dict(), indent=2)
        
        elif format == 'text':
            report = []
            report.append("=" * 70)
            report.append(f"CAMPAIGN REPORT: {campaign.name}")
            report.append("=" * 70)
            report.append(f"ID: {campaign.id}")
            report.append(f"Created: {campaign.created_at}")
            report.append(f"Description: {campaign.description}")
            report.append("")
            report.append("STATISTICS")
            report.append("-" * 70)
            report.append(f"  Payloads Embedded: {campaign.stats['payloads_embedded']}")
            report.append(f"  Payloads Extracted: {campaign.stats['payloads_extracted']}")
            report.append(f"  Payloads Executed: {campaign.stats['payloads_executed']}")
            report.append(f"  Exfiltrations Successful: {campaign.stats['exfiltrations_successful']}")
            report.append(f"  Exfiltrations Failed: {campaign.stats['exfiltrations_failed']}")
            report.append(f"  Targets Compromised: {len(campaign.stats['targets_compromised'])}")
            report.append("")
            report.append("EVENT TIMELINE")
            report.append("-" * 70)
            
            for event in campaign.events[-10:]:  # Last 10 events
                report.append(f"  [{event['timestamp']}] {event['type']}")
                report.append(f"     {event['details']}")
            
            report.append("=" * 70)
            return '\n'.join(report)
        
        elif format == 'html':
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Campaign Report: {campaign.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }}
        h1 {{ color: #00ff41; }}
        .stats {{ background: #16213e; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .stat-item {{ display: inline-block; margin: 10px 20px; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #00ff41; }}
        .stat-label {{ font-size: 14px; color: #aaa; }}
        .timeline {{ background: #16213e; padding: 20px; border-radius: 10px; }}
        .event {{ margin: 10px 0; padding: 10px; background: #0f3460; border-left: 3px solid #00ff41; }}
    </style>
</head>
<body>
    <h1>⚡ {campaign.name}</h1>
    <p><strong>ID:</strong> {campaign.id}</p>
    <p><strong>Created:</strong> {campaign.created_at}</p>
    <p><strong>Description:</strong> {campaign.description}</p>
    
    <div class="stats">
        <h2>Statistics</h2>
        <div class="stat-item">
            <div class="stat-value">{campaign.stats['payloads_embedded']}</div>
            <div class="stat-label">Payloads Embedded</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{campaign.stats['payloads_executed']}</div>
            <div class="stat-label">Payloads Executed</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{campaign.stats['exfiltrations_successful']}</div>
            <div class="stat-label">Successful Exfiltrations</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{len(campaign.stats['targets_compromised'])}</div>
            <div class="stat-label">Targets Compromised</div>
        </div>
    </div>
    
    <div class="timeline">
        <h2>Event Timeline</h2>
"""
            for event in campaign.events[-20:]:
                html += f"""
        <div class="event">
            <strong>{event['type']}</strong> - {event['timestamp']}<br>
            <small>{event['details']}</small>
        </div>
"""
            
            html += """
    </div>
</body>
</html>
"""
            return html
        
        return "Unsupported format"
    
    def _generate_overall_report(self, format: str) -> str:
        """Generate overall analytics report"""
        stats = self.get_overall_stats()
        
        if format == 'json':
            return json.dumps(stats, indent=2)
        
        elif format == 'text':
            report = []
            report.append("=" * 70)
            report.append("ECHODEAD - OVERALL ANALYTICS REPORT")
            report.append("=" * 70)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            report.append("OVERALL STATISTICS")
            report.append("-" * 70)
            report.append(f"  Total Campaigns: {stats['total_campaigns']}")
            report.append(f"  Payloads Embedded: {stats['payloads_embedded']}")
            report.append(f"  Payloads Executed: {stats['payloads_executed']}")
            report.append(f"  Successful Exfiltrations: {stats['exfiltrations_successful']}")
            report.append(f"  Failed Exfiltrations: {stats['exfiltrations_failed']}")
            report.append(f"  Success Rate: {stats['success_rate']:.1f}%")
            report.append(f"  Unique Targets: {stats['unique_targets']}")
            report.append("")
            report.append("CAMPAIGNS")
            report.append("-" * 70)
            
            for campaign_id, campaign in list(self.campaigns.items())[:10]:
                report.append(f"  [{campaign.name}] - {campaign.stats['payloads_embedded']} payloads")
            
            report.append("=" * 70)
            return '\n'.join(report)
        
        return "Unsupported format"
    
    def export_to_csv(self, campaign_id: Optional[str] = None) -> str:
        """Export campaign events to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Campaign', 'Event Type', 'Timestamp', 'Details'])
        
        # Data
        campaigns = [self.campaigns[campaign_id]] if campaign_id else self.campaigns.values()
        
        for campaign in campaigns:
            for event in campaign.events:
                writer.writerow([
                    campaign.name,
                    event['type'],
                    event['timestamp'],
                    str(event['details'])
                ])
        
        return output.getvalue()


# Example usage
def main():
    """Demo analytics system"""
    analytics = AnalyticsEngine()
    
    # Create test campaign
    campaign = analytics.create_campaign("Test Operation", "Testing analytics system")
    
    # Add some events
    campaign.add_event('payload_embedded', {'image': 'vacation.jpg', 'payload': 'keylogger.py'})
    campaign.add_event('payload_executed', {'target': '192.168.1.100'})
    campaign.add_event('exfiltration_success', {'data_size': 1024})
    campaign.add_event('target_compromised', {'target': '192.168.1.100'})
    
    analytics.save_campaign(campaign)
    
    # Generate report
    print(analytics.generate_report(campaign.id, format='text'))
    print("\n")
    print(analytics.generate_report(format='text'))


if __name__ == '__main__':
    main()
