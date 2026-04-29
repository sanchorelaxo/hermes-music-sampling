"""Ardour Automator — headless Ardour automation via Lua scripts."""
from .pipeline import run_script, probe, export, ARDour_AVAILABLE, ARDour_CLI, ARDour_VERSION
from . import arpeggiators

# Re-export convenience arpeggiator runners at the top level
from .arpeggiators import (
    render_simple_arp,
    render_barlow_arp,
    render_raptor_arp,
    run_simple_arp,
    run_barlow_arp,
    run_raptor_arp,
)

__all__ = [
    "run_script",
    "probe",
    "export",
    "ARDour_AVAILABLE",
    "ARDour_CLI",
    "ARDour_VERSION",
    "arpeggiators",
    "render_simple_arp",
    "render_barlow_arp",
    "render_raptor_arp",
    "run_simple_arp",
    "run_barlow_arp",
    "run_raptor_arp",
]
