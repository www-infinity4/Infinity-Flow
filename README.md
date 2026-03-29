# Infinity-Flow

**Trackable physical-digital coin toolkit** – a software system modelling the
Infinity-Flow apothecary coin concept: collectible coins that combine a
physical metal shell with a nanosized nuclear core, leaf shielding for
containment and on-demand pulse emission, and cryptographic provenance for
tamper-proof digital tracking.

---

## Concept

Each coin in the set is a hardware/signal hybrid:

| Layer | Physical | Digital |
|-------|----------|---------|
| **Shell** | Chosen metal (gold, silver, platinum, …) | Signal properties derived from material physics |
| **Core** | Nanosized radionuclide (Ra-223/224) in an encapsulated carrier | SHA-256 nuclear fingerprint → unique tamper-proof ID |
| **Shield** | Gold-leaf or graphene-gold composite at ~100 nm | Containment by default; configurable pulse window |
| **Provenance** | Serial number stamped on coin | Immutable chain of minted/transferred/authenticated events |

The ten metals in the starter set, each with a distinct signal role:

| Metal | Tier | Signal type | Pulse |
|-------|------|-------------|-------|
| Gold | Rare | Plasmonic EM pulse | ✓ |
| Silver | Uncommon | Antimicrobial ion release | — |
| Copper | Common | Resistive change | ✓ |
| Nickel | Common | Resistive change | ✓ |
| Platinum | Rare | Catalytic chemical | ✓ |
| Palladium | Rare | Catalytic chemical | ✓ |
| Bismuth | Uncommon | Passive shielding | — |
| Iridium | **Exotic** | Electrochemical catalytic | ✓ |
| Ruthenium | **Exotic** | Electrochemical catalytic | ✓ |
| Carbon Hybrid | Rare | Frequency-shift computing | ✓ |

---

## Project layout

```
src/infinity_flow/
    __init__.py
    cli.py               # Click CLI entry-point
    coin/
        __init__.py
        models.py        # Coin, NuclearCore, ShieldConfig, ProvenanceEvent
        apothecary.py    # ApothecarySet factory (full 10-coin starter set)
        tracker.py       # CoinTracker – in-memory provenance ledger
        signal.py        # SignalEmitter – physics-based signal simulation
tests/
    test_models.py
    test_apothecary.py
    test_tracker.py
    test_signal.py
    test_cli.py
```

---

## Installation

```bash
pip install -e .
```

---

## CLI usage

```bash
# List all coins in the default set
infinity-flow list

# Filter by collectible tier
infinity-flow list --tier exotic

# Inspect a single coin (JSON output)
infinity-flow show gold

# Mint a full set and dump JSON
infinity-flow mint --minted-by "My-Mint"

# Verify the digital integrity of every coin
infinity-flow verify

# Simulate a signal pulse
infinity-flow pulse gold
infinity-flow pulse carbon_hybrid
```

---

## Python API

```python
from infinity_flow import ApothecarySet, CoinTracker, SignalEmitter
from infinity_flow.coin.models import MetalType

# Mint the complete apothecary set
apothecary = ApothecarySet.create(minted_by="My-Mint")

# Register all coins in a tracker (provenance ledger)
tracker = CoinTracker(name="Gallery-1")
tracker.register_many(apothecary.all_coins())

# Authenticate a coin
gold = apothecary.get(MetalType.GOLD)
ok = tracker.authenticate(gold.coin_id)       # True

# Pulse the signal (returns the digital-signature token)
token = tracker.pulse(gold.coin_id)           # 64-char hex string

# Simulate signal emission
event = SignalEmitter(gold).emit()
print(event.signal_type)    # "plasmonic_em_pulse"
print(event.intensity)      # 0.95
print(event.frequency_ghz)  # 300.0
```

---

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Safety note

This repository is a **software simulation** of the Infinity-Flow coin
concept.  Any real-world work involving radioactive materials (Ra-223, Ra-224,
etc.) must be conducted in compliance with all applicable national and
international regulations governing radioactive substances.
