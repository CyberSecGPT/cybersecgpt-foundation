"""Public package interface for the CyberSecGPT foundation library."""

from pkgutil import extend_path

from .foundation import __version__

__path__ = extend_path(__path__, __name__)

__all__ = ["__version__"]
