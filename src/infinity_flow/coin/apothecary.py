"""
Apothecary collectible-set factory.

Provides ``ApothecarySet``, a convenience class that pre-builds the full
starter set of signal-emitting coins described in the Infinity-Flow concept:

    Gold      – baseline plasmonic signal / high-Z amplifier
    Silver    – antimicrobial ion-release synergy
    Copper    – conductivity / structural growth on carbon scaffold
    Nickel    – structural electrodeposition partner for carbon nanotubes
    Platinum  – catalytic signal conversion (radiation → chemical energy)
    Palladium – catalysis / hydrogen-storage signal modulation
    Bismuth   – low-melting alloy, radiation shielding, medical imaging
    Iridium   – extreme durability / catalysis (exotic tier)
    Ruthenium – extreme catalysis / electrochemical signalling (exotic tier)
    Carbon Hybrid – dynamic growth shell; radiation-driven metal deposition

Each coin is stamped with a ``minted`` provenance event and a pre-configured
``ShieldConfig`` / ``NuclearCore`` appropriate for its design role.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from infinity_flow.coin.models import (
    Coin,
    CoinTier,
    MetalType,
    NuclearCore,
    ShieldConfig,
    ShieldMaterial,
)

# ---------------------------------------------------------------------------
# Default core / shield presets per metal
# ---------------------------------------------------------------------------

_CORE_PRESETS: Dict[MetalType, NuclearCore] = {
    MetalType.GOLD: NuclearCore(
        isotope="Ra-224",
        activity_bq=2.0,
        particle_size_nm=5.0,
        encapsulation="CaCO3",
    ),
    MetalType.SILVER: NuclearCore(
        isotope="Ra-224",
        activity_bq=1.5,
        particle_size_nm=4.0,
        encapsulation="CaCO3",
    ),
    MetalType.COPPER: NuclearCore(
        isotope="Ra-223",
        activity_bq=1.0,
        particle_size_nm=6.0,
        encapsulation="GdVO4",
    ),
    MetalType.NICKEL: NuclearCore(
        isotope="Ra-223",
        activity_bq=1.0,
        particle_size_nm=6.0,
        encapsulation="GdVO4",
    ),
    MetalType.PLATINUM: NuclearCore(
        isotope="Ra-224",
        activity_bq=3.0,
        particle_size_nm=4.5,
        encapsulation="CaCO3",
    ),
    MetalType.PALLADIUM: NuclearCore(
        isotope="Ra-224",
        activity_bq=2.5,
        particle_size_nm=4.5,
        encapsulation="CaCO3",
    ),
    MetalType.BISMUTH: NuclearCore(
        isotope="Ra-223",
        activity_bq=1.0,
        particle_size_nm=7.0,
        encapsulation="GdVO4",
    ),
    MetalType.IRIDIUM: NuclearCore(
        isotope="Ra-224",
        activity_bq=5.0,
        particle_size_nm=3.5,
        encapsulation="CaCO3",
    ),
    MetalType.RUTHENIUM: NuclearCore(
        isotope="Ra-224",
        activity_bq=4.0,
        particle_size_nm=3.5,
        encapsulation="CaCO3",
    ),
    MetalType.CARBON_HYBRID: NuclearCore(
        isotope="Ra-224",
        activity_bq=2.0,
        particle_size_nm=5.0,
        encapsulation="CNT",
    ),
}

_SHIELD_PRESETS: Dict[MetalType, ShieldConfig] = {
    MetalType.GOLD: ShieldConfig(
        material=ShieldMaterial.GOLD_LEAF,
        thickness_nm=100.0,
        pulse_enabled=True,
    ),
    MetalType.SILVER: ShieldConfig(
        material=ShieldMaterial.GOLD_LEAF,
        thickness_nm=100.0,
        pulse_enabled=False,
    ),
    MetalType.COPPER: ShieldConfig(
        material=ShieldMaterial.GRAPHENE_GOLD,
        thickness_nm=80.0,
        pulse_enabled=True,
    ),
    MetalType.NICKEL: ShieldConfig(
        material=ShieldMaterial.GRAPHENE_GOLD,
        thickness_nm=80.0,
        pulse_enabled=True,
    ),
    MetalType.PLATINUM: ShieldConfig(
        material=ShieldMaterial.GOLD_LEAF,
        thickness_nm=120.0,
        pulse_enabled=True,
    ),
    MetalType.PALLADIUM: ShieldConfig(
        material=ShieldMaterial.GOLD_LEAF,
        thickness_nm=110.0,
        pulse_enabled=True,
    ),
    MetalType.BISMUTH: ShieldConfig(
        material=ShieldMaterial.GRAPHENE,
        thickness_nm=60.0,
        pulse_enabled=False,
    ),
    MetalType.IRIDIUM: ShieldConfig(
        material=ShieldMaterial.GOLD_LEAF,
        thickness_nm=150.0,
        pulse_enabled=True,
    ),
    MetalType.RUTHENIUM: ShieldConfig(
        material=ShieldMaterial.GOLD_LEAF,
        thickness_nm=140.0,
        pulse_enabled=True,
    ),
    MetalType.CARBON_HYBRID: ShieldConfig(
        material=ShieldMaterial.GRAPHENE,
        thickness_nm=50.0,
        pulse_enabled=True,
    ),
}

_TIER_MAP: Dict[MetalType, CoinTier] = {
    MetalType.GOLD: CoinTier.RARE,
    MetalType.SILVER: CoinTier.UNCOMMON,
    MetalType.COPPER: CoinTier.COMMON,
    MetalType.NICKEL: CoinTier.COMMON,
    MetalType.PLATINUM: CoinTier.RARE,
    MetalType.PALLADIUM: CoinTier.RARE,
    MetalType.BISMUTH: CoinTier.UNCOMMON,
    MetalType.IRIDIUM: CoinTier.EXOTIC,
    MetalType.RUTHENIUM: CoinTier.EXOTIC,
    MetalType.CARBON_HYBRID: CoinTier.RARE,
}


def _mint_timestamp() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


class ApothecarySet:
    """The complete apothecary collectible set of Infinity-Flow coins.

    Usage
    -----
    >>> apothecary = ApothecarySet.create()
    >>> gold = apothecary.get(MetalType.GOLD)
    >>> print(gold.digital_signature)

    Parameters
    ----------
    minted_by:
        Identifier of the entity that minted this set (stamped into each
        coin's initial provenance event).
    """

    def __init__(self, coins: Dict[MetalType, Coin]) -> None:
        self._coins: Dict[MetalType, Coin] = coins

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(cls, minted_by: str = "Infinity-Flow-Mint") -> "ApothecarySet":
        """Mint a complete apothecary set with all ten coin types."""
        ts = _mint_timestamp()
        coins: Dict[MetalType, Coin] = {}
        for metal in MetalType:
            coin = Coin(
                metal=metal,
                core=_CORE_PRESETS[metal],
                shield=_SHIELD_PRESETS[metal],
                tier=_TIER_MAP[metal],
            )
            coin.add_provenance(
                event_type="minted",
                actor=minted_by,
                timestamp=ts,
                notes=f"Initial mint of {metal.value} coin.",
            )
            coins[metal] = coin
        return cls(coins)

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def get(self, metal: MetalType) -> Coin:
        """Return the coin for the given metal type."""
        return self._coins[metal]

    def all_coins(self) -> List[Coin]:
        """Return all coins in the set, ordered by MetalType definition."""
        return list(self._coins.values())

    def by_tier(self, tier: CoinTier) -> List[Coin]:
        """Return all coins of the given collectible tier."""
        return [c for c in self._coins.values() if c.tier == tier]

    def summaries(self) -> List[dict]:
        """Return JSON-serialisable summaries of every coin."""
        return [c.summary() for c in self.all_coins()]

    def verify_all(self) -> Dict[str, bool]:
        """Verify integrity of every coin; returns {coin_id: is_valid}."""
        return {c.coin_id: c.verify_integrity() for c in self.all_coins()}
