"""
Command-line interface for the Infinity-Flow coin toolkit.

Usage examples
--------------
List all coins in the default apothecary set::

    $ infinity-flow list

Show details of a single coin by metal type::

    $ infinity-flow show gold

Mint a complete set and dump JSON summaries::

    $ infinity-flow mint

Verify the integrity of every coin in the set::

    $ infinity-flow verify

Simulate a signal pulse from a coin::

    $ infinity-flow pulse gold
"""

from __future__ import annotations

import json

import click

from infinity_flow.coin.apothecary import ApothecarySet
from infinity_flow.coin.models import CoinTier, MetalType
from infinity_flow.coin.signal import SignalEmitter
from infinity_flow.coin.tracker import CoinTracker


def _build_set_and_tracker() -> tuple[ApothecarySet, CoinTracker]:
    apothecary = ApothecarySet.create(minted_by="CLI-Mint")
    tracker = CoinTracker(name="CLI-Tracker")
    tracker.register_many(apothecary.all_coins(), actor="CLI-Mint")
    return apothecary, tracker


@click.group()
def main() -> None:
    """Infinity-Flow – trackable physical-digital coin toolkit."""


@main.command("list")
@click.option(
    "--tier",
    type=click.Choice([t.value for t in CoinTier]),
    default=None,
    help="Filter coins by collectible tier.",
)
def list_coins(tier: str | None) -> None:
    """List all coins in the default apothecary set."""
    apothecary = ApothecarySet.create()
    coins = (
        apothecary.by_tier(CoinTier(tier)) if tier else apothecary.all_coins()
    )
    click.echo(f"{'Metal':<16} {'Tier':<10} {'Isotope':<8} {'Activity (Bq)':<14} {'Pulse'}")
    click.echo("-" * 62)
    for coin in coins:
        click.echo(
            f"{coin.metal.value:<16} "
            f"{coin.tier.value:<10} "
            f"{coin.core.isotope:<8} "
            f"{coin.core.activity_bq:<14.1f} "
            f"{'yes' if coin.shield.pulse_enabled else 'no'}"
        )


@main.command("show")
@click.argument("metal", type=click.Choice([m.value for m in MetalType]))
def show_coin(metal: str) -> None:
    """Show full details for the coin of the given METAL type."""
    apothecary = ApothecarySet.create()
    coin = apothecary.get(MetalType(metal))
    click.echo(json.dumps(coin.summary(), indent=2))


@main.command("mint")
@click.option("--minted-by", default="CLI-Mint", help="Minter identifier.")
def mint_set(minted_by: str) -> None:
    """Mint a complete apothecary set and print JSON summaries."""
    apothecary = ApothecarySet.create(minted_by=minted_by)
    click.echo(json.dumps(apothecary.summaries(), indent=2))


@main.command("verify")
def verify_set() -> None:
    """Verify the digital integrity of every coin in the set."""
    apothecary = ApothecarySet.create()
    results = apothecary.verify_all()
    all_ok = all(results.values())
    for coin_id, valid in results.items():
        status = click.style("OK", fg="green") if valid else click.style("FAIL", fg="red")
        click.echo(f"{coin_id} … {status}")
    if all_ok:
        click.echo(click.style("\nAll coins passed integrity verification.", fg="green"))
    else:
        click.echo(click.style("\nSome coins failed verification!", fg="red"), err=True)


@main.command("pulse")
@click.argument("metal", type=click.Choice([m.value for m in MetalType]))
def pulse_coin(metal: str) -> None:
    """Simulate a signal pulse from the coin of the given METAL type."""
    apothecary = ApothecarySet.create()
    coin = apothecary.get(MetalType(metal))
    emitter = SignalEmitter(coin)
    event = emitter.emit()
    click.echo(f"Coin      : {event.coin_id}")
    click.echo(f"Metal     : {event.metal.value}")
    click.echo(f"Signal    : {event.signal_type}")
    click.echo(f"Intensity : {event.intensity}")
    click.echo(f"Freq (GHz): {event.frequency_ghz}")
    if event.fingerprint_token:
        click.echo(f"Token     : {event.fingerprint_token}")
    else:
        click.echo("Token     : (shield not pulse-enabled)")
    click.echo(f"Notes     : {event.notes}")
