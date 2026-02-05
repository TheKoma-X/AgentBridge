"""
Enhanced logging and monitoring for AgentBridge
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
import json
import traceback
from pathlib import Path


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Structure for a log entry."""
    timestamp: datetime
    level: LogLevel
    source: str
    message: str
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        result = {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "source": self.source,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id
        return result


class AgentBridgeLogger:
    """Enhanced logger for AgentBridge with correlation tracking."""
    
    def __init__(self, name: str = "AgentBridge", level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self.handlers: list = []
        self.correlation_stack: list = []
        
        # Set up basic logging
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Avoid adding handlers multiple times
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def set_level(self, level: LogLevel):
        """Set the logging level."""
        self.level = level
        self.logger.setLevel(getattr(logging, level.value))
    
    def push_correlation_id(self, correlation_id: str):
        """Push a correlation ID onto the stack."""
        self.correlation_stack.append(correlation_id)
    
    def pop_correlation_id(self) -> Optional[str]:
        """Pop a correlation ID from the stack."""
        if self.correlation_stack:
            return self.correlation_stack.pop()
        return None
    
    def get_current_correlation_id(self) -> Optional[str]:
        """Get the current correlation ID."""
        if self.correlation_stack:
            return self.correlation_stack[-1]
        return None
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if a log level should be logged."""
        level_values = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4
        }
        return level_values[level] >= level_values[self.level]
    
    def _log(self, level: LogLevel, source: str, message: str, 
             details: Optional[Dict[str, Any]] = None, 
             correlation_id: Optional[str] = None):
        """Internal logging method."""
        if not self._should_log(level):
            return
            
        # Use provided correlation ID or get from stack
        corr_id = correlation_id or self.get_current_correlation_id()
        
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            source=source,
            message=message,
            details=details,
            correlation_id=corr_id
        )
        
        # Log to standard logger
        self.logger.log(
            getattr(logging, level.value),
            f"[{source}] {message}"
        )
        
        # Add to any custom handlers
        for handler in self.handlers:
            handler.handle(log_entry)
    
    def debug(self, source: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log a debug message."""
        self._log(LogLevel.DEBUG, source, message, details)
    
    def info(self, source: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log an info message."""
        self._log(LogLevel.INFO, source, message, details)
    
    def warning(self, source: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log a warning message."""
        self._log(LogLevel.WARNING, source, message, details)
    
    def error(self, source: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log an error message."""
        self._log(LogLevel.ERROR, source, message, details)
    
    def critical(self, source: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log a critical message."""
        self._log(LogLevel.CRITICAL, source, message, details)
    
    def exception(self, source: str, message: str, 
                  exc_info: Optional[Exception] = None, 
                  details: Optional[Dict[str, Any]] = None):
        """Log an exception with traceback."""
        if exc_info is None:
            exc_info = sys.exc_info()[1]  # Get current exception
        
        error_details = {
            "exception_type": type(exc_info).__name__ if exc_info else None,
            "exception_message": str(exc_info) if exc_info else None,
            "traceback": traceback.format_exc() if exc_info else None
        }
        
        if details:
            error_details.update(details)
        
        self.error(source, message, error_details)


class FileLogHandler:
    """Log handler that writes to a file."""
    
    def __init__(self, filepath: str, max_size_mb: int = 10):
        self.filepath = Path(filepath)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Ensure the log file exists."""
        if not self.filepath.parent.exists():
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            self.filepath.touch()
    
    def handle(self, log_entry: LogEntry):
        """Handle a log entry."""
        # Rotate file if too large
        if self.filepath.stat().st_size > self.max_size_bytes:
            self.rotate_log()
        
        with open(self.filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry.to_dict()) + '\n')
    
    def rotate_log(self):
        """Rotate the log file."""
        backup_path = self.filepath.with_suffix('.old')
        if backup_path.exists():
            backup_path.unlink()
        self.filepath.rename(backup_path)


class MetricsCollector:
    """Collect metrics about bridge operations."""
    
    def __init__(self):
        self.counters = {
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
            'connections': 0,
            'disconnections': 0,
        }
        self.timers = {
            'avg_response_time': [],
            'avg_processing_time': [],
        }
        self.framework_stats = {}
    
    def increment_counter(self, counter_name: str, value: int = 1):
        """Increment a counter."""
        if counter_name not in self.counters:
            self.counters[counter_name] = 0
        self.counters[counter_name] += value
    
    def record_timer(self, timer_name: str, value: float):
        """Record a timing value."""
        if timer_name not in self.timers:
            self.timers[timer_name] = []
        self.timers[timer_name].append(value)
    
    def update_framework_stats(self, framework: str, operation: str, success: bool = True):
        """Update stats for a specific framework."""
        if framework not in self.framework_stats:
            self.framework_stats[framework] = {
                'operations': 0,
                'successes': 0,
                'failures': 0
            }
        
        self.framework_stats[framework]['operations'] += 1
        if success:
            self.framework_stats[framework]['successes'] += 1
        else:
            self.framework_stats[framework]['failures'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        metrics = {
            'counters': self.counters.copy(),
            'timers': {}
        }
        
        # Calculate averages for timers
        for timer_name, values in self.timers.items():
            if values:
                metrics['timers'][timer_name] = {
                    'count': len(values),
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
            else:
                metrics['timers'][timer_name] = {
                    'count': 0,
                    'average': 0,
                    'min': 0,
                    'max': 0
                }
        
        metrics['framework_stats'] = self.framework_stats.copy()
        return metrics


# Global logger instance
_bridge_logger: Optional[AgentBridgeLogger] = None
_metrics_collector: Optional[MetricsCollector] = None


def get_logger() -> AgentBridgeLogger:
    """Get the global logger instance."""
    global _bridge_logger
    if _bridge_logger is None:
        _bridge_logger = AgentBridgeLogger()
    return _bridge_logger


def set_logger(logger: AgentBridgeLogger) -> None:
    """Set the global logger instance."""
    global _bridge_logger
    _bridge_logger = logger


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def set_metrics_collector(collector: MetricsCollector) -> None:
    """Set the global metrics collector instance."""
    global _metrics_collector
    _metrics_collector = collector
