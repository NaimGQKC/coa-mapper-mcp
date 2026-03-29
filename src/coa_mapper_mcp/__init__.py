__version__ = "0.1.0"

from .mapper import CoaMapper

SUPPORTED_PLATFORMS = ["quickbooks", "xero", "wave", "sage", "freshbooks"]

__all__ = ["CoaMapper", "SUPPORTED_PLATFORMS", "__version__"]
