"""Tests for infinity_flow.coin.signal."""

import pytest

from infinity_flow.coin.models import Coin, CoinTier, MetalType, ShieldConfig
from infinity_flow.coin.signal import SignalEmitter, SignalEvent, _SIGNAL_TYPE, _INTENSITY


class TestSignalEmitter:
    def _coin(self, metal: MetalType, pulse: bool = True) -> Coin:
        return Coin(metal=metal, shield=ShieldConfig(pulse_enabled=pulse))

    def test_emit_returns_signal_event(self):
        coin = self._coin(MetalType.GOLD)
        event = SignalEmitter(coin).emit()
        assert isinstance(event, SignalEvent)

    def test_emit_coin_id_matches(self):
        coin = self._coin(MetalType.GOLD)
        event = SignalEmitter(coin).emit()
        assert event.coin_id == coin.coin_id

    def test_emit_metal_matches(self):
        coin = self._coin(MetalType.PLATINUM)
        event = SignalEmitter(coin).emit()
        assert event.metal == MetalType.PLATINUM

    def test_emit_signal_type_matches_table(self):
        for metal in MetalType:
            coin = self._coin(metal)
            event = SignalEmitter(coin).emit()
            assert event.signal_type == _SIGNAL_TYPE[metal]

    def test_emit_intensity_in_range(self):
        for metal in MetalType:
            coin = self._coin(metal)
            event = SignalEmitter(coin).emit()
            assert 0.0 <= event.intensity <= 1.0, f"{metal}: intensity out of range"

    def test_emit_token_present_when_pulse_enabled(self):
        coin = self._coin(MetalType.GOLD, pulse=True)
        event = SignalEmitter(coin).emit()
        assert event.fingerprint_token == coin.digital_signature

    def test_emit_token_none_when_pulse_disabled(self):
        coin = self._coin(MetalType.SILVER, pulse=False)
        event = SignalEmitter(coin).emit()
        assert event.fingerprint_token is None

    def test_emit_has_timestamp(self):
        coin = self._coin(MetalType.GOLD)
        event = SignalEmitter(coin).emit()
        assert event.timestamp  # non-empty string

    def test_emit_has_notes(self):
        coin = self._coin(MetalType.GOLD)
        event = SignalEmitter(coin).emit()
        assert len(event.notes) > 0

    def test_all_metals_produce_events(self):
        for metal in MetalType:
            coin = self._coin(metal)
            event = SignalEmitter(coin).emit()
            assert event.signal_type  # non-empty
