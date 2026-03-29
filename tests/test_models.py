"""Tests for infinity_flow.coin.models."""

import hashlib

import pytest

from infinity_flow.coin.models import (
    Coin,
    CoinTier,
    MetalType,
    NuclearCore,
    ProvenanceEvent,
    ShieldConfig,
    ShieldMaterial,
)


# ---------------------------------------------------------------------------
# NuclearCore
# ---------------------------------------------------------------------------


class TestNuclearCore:
    def test_fingerprint_is_deterministic(self):
        core = NuclearCore(
            isotope="Ra-224",
            activity_bq=2.0,
            particle_size_nm=5.0,
            encapsulation="CaCO3",
        )
        assert core.fingerprint == core.fingerprint

    def test_fingerprint_changes_with_isotope(self):
        core1 = NuclearCore(isotope="Ra-223", activity_bq=1.0, particle_size_nm=5.0, encapsulation="CaCO3")
        core2 = NuclearCore(isotope="Ra-224", activity_bq=1.0, particle_size_nm=5.0, encapsulation="CaCO3")
        assert core1.fingerprint != core2.fingerprint

    def test_fingerprint_changes_with_activity(self):
        core1 = NuclearCore(isotope="Ra-224", activity_bq=1.0, particle_size_nm=5.0, encapsulation="CaCO3")
        core2 = NuclearCore(isotope="Ra-224", activity_bq=2.0, particle_size_nm=5.0, encapsulation="CaCO3")
        assert core1.fingerprint != core2.fingerprint

    def test_fingerprint_is_sha256_hex(self):
        core = NuclearCore()
        assert len(core.fingerprint) == 64
        int(core.fingerprint, 16)  # must be valid hex


# ---------------------------------------------------------------------------
# ShieldConfig
# ---------------------------------------------------------------------------


class TestShieldConfig:
    def test_can_pulse_when_enabled(self):
        shield = ShieldConfig(pulse_enabled=True)
        assert shield.can_pulse() is True

    def test_cannot_pulse_when_disabled(self):
        shield = ShieldConfig(pulse_enabled=False)
        assert shield.can_pulse() is False


# ---------------------------------------------------------------------------
# Coin
# ---------------------------------------------------------------------------


class TestCoin:
    def _make_coin(self, metal: MetalType = MetalType.GOLD) -> Coin:
        return Coin(
            metal=metal,
            core=NuclearCore(isotope="Ra-224", activity_bq=2.0, particle_size_nm=5.0, encapsulation="CaCO3"),
            shield=ShieldConfig(material=ShieldMaterial.GOLD_LEAF, thickness_nm=100.0, pulse_enabled=True),
            tier=CoinTier.RARE,
            coin_id="test-coin-id",
        )

    def test_digital_signature_is_deterministic(self):
        coin = self._make_coin()
        assert coin.digital_signature == coin.digital_signature

    def test_digital_signature_depends_on_coin_id(self):
        coin1 = Coin(metal=MetalType.GOLD, coin_id="id-1")
        coin2 = Coin(metal=MetalType.GOLD, coin_id="id-2")
        assert coin1.digital_signature != coin2.digital_signature

    def test_digital_signature_depends_on_metal(self):
        coin1 = Coin(metal=MetalType.GOLD, coin_id="same-id")
        coin2 = Coin(metal=MetalType.SILVER, coin_id="same-id")
        assert coin1.digital_signature != coin2.digital_signature

    def test_verify_integrity_passes_for_fresh_coin(self):
        coin = self._make_coin()
        assert coin.verify_integrity() is True

    def test_add_provenance(self):
        coin = self._make_coin()
        coin.add_provenance("minted", "factory", "2026-01-01T00:00:00Z")
        assert len(coin.provenance) == 1
        assert coin.provenance[0].event_type == "minted"
        assert coin.provenance[0].actor == "factory"

    def test_summary_keys(self):
        coin = self._make_coin()
        s = coin.summary()
        for key in ("coin_id", "metal", "tier", "core", "shield", "digital_signature", "provenance_length"):
            assert key in s

    def test_summary_provenance_length(self):
        coin = self._make_coin()
        coin.add_provenance("minted", "factory", "2026-01-01T00:00:00Z")
        assert coin.summary()["provenance_length"] == 1

    def test_uuid_generated_when_not_specified(self):
        coin = Coin(metal=MetalType.SILVER)
        assert len(coin.coin_id) == 36  # UUID4 format

    def test_different_coins_get_different_ids(self):
        coins = [Coin(metal=MetalType.GOLD) for _ in range(10)]
        ids = {c.coin_id for c in coins}
        assert len(ids) == 10
