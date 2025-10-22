"""Logging configuration for the multi-agent customer care system."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        
        # Add color to logger name based on component
        logger_name = record.name
        if 'agent' in logger_name:
            record.name = f"{Fore.BLUE}{logger_name}{Style.RESET_ALL}"
        elif 'orchestrator' in logger_name:
            record.name = f"{Fore.MAGENTA}{logger_name}{Style.RESET_ALL}"
        elif 'planner' in logger_name:
            record.name = f"{Fore.CYAN}{logger_name}{Style.RESET_ALL}"
        elif 'tools' in logger_name:
            record.name = f"{Fore.GREEN}{logger_name}{Style.RESET_ALL}"
        
        return super().format(record)

def setup_logging(log_level: str = "INFO", log_to_file: bool = True):
    """Set up logging configuration for the application."""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if log_to_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(
            logs_dir / f"customer_care_{timestamp}.log",
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    # Demo-specific loggers
    logging.getLogger("agents").setLevel(logging.INFO)
    logging.getLogger("orchestrator").setLevel(logging.INFO)
    logging.getLogger("planner").setLevel(logging.INFO)
    logging.getLogger("tools").setLevel(logging.INFO)
    
    logger.info(f"Logging configured - Level: {log_level}, File logging: {log_to_file}")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)