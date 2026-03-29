"""
Signal simulation for Infinity-Flow coins.

Each metal type has characteristic signal properties derived from real
nanomaterial physics:

* Gold  – plasmonic resonance; alpha-induced electron cascades create
           detectable EM micro-pulses.
* Silver – antimicrobial ion-release enhanced by radiolytic oxidative stress.
* Carbon hybrid – radiation-driven electrodeposition; dynamic shell growth
                  produces frequency-shift "computing" output.
* Platinum/Palladium – catalytic conversion of radiation energy to chemical
                        signal.
* Bismuth – low-melting alloy; acts as passive radiation absorber / shielding
             signal dampener.
* Copper/Nickel – structural conductivity; electrodeposition on CNT scaffold
                  generates resistive-change signals.
* Iridium/Ruthenium – extreme-durability catalytic electrochemical signals.

``SignalEmitter`` wraps a ``Coin`` and provides a ``emit()`` method that
returns a ``SignalEvent`` describing the simulated output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from infinity_flow.coin.models import Coin, MetalType


# ---------------------------------------------------------------------------
# Signal property tables
# ---------------------------------------------------------------------------

_SIGNAL_TYPE: dict[MetalType, str] = {
    MetalType.GOLD: "plasmonic_em_pulse",
    MetalType.SILVER: "antimicrobial_ion_release",
    MetalType.COPPER: "resistive_change",
    MetalType.NICKEL: "resistive_change",
    MetalType.PLATINUM: "catalytic_chemical",
    MetalType.PALLADIUM: "catalytic_chemical",
    MetalType.BISMUTH: "passive_shielding",
    MetalType.IRIDIUM: "electrochemical_catalytic",
    MetalType.RUTHENIUM: "electrochemical_catalytic",
    MetalType.CARBON_HYBRID: "frequency_shift_computing",
}

# Relative signal intensity factor per metal (arbitrary units, 0–1)
_INTENSITY: dict[MetalType, float] = {
    MetalType.GOLD: 0.95,
    MetalType.SILVER: 0.70,
    MetalType.COPPER: 0.55,
    MetalType.NICKEL: 0.50,
    MetalType.PLATINUM: 0.80,
    MetalType.PALLADIUM: 0.75,
    MetalType.BISMUTH: 0.20,
    MetalType.IRIDIUM: 0.90,
    MetalType.RUTHENIUM: 0.85,
    MetalType.CARBON_HYBRID: 0.88,
}

# Characteristic frequency band per metal (GHz, representative value)
_FREQUENCY_GHZ: dict[MetalType, float] = {
    MetalType.GOLD: 300.0,    # optical plasmonic (near-IR mapped to GHz equiv)
    MetalType.SILVER: 280.0,
    MetalType.COPPER: 5.8,
    MetalType.NICKEL: 4.5,
    MetalType.PLATINUM: 24.0,
    MetalType.PALLADIUM: 20.0,
    MetalType.BISMUTH: 0.1,
    MetalType.IRIDIUM: 60.0,
    MetalType.RUTHENIUM: 50.0,
    MetalType.CARBON_HYBRID: 2.4,
}


@dataclass
class SignalEvent:
    """The result of a single coin signal emission.

    Attributes
    ----------
    coin_id:
        Identifier of the emitting coin.
    metal:
        Metal type of the emitting coin.
    signal_type:
        Qualitative type of emission (e.g. ``"plasmonic_em_pulse"``).
    intensity:
        Relative intensity in the range [0, 1].
    frequency_ghz:
        Characteristic frequency of the emission in GHz.
    fingerprint_token:
        The coin's digital signature emitted as the verifiable token (only
        present when the shield is pulse-enabled).
    timestamp:
        ISO-8601 timestamp of the simulated emission.
    notes:
        Human-readable description of the physics model.
    """

    coin_id: str
    metal: MetalType
    signal_type: str
    intensity: float
    frequency_ghz: float
    fingerprint_token: Optional[str]
    timestamp: str
    notes: str = ""


class SignalEmitter:
    """Simulates signal emission from an Infinity-Flow coin.

    Parameters
    ----------
    coin:
        The coin to simulate.
    """

    def __init__(self, coin: Coin) -> None:
        self.coin = coin

    def emit(self) -> SignalEvent:
        """Produce a simulated ``SignalEvent`` from the coin.

        The intensity is modulated by the core activity and the shield
        thickness:  thicker shields attenuate the output.

        Returns
        -------
        SignalEvent
        """
        metal = self.coin.metal
        base_intensity = _INTENSITY[metal]

        # Shield attenuation: thicker shield → lower intensity
        # 100 nm gold leaf is the reference; scale proportionally.
        attenuation = min(self.coin.shield.thickness_nm / 100.0, 2.0)
        effective_intensity = round(
            base_intensity * self.coin.core.activity_bq / (attenuation * 2.0), 4
        )
        effective_intensity = min(max(effective_intensity, 0.0), 1.0)

        token: Optional[str] = None
        if self.coin.shield.pulse_enabled:
            token = self.coin.digital_signature

        return SignalEvent(
            coin_id=self.coin.coin_id,
            metal=metal,
            signal_type=_SIGNAL_TYPE[metal],
            intensity=effective_intensity,
            frequency_ghz=_FREQUENCY_GHZ[metal],
            fingerprint_token=token,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
            notes=self._notes(metal),
        )

    @staticmethod
    def _notes(metal: MetalType) -> str:
        descriptions = {
            MetalType.GOLD: (
                "Alpha particles ionise gold lattice electrons; secondary cascades "
                "induce plasmonic oscillations and detectable EM micro-pulses."
            ),
            MetalType.SILVER: (
                "Radiolysis-enhanced Ag⁺ ion release synergises with oxidative "
                "stress for localised antimicrobial / biofilm-disruption signalling."
            ),
            MetalType.COPPER: (
                "Electrodeposition on CNT scaffold modulated by radiolytic reducing "
                "conditions; resistive changes encode signal."
            ),
            MetalType.NICKEL: (
                "Structural Ni deposition on carbon nanotube backbone; magnetic "
                "susceptibility shift detectable as an AC signal."
            ),
            MetalType.PLATINUM: (
                "Pt catalyses radiolytic H₂O₂ decomposition → O₂ + chemical energy "
                "pulse detectable via gas-pressure transducer."
            ),
            MetalType.PALLADIUM: (
                "Pd hydrogen-absorption modulated by radiation-induced local H₂; "
                "pressure/conductivity shift acts as signal carrier."
            ),
            MetalType.BISMUTH: (
                "High-Z Bi passively absorbs scattered gammas; low-level "
                "bremsstrahlung forms a dampened background reference signal."
            ),
            MetalType.IRIDIUM: (
                "Extreme-durability Ir electrocatalyst; radiation drives micro-current "
                "spikes in the electrochemical double-layer."
            ),
            MetalType.RUTHENIUM: (
                "Ru-based dye-sensitiser analogue converts alpha-induced UV photons "
                "to electrochemical signal via MLCT transitions."
            ),
            MetalType.CARBON_HYBRID: (
                "Graphene-metal composite shell: radiation-driven metal deposition "
                "evolves nano-circuit topology → frequency-shift computing output."
            ),
        }
        return descriptions.get(metal, "")
