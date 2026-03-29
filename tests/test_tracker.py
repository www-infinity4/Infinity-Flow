"""Tests for infinity_flow.coin.tracker."""

import pytest

from infinity_flow.coin.models import Coin, MetalType
from infinity_flow.coin.tracker import CoinTracker


def _make_coin(metal: MetalType = MetalType.GOLD) -> Coin:
    return Coin(metal=metal)


class TestCoinTracker:
    def setup_method(self):
        self.tracker = CoinTracker(name="test-tracker")

    def test_repr(self):
        assert "test-tracker" in repr(self.tracker)
        assert "0" in repr(self.tracker)

    def test_len_empty(self):
        assert len(self.tracker) == 0

    def test_register_adds_coin(self):
        coin = _make_coin()
        self.tracker.register(coin)
        assert len(self.tracker) == 1

    def test_register_stamps_provenance(self):
        coin = _make_coin()
        self.tracker.register(coin, actor="factory")
        assert any(e.event_type == "registered" for e in coin.provenance)

    def test_register_duplicate_raises(self):
        coin = _make_coin()
        self.tracker.register(coin)
        with pytest.raises(ValueError):
            self.tracker.register(coin)

    def test_get_returns_correct_coin(self):
        coin = _make_coin()
        self.tracker.register(coin)
        retrieved = self.tracker.get(coin.coin_id)
        assert retrieved is coin

    def test_get_missing_raises(self):
        with pytest.raises(KeyError):
            self.tracker.get("non-existent-id")

    def test_register_many(self):
        coins = [_make_coin(MetalType.GOLD), _make_coin(MetalType.SILVER)]
        self.tracker.register_many(coins)
        assert len(self.tracker) == 2

    def test_list_coins(self):
        coin1 = _make_coin(MetalType.GOLD)
        coin2 = _make_coin(MetalType.SILVER)
        self.tracker.register_many([coin1, coin2])
        listed = self.tracker.list_coins()
        assert len(listed) == 2

    def test_find_by_metal(self):
        gold = _make_coin(MetalType.GOLD)
        silver = _make_coin(MetalType.SILVER)
        self.tracker.register_many([gold, silver])
        result = self.tracker.find_by_metal(MetalType.GOLD)
        assert len(result) == 1
        assert result[0].metal == MetalType.GOLD

    def test_transfer_adds_provenance(self):
        coin = _make_coin()
        self.tracker.register(coin)
        self.tracker.transfer(coin.coin_id, from_actor="alice", to_actor="bob")
        assert any(e.event_type == "transferred" for e in coin.provenance)

    def test_authenticate_valid_coin(self):
        coin = _make_coin()
        self.tracker.register(coin)
        result = self.tracker.authenticate(coin.coin_id)
        assert result is True

    def test_authenticate_adds_provenance(self):
        coin = _make_coin()
        self.tracker.register(coin)
        self.tracker.authenticate(coin.coin_id)
        assert any(e.event_type == "authenticated" for e in coin.provenance)

    def test_pulse_pulse_enabled_returns_token(self):
        from infinity_flow.coin.models import ShieldConfig
        coin = Coin(metal=MetalType.GOLD, shield=ShieldConfig(pulse_enabled=True))
        self.tracker.register(coin)
        token = self.tracker.pulse(coin.coin_id)
        assert token == coin.digital_signature

    def test_pulse_disabled_returns_none(self):
        from infinity_flow.coin.models import ShieldConfig
        coin = Coin(metal=MetalType.SILVER, shield=ShieldConfig(pulse_enabled=False))
        self.tracker.register(coin)
        token = self.tracker.pulse(coin.coin_id)
        assert token is None

    def test_pulse_disabled_adds_attempted_provenance(self):
        from infinity_flow.coin.models import ShieldConfig
        coin = Coin(metal=MetalType.SILVER, shield=ShieldConfig(pulse_enabled=False))
        self.tracker.register(coin)
        self.tracker.pulse(coin.coin_id)
        assert any(e.event_type == "pulse_attempted" for e in coin.provenance)

    def test_verify_all(self):
        coins = [_make_coin(MetalType.GOLD), _make_coin(MetalType.SILVER)]
        self.tracker.register_many(coins)
        results = self.tracker.verify_all()
        assert all(results.values())
