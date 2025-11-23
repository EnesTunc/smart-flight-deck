"""
Smart Flight Deck Companion - MobiFlight WASM Installer
Automatically detects MSFS installation and installs MobiFlight WASM module.

Supports:
- Microsoft Store version
- Steam version
- Custom installation paths
"""

import os
import logging
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


# MobiFlight WASM GitHub release info
MOBIFLIGHT_WASM_REPO = "MobiFlight/MobiFlight-WASM-Module"
MOBIFLIGHT_WASM_RELEASE_URL = (
    "https://github.com/MobiFlight/MobiFlight-WASM-Module/releases/latest/download/"
    "mobiflight-event-module.zip"
)
MOBIFLIGHT_WASM_FOLDER_NAME = "mobiflight-event-module"
MOBIFLIGHT_WASM_VERSION_FILE = "layout.json"


class MSFSEdition(Enum):
    """MSFS installation types."""

    STEAM = "steam"
    MS_STORE = "ms_store"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


@dataclass
class MSFSInstallation:
    """Information about an MSFS installation."""

    edition: MSFSEdition
    packages_path: Path
    community_path: Path
    official_path: Optional[Path] = None
    user_cfg_path: Optional[Path] = None


@dataclass
class WASMStatus:
    """MobiFlight WASM installation status."""

    installed: bool
    path: Optional[Path] = None
    version: Optional[str] = None
    needs_update: bool = False
    error_message: str = ""


class MSFSDetector:
    """
    Detects MSFS installation paths.

    Checks multiple possible locations for both Steam and MS Store versions.
    """

    # Known MSFS paths
    STEAM_PATHS = [
        Path(os.environ.get("APPDATA", "")) / "Microsoft Flight Simulator",
    ]

    MS_STORE_PATHS = [
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Packages"
        / "Microsoft.FlightSimulator_8wekyb3d8bbwe"
        / "LocalCache",
    ]

    # MSFS 2024 paths
    MSFS2024_STEAM_PATHS = [
        Path(os.environ.get("APPDATA", "")) / "Microsoft Flight Simulator 2024",
    ]

    MSFS2024_MS_STORE_PATHS = [
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Packages"
        / "Microsoft.Limitless_8wekyb3d8bbwe"
        / "LocalCache",
    ]

    def __init__(self):
        self._installations: List[MSFSInstallation] = []

    def detect_all(self) -> List[MSFSInstallation]:
        """
        Detect all MSFS installations.

        Returns:
            List of found installations
        """
        self._installations.clear()

        # Check MSFS 2020 paths
        for steam_path in self.STEAM_PATHS:
            install = self._check_path(steam_path, MSFSEdition.STEAM)
            if install:
                self._installations.append(install)

        for ms_path in self.MS_STORE_PATHS:
            install = self._check_path(ms_path, MSFSEdition.MS_STORE)
            if install:
                self._installations.append(install)

        # Check MSFS 2024 paths
        for steam_path in self.MSFS2024_STEAM_PATHS:
            install = self._check_path(steam_path, MSFSEdition.STEAM)
            if install:
                self._installations.append(install)

        for ms_path in self.MSFS2024_MS_STORE_PATHS:
            install = self._check_path(ms_path, MSFSEdition.MS_STORE)
            if install:
                self._installations.append(install)

        # Try to read from UserCfg.opt for custom paths
        for install in self._installations:
            self._parse_user_cfg(install)

        logger.info(f"Found {len(self._installations)} MSFS installation(s)")
        return self._installations

    def _check_path(
        self, base_path: Path, edition: MSFSEdition
    ) -> Optional[MSFSInstallation]:
        """
        Check if a path contains valid MSFS configuration.

        Args:
            base_path: Path to check
            edition: Expected MSFS edition

        Returns:
            MSFSInstallation if valid, None otherwise
        """
        if not base_path.exists():
            return None

        # Look for UserCfg.opt which indicates MSFS config folder
        user_cfg = base_path / "UserCfg.opt"
        if not user_cfg.exists():
            return None

        # Parse UserCfg.opt to find packages path
        packages_path = self._get_packages_path_from_cfg(user_cfg)

        if packages_path and packages_path.exists():
            community_path = packages_path / "Community"
            official_path = packages_path / "Official"

            # Create Community folder if it doesn't exist
            community_path.mkdir(parents=True, exist_ok=True)

            return MSFSInstallation(
                edition=edition,
                packages_path=packages_path,
                community_path=community_path,
                official_path=official_path if official_path.exists() else None,
                user_cfg_path=user_cfg,
            )

        return None

    def _get_packages_path_from_cfg(self, user_cfg: Path) -> Optional[Path]:
        """
        Parse UserCfg.opt to find InstalledPackagesPath.

        Args:
            user_cfg: Path to UserCfg.opt

        Returns:
            Packages path or None
        """
        try:
            with open(user_cfg, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("InstalledPackagesPath"):
                        # Format: InstalledPackagesPath "C:\Path\To\Packages"
                        parts = line.split('"')
                        if len(parts) >= 2:
                            return Path(parts[1])
        except Exception as e:
            logger.error(f"Error reading UserCfg.opt: {e}")

        return None

    def _parse_user_cfg(self, install: MSFSInstallation):
        """
        Parse additional settings from UserCfg.opt.

        Args:
            install: Installation to update
        """
        if not install.user_cfg_path or not install.user_cfg_path.exists():
            return

        # Could extract more settings here if needed
        pass

    def get_primary_installation(self) -> Optional[MSFSInstallation]:
        """
        Get the primary (most likely used) MSFS installation.

        Returns:
            Primary installation or None
        """
        if not self._installations:
            self.detect_all()

        if self._installations:
            # Prefer MSFS 2024 if available, otherwise first found
            for install in self._installations:
                if "2024" in str(install.packages_path):
                    return install
            return self._installations[0]

        return None


class WASMInstaller:
    """
    Installs and manages MobiFlight WASM module.
    """

    def __init__(self, detector: Optional[MSFSDetector] = None):
        """
        Initialize installer.

        Args:
            detector: MSFS detector instance (creates one if not provided)
        """
        self._detector = detector or MSFSDetector()
        self._installation: Optional[MSFSInstallation] = None

    def check_status(
        self, installation: Optional[MSFSInstallation] = None
    ) -> WASMStatus:
        """
        Check MobiFlight WASM installation status.

        Args:
            installation: MSFS installation to check (auto-detects if None)

        Returns:
            WASMStatus with current state
        """
        if installation:
            self._installation = installation
        else:
            self._installation = self._detector.get_primary_installation()

        if not self._installation:
            return WASMStatus(
                installed=False,
                error_message="MSFS installation not found"
            )

        wasm_path = self._installation.community_path / MOBIFLIGHT_WASM_FOLDER_NAME

        if not wasm_path.exists():
            return WASMStatus(
                installed=False,
                error_message="MobiFlight WASM not installed"
            )

        # Check version
        version = self._get_installed_version(wasm_path)

        return WASMStatus(
            installed=True,
            path=wasm_path,
            version=version,
            needs_update=False  # TODO: Compare with latest release
        )

    def _get_installed_version(self, wasm_path: Path) -> Optional[str]:
        """
        Get installed WASM module version.

        Args:
            wasm_path: Path to WASM module folder

        Returns:
            Version string or None
        """
        layout_file = wasm_path / "layout.json"
        if not layout_file.exists():
            return None

        try:
            import json
            with open(layout_file, "r", encoding="utf-8") as f:
                layout = json.load(f)
                # Layout.json might have version info in content
                return layout.get("version", "unknown")
        except Exception as e:
            logger.warning(f"Could not read WASM version: {e}")
            return "unknown"

    async def install(
        self,
        installation: Optional[MSFSInstallation] = None,
        progress_callback: Optional[callable] = None
    ) -> Tuple[bool, str]:
        """
        Install MobiFlight WASM module.

        Args:
            installation: Target MSFS installation
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (success, message)
        """
        if installation:
            self._installation = installation
        else:
            self._installation = self._detector.get_primary_installation()

        if not self._installation:
            return False, "MSFS installation not found"

        try:
            if progress_callback:
                progress_callback("Downloading MobiFlight WASM module...", 10)

            # Download WASM module
            zip_path = await self._download_wasm()

            if not zip_path:
                return False, "Failed to download MobiFlight WASM"

            if progress_callback:
                progress_callback("Extracting files...", 50)

            # Extract to Community folder
            success = self._extract_wasm(zip_path)

            # Cleanup temp file
            try:
                os.unlink(zip_path)
            except Exception:
                pass

            if success:
                if progress_callback:
                    progress_callback("Installation complete!", 100)
                return True, "MobiFlight WASM installed successfully"
            else:
                return False, "Failed to extract WASM module"

        except Exception as e:
            logger.error(f"WASM installation failed: {e}")
            return False, f"Installation error: {str(e)}"

    async def _download_wasm(self) -> Optional[str]:
        """
        Download MobiFlight WASM module from GitHub.

        Returns:
            Path to downloaded zip file or None
        """
        try:
            import httpx

            # Create temp file
            temp_dir = tempfile.gettempdir()
            zip_path = os.path.join(temp_dir, "mobiflight-wasm.zip")

            async with httpx.AsyncClient(follow_redirects=True) as client:
                logger.info(f"Downloading from {MOBIFLIGHT_WASM_RELEASE_URL}")

                response = await client.get(
                    MOBIFLIGHT_WASM_RELEASE_URL,
                    timeout=60.0
                )

                if response.status_code == 200:
                    with open(zip_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Downloaded WASM module to {zip_path}")
                    return zip_path
                else:
                    logger.error(f"Download failed: HTTP {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Download error: {e}")
            return None

    def _extract_wasm(self, zip_path: str) -> bool:
        """
        Extract WASM module to Community folder.

        Args:
            zip_path: Path to downloaded zip file

        Returns:
            True if successful
        """
        if not self._installation:
            return False

        try:
            target_path = self._installation.community_path / MOBIFLIGHT_WASM_FOLDER_NAME

            # Remove existing installation
            if target_path.exists():
                shutil.rmtree(target_path)

            # Extract zip
            with zipfile.ZipFile(zip_path, "r") as zf:
                # Check zip structure - might have root folder or not
                names = zf.namelist()

                if names and names[0].startswith(MOBIFLIGHT_WASM_FOLDER_NAME):
                    # Has root folder, extract directly
                    zf.extractall(self._installation.community_path)
                else:
                    # No root folder, create it
                    target_path.mkdir(parents=True, exist_ok=True)
                    zf.extractall(target_path)

            logger.info(f"Extracted WASM module to {target_path}")
            return target_path.exists()

        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return False

    def uninstall(self) -> Tuple[bool, str]:
        """
        Uninstall MobiFlight WASM module.

        Returns:
            Tuple of (success, message)
        """
        if not self._installation:
            self._installation = self._detector.get_primary_installation()

        if not self._installation:
            return False, "MSFS installation not found"

        wasm_path = self._installation.community_path / MOBIFLIGHT_WASM_FOLDER_NAME

        if not wasm_path.exists():
            return True, "MobiFlight WASM is not installed"

        try:
            shutil.rmtree(wasm_path)
            logger.info(f"Uninstalled WASM module from {wasm_path}")
            return True, "MobiFlight WASM uninstalled successfully"
        except Exception as e:
            logger.error(f"Uninstall error: {e}")
            return False, f"Uninstall error: {str(e)}"


class WASMManager:
    """
    High-level manager for WASM installation and status.

    Provides simple interface for the main application.
    """

    def __init__(self):
        self._detector = MSFSDetector()
        self._installer = WASMInstaller(self._detector)
        self._status: Optional[WASMStatus] = None

    def get_msfs_installations(self) -> List[MSFSInstallation]:
        """Get all detected MSFS installations."""
        return self._detector.detect_all()

    def check_wasm_status(self) -> WASMStatus:
        """Check current WASM installation status."""
        self._status = self._installer.check_status()
        return self._status

    async def ensure_wasm_installed(
        self,
        auto_install: bool = False,
        progress_callback: Optional[callable] = None
    ) -> Tuple[bool, str]:
        """
        Ensure WASM is installed, optionally installing automatically.

        Args:
            auto_install: If True, install automatically if not found
            progress_callback: Progress update callback

        Returns:
            Tuple of (is_ready, message)
        """
        status = self.check_wasm_status()

        if status.installed and not status.needs_update:
            return True, f"MobiFlight WASM is installed at {status.path}"

        if not status.installed:
            if auto_install:
                return await self._installer.install(
                    progress_callback=progress_callback
                )
            else:
                return False, (
                    "MobiFlight WASM module is required for advanced aircraft support. "
                    "Would you like to install it?"
                )

        if status.needs_update:
            if auto_install:
                return await self._installer.install(
                    progress_callback=progress_callback
                )
            else:
                return True, (
                    f"MobiFlight WASM update available. "
                    f"Current: {status.version}"
                )

        return True, "WASM status check complete"

    async def install_wasm(
        self,
        progress_callback: Optional[callable] = None
    ) -> Tuple[bool, str]:
        """
        Install or update WASM module.

        Args:
            progress_callback: Progress update callback

        Returns:
            Tuple of (success, message)
        """
        return await self._installer.install(progress_callback=progress_callback)

    def uninstall_wasm(self) -> Tuple[bool, str]:
        """Uninstall WASM module."""
        return self._installer.uninstall()

    @property
    def is_wasm_available(self) -> bool:
        """Check if WASM is installed and ready."""
        if self._status is None:
            self.check_wasm_status()
        return self._status.installed if self._status else False

    @property
    def community_folder(self) -> Optional[Path]:
        """Get MSFS Community folder path."""
        install = self._detector.get_primary_installation()
        return install.community_path if install else None
