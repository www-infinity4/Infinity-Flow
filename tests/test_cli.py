"""Tests for the CLI entry-point."""

import json

from click.testing import CliRunner

from infinity_flow.cli import main
from infinity_flow.coin.models import MetalType


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_list_exits_ok(self):
        result = self.runner.invoke(main, ["list"])
        assert result.exit_code == 0

    def test_list_contains_metal_names(self):
        result = self.runner.invoke(main, ["list"])
        for metal in MetalType:
            assert metal.value in result.output

    def test_list_tier_filter_exotic(self):
        result = self.runner.invoke(main, ["list", "--tier", "exotic"])
        assert result.exit_code == 0
        assert "iridium" in result.output
        assert "ruthenium" in result.output
        assert "gold" not in result.output

    def test_show_gold_exits_ok(self):
        result = self.runner.invoke(main, ["show", "gold"])
        assert result.exit_code == 0

    def test_show_gold_returns_json(self):
        result = self.runner.invoke(main, ["show", "gold"])
        data = json.loads(result.output)
        assert data["metal"] == "gold"
        assert "digital_signature" in data

    def test_mint_returns_json_list(self):
        result = self.runner.invoke(main, ["mint"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == len(MetalType)

    def test_verify_exits_ok(self):
        result = self.runner.invoke(main, ["verify"])
        assert result.exit_code == 0

    def test_verify_contains_ok(self):
        result = self.runner.invoke(main, ["verify"])
        assert "OK" in result.output

    def test_pulse_gold_exits_ok(self):
        result = self.runner.invoke(main, ["pulse", "gold"])
        assert result.exit_code == 0

    def test_pulse_gold_contains_signal_type(self):
        result = self.runner.invoke(main, ["pulse", "gold"])
        assert "plasmonic_em_pulse" in result.output

    def test_pulse_silver_no_token(self):
        result = self.runner.invoke(main, ["pulse", "silver"])
        assert result.exit_code == 0
        assert "shield not pulse-enabled" in result.output
