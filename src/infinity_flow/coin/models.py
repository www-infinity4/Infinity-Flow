"""
Coin data models.

Each physical coin in the Infinity-Flow apothecary set is described by:
  - A metal composition (determines signal properties and biomedical role)
  - A shielding configuration (leaf material + thickness)
  - A unique nuclear fingerprint (cryptographic digest used as a tamper-proof ID)
  - A provenance record (chain of ownership events)

The radium-core concept is represented in software as a ``NuclearCore`` with
configurable isotope and activity level.  All real-world radioactive handling
must comply with applicable regulations; this model is a design/simulation
abstraction only.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class MetalType(str, Enum):
    """Primary shell metal for each coin in the apothecary set."""

    GOLD = "gold"
    SILVER = "silver"
    COPPER = "copper"
    NICKEL = "nickel"
    PLATINUM = "platinum"
    PALLADIUM = "palladium"
    BISMUTH = "bismuth"
    IRIDIUM = "iridium"
    RUTHENIUM = "ruthenium"
    CARBON_HYBRID = "carbon_hybrid"


class ShieldMaterial(str, Enum):
    """Leaf-shielding material that wraps the core cavity."""

    GOLD_LEAF = "gold_leaf"
    GRAPHENE_GOLD = "graphene_gold"
    GRAPHENE = "graphene"


class CoinTier(str, Enum):
    """Collectible tier – mirrors the apothecary rarity grading."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EXOTIC = "exotic"


@dataclass
class ShieldConfig:
    """Leaf-shielding configuration around the core cavity.

    Parameters
    ----------
    material:
        Shielding material (e.g. gold leaf, graphene-gold composite).
    thickness_nm:
        Nominal shield thickness in nanometres.  Gold leaf at ~100 nm fully
        contains alpha particles; thinner graphene composites allow controlled
        pulse transmission.
    pulse_enabled:
        When *True* the shield exposes a transmission window on demand,
        allowing the nuclear fingerprint signal to be read externally for
        verification.
    """

    material: ShieldMaterial = ShieldMaterial.GOLD_LEAF
    thickness_nm: float = 100.0
    pulse_enabled: bool = False

    def can_pulse(self) -> bool:
        """Return whether this config supports on-demand pulse emission."""
        return self.pulse_enabled


@dataclass
class NuclearCore:
    """Software model of the nanosized radionuclide core.

    This class represents the design parameters of the physical core.  The
    ``fingerprint`` property derives a deterministic, collision-resistant hex
    digest from the core parameters; it serves as the tamper-proof identifier
    that is linked to the coin's blockchain record.

    Parameters
    ----------
    isotope:
        Radionuclide label (e.g. ``"Ra-224"``).
    activity_bq:
        Nominal activity in Becquerel.  For nanosized cores used in targeted
        alpha therapy prototypes this is typically in the range 1–10 Bq.
    particle_size_nm:
        Mean diameter of the encapsulated nanoparticle carrier (nm).
    encapsulation:
        Carrier matrix material (e.g. ``"CaCO3"``, ``"GdVO4"``).
    """

    isotope: str = "Ra-224"
    activity_bq: float = 1.0
    particle_size_nm: float = 5.0
    encapsulation: str = "CaCO3"

    @property
    def fingerprint(self) -> str:
        """Deterministic hex fingerprint derived from core parameters."""
        raw = (
            f"{self.isotope}|{self.activity_bq:.6f}"
            f"|{self.particle_size_nm:.3f}|{self.encapsulation}"
        )
        return hashlib.sha256(raw.encode()).hexdigest()


@dataclass
class ProvenanceEvent:
    """A single entry in a coin's immutable provenance chain.

    Parameters
    ----------
    event_type:
        Verb describing the event (e.g. ``"minted"``, ``"transferred"``,
        ``"authenticated"``).
    actor:
        Identifier of the entity responsible for the event.
    timestamp:
        ISO-8601 timestamp string.
    notes:
        Optional free-text notes.
    """

    event_type: str
    actor: str
    timestamp: str
    notes: str = ""


@dataclass
class Coin:
    """A trackable physical-digital coin.

    The coin combines:
    * A physical shell made from a chosen metal (``metal``).
    * A nano-core with a nuclear fingerprint (``core``).
    * A leaf-shielding layer for containment and optional pulse emission
      (``shield``).
    * A digital provenance chain (``provenance``).
    * A ``tier`` that represents collectible rarity.

    A UUID-based ``coin_id`` uniquely identifies each instance.  The
    ``digital_signature`` ties the coin_id to the core fingerprint so that any
    tampering with the physical parameters invalidates the digital record.

    Parameters
    ----------
    metal:
        Primary shell metal.
    core:
        Nuclear core design parameters.
    shield:
        Leaf-shielding configuration.
    tier:
        Collectible rarity tier.
    coin_id:
        Auto-generated UUID (overridable for deterministic testing).
    provenance:
        Ordered list of provenance events.  Normally starts with a ``minted``
        event.
    """

    metal: MetalType
    core: NuclearCore = field(default_factory=NuclearCore)
    shield: ShieldConfig = field(default_factory=ShieldConfig)
    tier: CoinTier = CoinTier.COMMON
    coin_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provenance: List[ProvenanceEvent] = field(default_factory=list)

    @property
    def digital_signature(self) -> str:
        """Collision-resistant signature binding coin_id to core fingerprint."""
        raw = f"{self.coin_id}|{self.core.fingerprint}|{self.metal.value}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def add_provenance(
        self,
        event_type: str,
        actor: str,
        timestamp: str,
        notes: str = "",
    ) -> None:
        """Append a new provenance event to the chain."""
        self.provenance.append(
            ProvenanceEvent(
                event_type=event_type,
                actor=actor,
                timestamp=timestamp,
                notes=notes,
            )
        )

    def verify_integrity(self) -> bool:
        """Return *True* if the digital signature is consistent with the coin
        parameters (i.e. no tampering has occurred)."""
        raw = f"{self.coin_id}|{self.core.fingerprint}|{self.metal.value}"
        expected = hashlib.sha256(raw.encode()).hexdigest()
        return self.digital_signature == expected

    def summary(self) -> dict:
        """Return a JSON-serialisable summary of the coin."""
        return {
            "coin_id": self.coin_id,
            "metal": self.metal.value,
            "tier": self.tier.value,
            "core": {
                "isotope": self.core.isotope,
                "activity_bq": self.core.activity_bq,
                "particle_size_nm": self.core.particle_size_nm,
                "encapsulation": self.core.encapsulation,
                "fingerprint": self.core.fingerprint,
            },
            "shield": {
                "material": self.shield.material.value,
                "thickness_nm": self.shield.thickness_nm,
                "pulse_enabled": self.shield.pulse_enabled,
            },
            "digital_signature": self.digital_signature,
            "provenance_length": len(self.provenance),
        }
