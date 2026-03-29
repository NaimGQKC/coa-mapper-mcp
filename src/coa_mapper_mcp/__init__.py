__version__ = "0.1.0"

from .mapper import CoaMapper  # noqa: E402, F401

SUPPORTED_PLATFORMS = ["quickbooks", "xero", "wave", "sage", "freshbooks"]

__all__ = ["CoaMapper", "SUPPORTED_PLATFORMS", "__version__"]
