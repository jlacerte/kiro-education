"""Educational Metrics Tracker.

Tracks usage metrics, costs, and prevents abuse in the educational system.
Provides detailed analytics and automatic alerts for cost control.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from rich.console import Console

console = Console()

@dataclass
class SessionMetrics:
    """Metrics for a single educational session."""
    session_id: str
    lesson_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    kiro_calls: int = 0
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    tasks_completed: int = 0
    total_tasks: int = 0
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
    
    @property
    def duration_minutes(self) -> float:
        """Calculate session duration in minutes."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return 0.0
    
    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.estimated_input_tokens + self.estimated_output_tokens

class EducationalMetricsTracker:
    """Tracks and analyzes educational system usage metrics."""
    
    # Cost estimates (Claude 3.5 Sonnet pricing approximation)
    COST_PER_INPUT_TOKEN = 0.000003  # $3 per 1M input tokens
    COST_PER_OUTPUT_TOKEN = 0.000015  # $15 per 1M output tokens
    
    # Safety thresholds
    MAX_SESSIONS_PER_DAY = 10
    MAX_KIRO_CALLS_PER_SESSION = 50
    MAX_COST_PER_SESSION = 5.0  # USD
    MAX_TOKENS_PER_SESSION = 100000
    
    def __init__(self, metrics_dir: str = "metrics"):
        """Initialize metrics tracker.
        
        Args:
            metrics_dir: Directory to store metrics files.
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)
        self.current_session: Optional[SessionMetrics] = None
        
    def start_session(self, session_id: str, lesson_type: str) -> SessionMetrics:
        """Start tracking a new session.
        
        Args:
            session_id: Unique session identifier.
            lesson_type: Type of lesson (debugging, security, etc.).
            
        Returns:
            SessionMetrics object for the new session.
        """
        self.current_session = SessionMetrics(
            session_id=session_id,
            lesson_type=lesson_type,
            start_time=datetime.now()
        )
        
        # Check daily session limit
        daily_count = self._get_daily_session_count()
        if daily_count >= self.MAX_SESSIONS_PER_DAY:
            warning = f"[!] ALERT: {daily_count} sessions today (max: {self.MAX_SESSIONS_PER_DAY})"
            self.current_session.warnings.append(warning)
            console.print(f"[red]{warning}[/red]")
        
        console.print(f"[STATS] Metrics tracking started: {session_id}")
        return self.current_session
    
    def record_kiro_call(self, estimated_input_tokens: int = 1000, estimated_output_tokens: int = 500):
        """Record a call to Kiro with token estimates.
        
        Args:
            estimated_input_tokens: Estimated input tokens for this call.
            estimated_output_tokens: Estimated output tokens for this call.
        """
        if not self.current_session:
            return
        
        self.current_session.kiro_calls += 1
        self.current_session.estimated_input_tokens += estimated_input_tokens
        self.current_session.estimated_output_tokens += estimated_output_tokens
        
        # Calculate cost
        input_cost = estimated_input_tokens * self.COST_PER_INPUT_TOKEN
        output_cost = estimated_output_tokens * self.COST_PER_OUTPUT_TOKEN
        self.current_session.estimated_cost_usd += input_cost + output_cost
        
        # Check thresholds
        if self.current_session.kiro_calls > self.MAX_KIRO_CALLS_PER_SESSION:
            warning = f"[!] ALERT: {self.current_session.kiro_calls} Kiro calls (max: {self.MAX_KIRO_CALLS_PER_SESSION})"
            self.current_session.warnings.append(warning)
            console.print(f"[red]{warning}[/red]")
        
        if self.current_session.estimated_cost_usd > self.MAX_COST_PER_SESSION:
            warning = f"[!] ALERT: ${self.current_session.estimated_cost_usd:.2f} cost (max: ${self.MAX_COST_PER_SESSION})"
            self.current_session.warnings.append(warning)
            console.print(f"[red]{warning}[/red]")
    
    def end_session(self, tasks_completed: int, total_tasks: int) -> SessionMetrics:
        """End the current session and save metrics.
        
        Args:
            tasks_completed: Number of tasks completed.
            total_tasks: Total number of tasks.
            
        Returns:
            Final SessionMetrics object.
        """
        if not self.current_session:
            return None
        
        self.current_session.end_time = datetime.now()
        self.current_session.tasks_completed = tasks_completed
        self.current_session.total_tasks = total_tasks
        
        # Save metrics
        self._save_session_metrics(self.current_session)
        
        # Display summary
        self._display_session_summary(self.current_session)
        
        session = self.current_session
        self.current_session = None
        return session
    
    def _get_daily_session_count(self) -> int:
        """Get number of sessions today."""
        today = datetime.now().date()
        count = 0
        
        for metrics_file in self.metrics_dir.glob("session_*.json"):
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    session_date = datetime.fromisoformat(data['start_time']).date()
                    if session_date == today:
                        count += 1
            except:
                continue
        
        return count
    
    def _save_session_metrics(self, session: SessionMetrics):
        """Save session metrics to file."""
        timestamp = session.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"session_{session.session_id}_{timestamp}.json"
        filepath = self.metrics_dir / filename
        
        # Convert to dict with ISO format dates
        data = asdict(session)
        data['start_time'] = session.start_time.isoformat()
        if session.end_time:
            data['end_time'] = session.end_time.isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        console.print(f"[SAVE] Metrics saved: {filename}")
    
    def _display_session_summary(self, session: SessionMetrics):
        """Display session metrics summary."""
        console.print("\n[STATS] [bold cyan]Session Metrics Summary[/bold cyan]")
        console.print(f"   Session ID: {session.session_id}")
        console.print(f"   Duration: {session.duration_minutes:.1f} minutes")
        console.print(f"   Kiro Calls: {session.kiro_calls}")
        console.print(f"   Total Tokens: {session.total_tokens:,}")
        console.print(f"   Estimated Cost: ${session.estimated_cost_usd:.4f}")
        console.print(f"   Tasks: {session.tasks_completed}/{session.total_tasks}")
        
        if session.warnings:
            console.print(f"   [red]Warnings: {len(session.warnings)}[/red]")
            for warning in session.warnings:
                console.print(f"     {warning}")
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily usage report."""
        today = datetime.now().date()
        sessions = []
        total_cost = 0.0
        total_calls = 0
        
        for metrics_file in self.metrics_dir.glob("session_*.json"):
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    session_date = datetime.fromisoformat(data['start_time']).date()
                    if session_date == today:
                        sessions.append(data)
                        total_cost += data.get('estimated_cost_usd', 0)
                        total_calls += data.get('kiro_calls', 0)
            except:
                continue
        
        report = {
            "date": today.isoformat(),
            "total_sessions": len(sessions),
            "total_cost_usd": total_cost,
            "total_kiro_calls": total_calls,
            "average_cost_per_session": total_cost / len(sessions) if sessions else 0,
            "sessions": sessions,
            "alerts": {
                "over_session_limit": len(sessions) > self.MAX_SESSIONS_PER_DAY,
                "over_cost_limit": total_cost > (self.MAX_COST_PER_SESSION * len(sessions)),
                "high_usage_sessions": [s for s in sessions if s.get('kiro_calls', 0) > self.MAX_KIRO_CALLS_PER_SESSION]
            }
        }
        
        return report
    
    def save_metrics_to_artifacts(self, session_path: Path, session: SessionMetrics):
        """Save metrics to session artifacts folder.
        
        Args:
            session_path: Path to session folder.
            session: Session metrics to save.
        """
        artifacts_dir = session_path / "03_artifacts"
        metrics_file = artifacts_dir / "usage_metrics.json"
        
        # Convert to dict
        data = asdict(session)
        data['start_time'] = session.start_time.isoformat()
        if session.end_time:
            data['end_time'] = session.end_time.isoformat()
        
        # Add daily context
        data['daily_report'] = self.generate_daily_report()
        
        with open(metrics_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        console.print("[STATS] Usage metrics saved to artifacts")
