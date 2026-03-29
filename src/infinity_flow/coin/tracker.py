"""
Digital tracking and provenance ledger for Infinity-Flow coins.

``CoinTracker`` acts as an in-memory ledger.  Each registered coin is stored
by its ``coin_id``.  Events (transfer, authentication, pulse) can be appended
to any tracked coin.  The tracker also provides a ``verify`` helper that
re-computes the digital signature and confirms it matches the stored value.

In a production deployment this ledger would be backed by a blockchain or
distributed-ledger service; the signature already provides the tamper-proof
linkage needed for on-chain anchoring.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from infinity_flow.coin.models import Coin, MetalType


def _now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


class CoinTracker:
    """In-memory ledger for tracking a collection of Infinity-Flow coins.

    Parameters
    ----------
    name:
        Optional human-readable name for this tracker instance
        (e.g. ``"Gallery-1"``).
    """

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self._registry: Dict[str, Coin] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, coin: Coin, actor: str = "system") -> None:
        """Add *coin* to the ledger and stamp a ``registered`` provenance event.

        Raises
        ------
        ValueError
            If a coin with the same ``coin_id`` is already registered.
        """
        if coin.coin_id in self._registry:
            raise ValueError(
                f"Coin {coin.coin_id!r} is already registered in tracker "
                f"{self.name!r}."
            )
        coin.add_provenance(
            event_type="registered",
            actor=actor,
            timestamp=_now(),
            notes=f"Registered in tracker '{self.name}'.",
        )
        self._registry[coin.coin_id] = coin

    def register_many(self, coins: List[Coin], actor: str = "system") -> None:
        """Register a list of coins in a single call."""
        for coin in coins:
            self.register(coin, actor=actor)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get(self, coin_id: str) -> Coin:
        """Return the coin with the given ``coin_id``.

        Raises
        ------
        KeyError
            If no coin with that id is tracked.
        """
        if coin_id not in self._registry:
            raise KeyError(f"Coin {coin_id!r} not found in tracker {self.name!r}.")
        return self._registry[coin_id]

    def list_coins(self) -> List[Coin]:
        """Return all tracked coins."""
        return list(self._registry.values())

    def find_by_metal(self, metal: MetalType) -> List[Coin]:
        """Return all tracked coins whose primary metal matches *metal*."""
        return [c for c in self._registry.values() if c.metal == metal]

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def transfer(
        self,
        coin_id: str,
        from_actor: str,
        to_actor: str,
        notes: str = "",
    ) -> None:
        """Record an ownership transfer event on the coin's provenance chain."""
        coin = self.get(coin_id)
        coin.add_provenance(
            event_type="transferred",
            actor=from_actor,
            timestamp=_now(),
            notes=f"Transferred to {to_actor!r}. {notes}".strip(),
        )

    def authenticate(self, coin_id: str, actor: str = "system") -> bool:
        """Verify the coin's digital signature and record the result.

        Returns
        -------
        bool
            *True* if the coin's signature is valid, *False* otherwise.
        """
        coin = self.get(coin_id)
        valid = coin.verify_integrity()
        coin.add_provenance(
            event_type="authenticated",
            actor=actor,
            timestamp=_now(),
            notes=f"Integrity check {'passed' if valid else 'FAILED'}.",
        )
        return valid

    def pulse(self, coin_id: str, actor: str = "system") -> Optional[str]:
        """Trigger a signal pulse from the coin (if its shield allows it).

        Returns the coin's ``digital_signature`` on success (to be used as the
        externally readable verification token), or *None* if the coin's shield
        does not support pulsing.
        """
        coin = self.get(coin_id)
        if not coin.shield.can_pulse():
            coin.add_provenance(
                event_type="pulse_attempted",
                actor=actor,
                timestamp=_now(),
                notes="Pulse attempted but shield is not pulse-enabled.",
            )
            return None
        coin.add_provenance(
            event_type="pulsed",
            actor=actor,
            timestamp=_now(),
            notes="Signal pulsed outward for external verification.",
        )
        return coin.digital_signature

    # ------------------------------------------------------------------
    # Bulk verification
    # ------------------------------------------------------------------

    def verify_all(self) -> Dict[str, bool]:
        """Return a mapping of {coin_id: integrity_valid} for all tracked coins."""
        return {cid: coin.verify_integrity() for cid, coin in self._registry.items()}

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._registry)

    def __repr__(self) -> str:
        return f"CoinTracker(name={self.name!r}, coins={len(self)})"
