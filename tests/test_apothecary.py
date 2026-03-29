"""Tests for infinity_flow.coin.apothecary."""

import pytest

from infinity_flow.coin.apothecary import ApothecarySet
from infinity_flow.coin.models import CoinTier, MetalType


class TestApothecarySet:
    def setup_method(self):
        self.apothecary = ApothecarySet.create(minted_by="test-mint")

    def test_contains_all_metal_types(self):
        metals = {c.metal for c in self.apothecary.all_coins()}
        assert metals == set(MetalType)

    def test_ten_coins_in_set(self):
        assert len(self.apothecary.all_coins()) == len(MetalType)

    def test_get_returns_correct_coin(self):
        gold = self.apothecary.get(MetalType.GOLD)
        assert gold.metal == MetalType.GOLD

    def test_get_missing_key_raises(self):
        # Force a bad key by bypassing the enum
        with pytest.raises(KeyError):
            bad_set = ApothecarySet({})
            bad_set.get(MetalType.GOLD)

    def test_by_tier_exotic(self):
        exotic = self.apothecary.by_tier(CoinTier.EXOTIC)
        assert all(c.tier == CoinTier.EXOTIC for c in exotic)
        assert len(exotic) == 2  # Iridium + Ruthenium

    def test_by_tier_rare(self):
        rare = self.apothecary.by_tier(CoinTier.RARE)
        metals = {c.metal for c in rare}
        assert MetalType.GOLD in metals
        assert MetalType.PLATINUM in metals

    def test_each_coin_has_mint_provenance(self):
        for coin in self.apothecary.all_coins():
            assert any(e.event_type == "minted" for e in coin.provenance)
            assert any(e.actor == "test-mint" for e in coin.provenance)

    def test_verify_all_passes(self):
        results = self.apothecary.verify_all()
        assert all(results.values()), "Some coins failed integrity verification"

    def test_summaries_returns_list_of_dicts(self):
        summaries = self.apothecary.summaries()
        assert isinstance(summaries, list)
        assert len(summaries) == len(MetalType)
        for s in summaries:
            assert isinstance(s, dict)
            assert "digital_signature" in s

    def test_each_coin_has_unique_id(self):
        ids = {c.coin_id for c in self.apothecary.all_coins()}
        assert len(ids) == len(MetalType)

    def test_iridium_is_exotic(self):
        ir = self.apothecary.get(MetalType.IRIDIUM)
        assert ir.tier == CoinTier.EXOTIC

    def test_bismuth_is_uncommon(self):
        bi = self.apothecary.get(MetalType.BISMUTH)
        assert bi.tier == CoinTier.UNCOMMON

    def test_gold_shield_pulse_enabled(self):
        gold = self.apothecary.get(MetalType.GOLD)
        assert gold.shield.pulse_enabled is True

    def test_silver_shield_pulse_disabled(self):
        silver = self.apothecary.get(MetalType.SILVER)
        assert silver.shield.pulse_enabled is False
