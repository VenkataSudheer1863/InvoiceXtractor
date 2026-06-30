"""Base Agent Class"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent's primary function"""
        pass
    
    def log_info(self, message: str):
        self.logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str):
        self.logger.error(f"[{self.name}] {message}")
    
    def log_warning(self, message: str):
        self.logger.warning(f"[{self.name}] {message}")
