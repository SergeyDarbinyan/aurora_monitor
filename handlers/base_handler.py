from abc import ABC, abstractmethod
import logging

class BaseHandler(ABC):
    """Abstract base class for all handlers."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def handle(self, *args, **kwargs):
        """Abstract method to be implemented by concrete handlers."""
        pass