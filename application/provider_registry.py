"""
Registry for managing import/export providers.
"""
from typing import Dict, List
from application.import_export_interface import ImportProvider, ExportProvider


class ProviderRegistry:
    """Registry for storing and retrieving import/export providers."""
    _providers: Dict[str, object] = {}

    @classmethod
    def register(cls, name: str, provider: object) -> None:
        """Register a provider instance under a specific name."""
        if not isinstance(provider, (ImportProvider, ExportProvider)):
            raise ValueError("Provider must implement ImportProvider or ExportProvider")
        cls._providers[name.lower()] = provider

    @classmethod
    def get_provider(cls, name: str) -> object:
        """Retrieve a provider by name."""
        name = name.lower()
        if name not in cls._providers:
            raise ValueError(f"Provider '{name}' not found in registry.")
        return cls._providers[name]

    @classmethod
    def list_providers(cls) -> List[str]:
        """Return a list of registered provider names."""
        return list(cls._providers.keys())


# Global registry instance
registry = ProviderRegistry()