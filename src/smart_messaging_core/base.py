"""Base protocol abstractions for smart_messaging_core."""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class BaseProtocolConfig:
    """Base configuration for a messaging protocol client."""

    enabled: bool = True


class BaseProtocolClient(ABC):
    """Unified protocol client interface used by MessagingClient."""

    supports_publish: bool = False
    supports_subscribe: bool = False
    config_type = BaseProtocolConfig

    def __init__(self, config: BaseProtocolConfig) -> None:
        self._validate_config(config)
        self._config = config

    @classmethod
    def _validate_config(cls, config: BaseProtocolConfig) -> None:
        if not isinstance(config, cls.config_type):
            raise TypeError(
                f"{cls.__name__} requires {cls.config_type.__name__}, got {type(config).__name__}"
            )

    def publish(self, channel: str, payload: dict[str, Any]) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__} does not support publish")

    def subscribe(self, channel: str, handler: Callable[[dict[str, Any]], None]) -> None:
        raise NotImplementedError(f"{self.__class__.__name__} does not support subscribe")

    def close(self) -> None:
        """Release protocol resources; default is no-op."""
        return None
