"""
Smart Flight Deck Companion - Checklist Loader
Loads and manages checklist JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .checklist import Checklist

logger = logging.getLogger(__name__)


class ChecklistLoader:
    """
    Loads checklist definitions from JSON files.

    Supports aircraft-specific checklists with fallback to default.
    """

    def __init__(self, checklists_dir: Optional[Path] = None):
        """
        Initialize loader.

        Args:
            checklists_dir: Directory containing checklist JSON files
        """
        if checklists_dir is None:
            # Default to bridge/checklists/
            self._dir = Path(__file__).parent.parent / "checklists"
        else:
            self._dir = Path(checklists_dir)

        self._cache: Dict[str, Dict[str, Checklist]] = {}  # aircraft -> {checklist_id -> Checklist}
        self._default_checklists: Dict[str, Checklist] = {}

        # Load default checklists on init
        self._load_default()

    def _load_default(self):
        """Load default checklist file."""
        default_path = self._dir / "default.json"
        if default_path.exists():
            self._default_checklists = self._load_file(default_path, "default")
            logger.info(f"Loaded {len(self._default_checklists)} default checklists")

    def _load_file(self, path: Path, aircraft: str) -> Dict[str, Checklist]:
        """Load checklists from a JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            checklists = {}
            aircraft_name = data.get("aircraft", aircraft)

            for checklist_id, checklist_data in data.get("checklists", {}).items():
                try:
                    checklist = Checklist.from_dict(checklist_id, checklist_data, aircraft_name)
                    checklists[checklist_id] = checklist
                    logger.debug(f"Loaded checklist: {checklist_id} ({len(checklist.items)} items)")
                except Exception as e:
                    logger.error(f"Failed to parse checklist {checklist_id}: {e}")

            return checklists

        except Exception as e:
            logger.error(f"Failed to load checklist file {path}: {e}")
            return {}

    def get_checklists_for_aircraft(self, aircraft_title: str) -> Dict[str, Checklist]:
        """
        Get all checklists for an aircraft.

        Args:
            aircraft_title: Aircraft title from simulator

        Returns:
            Dictionary of checklist_id -> Checklist
        """
        # Check cache first
        cache_key = aircraft_title.lower()
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Try to find aircraft-specific file
        profile_id = self._match_aircraft(aircraft_title)

        if profile_id and profile_id != "default":
            profile_path = self._dir / f"{profile_id}.json"
            if profile_path.exists():
                checklists = self._load_file(profile_path, profile_id)
                if checklists:
                    self._cache[cache_key] = checklists
                    logger.info(f"Loaded {len(checklists)} checklists for {aircraft_title}")
                    return checklists

        # Fall back to default
        self._cache[cache_key] = self._default_checklists
        return self._default_checklists

    def get_checklist(self, aircraft_title: str, checklist_id: str) -> Optional[Checklist]:
        """
        Get a specific checklist for an aircraft.

        Args:
            aircraft_title: Aircraft title
            checklist_id: Checklist identifier (e.g., "before_takeoff")

        Returns:
            Checklist or None if not found
        """
        checklists = self.get_checklists_for_aircraft(aircraft_title)
        return checklists.get(checklist_id)

    def list_checklists(self, aircraft_title: str) -> List[Dict]:
        """
        List available checklists for an aircraft.

        Args:
            aircraft_title: Aircraft title

        Returns:
            List of checklist info dicts
        """
        checklists = self.get_checklists_for_aircraft(aircraft_title)

        return [
            {
                "id": checklist_id,
                "name": checklist.name,
                "phase": checklist.phase,
                "items_count": checklist.total_items,
            }
            for checklist_id, checklist in checklists.items()
        ]

    def list_all_profiles(self) -> List[str]:
        """List all available checklist profiles."""
        profiles = []
        if self._dir.exists():
            for path in self._dir.glob("*.json"):
                profiles.append(path.stem)
        return profiles

    def _match_aircraft(self, aircraft_title: str) -> Optional[str]:
        """Match aircraft title to checklist profile."""
        title_lower = aircraft_title.lower()

        # A320 variants
        if any(x in title_lower for x in ["a320", "a319", "a321", "a32n"]):
            if "fenix" in title_lower:
                return "a320_fenix"
            elif any(x in title_lower for x in ["flybywire", "fbw", "a32nx"]):
                return "a320_fbw"
            return "a320_generic"

        # Boeing 737
        if "737" in title_lower:
            if "pmdg" in title_lower:
                return "b737_pmdg"
            return "b737_generic"

        # Boeing 747
        if "747" in title_lower:
            return "b747_generic"

        # Boeing 787
        if "787" in title_lower:
            return "b787_generic"

        # Cessna 172
        if "172" in title_lower or ("cessna" in title_lower and "skyhawk" in title_lower):
            return "c172"

        # CRJ
        if "crj" in title_lower:
            return "crj"

        # Default
        return "default"

    def reload(self):
        """Reload all checklists from disk."""
        self._cache.clear()
        self._default_checklists.clear()
        self._load_default()
        logger.info("Checklists reloaded")


class ChecklistManager:
    """
    High-level checklist manager.

    Combines loader with engine for easier use.
    """

    def __init__(self):
        from .checklist import ChecklistEngine

        self._loader = ChecklistLoader()
        self._engine = ChecklistEngine()
        self._current_aircraft: str = ""

    @property
    def engine(self):
        """Get checklist engine."""
        return self._engine

    @property
    def loader(self):
        """Get checklist loader."""
        return self._loader

    def set_aircraft(self, aircraft_title: str):
        """Set current aircraft."""
        self._current_aircraft = aircraft_title

    def list_available(self) -> List[Dict]:
        """List available checklists for current aircraft."""
        return self._loader.list_checklists(self._current_aircraft)

    def start_checklist(self, checklist_id: str):
        """Start a checklist by ID."""
        checklist = self._loader.get_checklist(self._current_aircraft, checklist_id)
        if not checklist:
            return None
        return self._engine.start(checklist)

    def find_checklist_by_name(self, name: str) -> Optional[str]:
        """
        Find checklist ID by name (fuzzy match).

        Args:
            name: Checklist name or partial name

        Returns:
            Checklist ID or None
        """
        name_lower = name.lower()
        checklists = self._loader.get_checklists_for_aircraft(self._current_aircraft)

        # Exact match first
        for checklist_id, checklist in checklists.items():
            if checklist_id.lower() == name_lower:
                return checklist_id
            if checklist.name.lower() == name_lower:
                return checklist_id

        # Partial match
        for checklist_id, checklist in checklists.items():
            if name_lower in checklist_id.lower():
                return checklist_id
            if name_lower in checklist.name.lower():
                return checklist_id

        # Common aliases
        aliases = {
            "before start": "before_start",
            "after start": "after_start",
            "before taxi": "before_taxi",
            "before takeoff": "before_takeoff",
            "after takeoff": "after_takeoff",
            "descent": "descent",
            "approach": "approach",
            "before landing": "before_landing",
            "after landing": "after_landing",
            "shutdown": "shutdown",
            "cockpit prep": "cockpit_preparation",
            "cockpit preparation": "cockpit_preparation",
        }

        if name_lower in aliases:
            return aliases[name_lower]

        return None
