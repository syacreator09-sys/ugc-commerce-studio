from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from ..offers import ProductOfferSnapshot


class DiscoveryCandidate(BaseModel):
    provider: str
    offer: ProductOfferSnapshot
    raw: dict[str, Any] = Field(default_factory=dict)


class DiscoveryProvider(ABC):
    name: str

    @abstractmethod
    def discover(self, payloads: list[dict[str, Any]]) -> list[DiscoveryCandidate]:
        raise NotImplementedError
