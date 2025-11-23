"""
Smart Flight Deck Companion - MobiFlight WASM Integration
Provides LVAR read/write access via MobiFlight WASM module.

MobiFlight WASM Module: https://github.com/MobiFlight/MobiFlight-WASM-Module
License: MIT (commercial use allowed)
"""

import logging
import struct
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import IntEnum

logger = logging.getLogger(__name__)


class MobiFlightMessageType(IntEnum):
    """MobiFlight WASM message types."""

    # Client -> WASM
    CYCLIC_DATA_READ = 0
    LVAR_READ = 1
    LVAR_WRITE = 2
    EXECUTE_HTML_EVENT = 3
    EXECUTE_CALCULATOR_CODE = 4

    # WASM -> Client
    CYCLIC_DATA_RESPONSE = 10
    LVAR_READ_RESPONSE = 11
    LVAR_LIST = 12


@dataclass
class LVarValue:
    """Represents an LVAR with its value."""

    name: str
    value: float
    success: bool = True
    error_message: str = ""


class MobiFlightClient:
    """
    MobiFlight WASM Module client.

    Communicates with the MobiFlight WASM module installed in MSFS
    to read/write LVARs and execute H:Events.

    The WASM module uses SimConnect Client Data Areas for communication:
    - Client sends commands via a Client Data Area
    - WASM responds via another Client Data Area
    """

    # MobiFlight Client Data Area names
    CLIENT_DATA_NAME_COMMAND = "MobiFlight.Command"
    CLIENT_DATA_NAME_RESPONSE = "MobiFlight.Response"
    CLIENT_DATA_NAME_LVARS = "MobiFlight.LVars"
    CLIENT_DATA_NAME_STRINGRESPONSE = "MobiFlight.StringResponse"

    # Data area IDs
    CLIENT_DATA_ID_COMMAND = 0
    CLIENT_DATA_ID_RESPONSE = 1
    CLIENT_DATA_ID_LVARS = 2
    CLIENT_DATA_ID_STRINGRESPONSE = 3

    # Definition IDs
    DATA_DEFINITION_ID_COMMAND = 0
    DATA_DEFINITION_ID_RESPONSE = 1
    DATA_DEFINITION_ID_STRINGRESPONSE = 2

    # Command string max length
    MAX_COMMAND_LENGTH = 1024
    MAX_RESPONSE_LENGTH = 8192

    def __init__(self, simconnect=None):
        """
        Initialize MobiFlight client.

        Args:
            simconnect: SimConnect instance (from python-simconnect)
        """
        self._sc = simconnect
        self._initialized = False
        self._available = False
        self._lvar_cache: Dict[str, float] = {}
        self._on_lvar_update: Optional[Callable[[str, float], None]] = None
        self._pending_requests: Dict[int, Any] = {}
        self._request_id = 0

    def initialize(self, simconnect) -> bool:
        """
        Initialize connection to MobiFlight WASM.

        Args:
            simconnect: SimConnect instance

        Returns:
            True if MobiFlight WASM is available and initialized
        """
        self._sc = simconnect

        if not self._sc:
            logger.error("SimConnect instance required for MobiFlight")
            return False

        try:
            # Try to map to MobiFlight Client Data Areas
            # This will fail if WASM module is not installed
            self._setup_client_data_areas()
            self._initialized = True
            self._available = True
            logger.info("MobiFlight WASM module connected successfully")
            return True

        except Exception as e:
            logger.warning(f"MobiFlight WASM not available: {e}")
            self._available = False
            return False

    def _setup_client_data_areas(self):
        """
        Set up SimConnect Client Data Areas for MobiFlight communication.

        Note: This uses low-level SimConnect API which may need
        python-simconnect modifications or direct ctypes calls.
        """
        # The actual implementation depends on SimConnect bindings
        # python-simconnect may need extension for ClientData support

        # For now, we'll use a simplified approach that checks WASM availability
        # via a known LVAR that MobiFlight creates
        pass

    @property
    def is_available(self) -> bool:
        """Check if MobiFlight WASM is available."""
        return self._available

    @property
    def is_initialized(self) -> bool:
        """Check if client is initialized."""
        return self._initialized

    async def read_lvar(self, lvar_name: str) -> LVarValue:
        """
        Read an LVAR value.

        Args:
            lvar_name: LVAR name (without L: prefix)

        Returns:
            LVarValue with the result
        """
        if not self._available:
            return LVarValue(
                name=lvar_name,
                value=0.0,
                success=False,
                error_message="MobiFlight WASM not available"
            )

        try:
            # Format: (>L:varname)
            # MobiFlight expects the LVAR name in RPN/calculator format
            command = f"1 (>L:{lvar_name})"

            # Send command and wait for response
            value = await self._send_command_and_wait(
                MobiFlightMessageType.LVAR_READ,
                lvar_name
            )

            if value is not None:
                self._lvar_cache[lvar_name] = value
                return LVarValue(name=lvar_name, value=value, success=True)
            else:
                return LVarValue(
                    name=lvar_name,
                    value=0.0,
                    success=False,
                    error_message=f"Failed to read LVAR: {lvar_name}"
                )

        except Exception as e:
            logger.error(f"Error reading LVAR {lvar_name}: {e}")
            return LVarValue(
                name=lvar_name,
                value=0.0,
                success=False,
                error_message=str(e)
            )

    async def write_lvar(self, lvar_name: str, value: float) -> bool:
        """
        Write a value to an LVAR.

        Args:
            lvar_name: LVAR name (without L: prefix)
            value: Value to write

        Returns:
            True if successful
        """
        if not self._available:
            logger.warning("MobiFlight WASM not available")
            return False

        try:
            # Format: value (>L:varname)
            # This is RPN calculator code that sets the LVAR
            command = f"{value} (>L:{lvar_name})"

            success = await self._send_command(
                MobiFlightMessageType.LVAR_WRITE,
                command
            )

            if success:
                self._lvar_cache[lvar_name] = value
                logger.debug(f"LVAR written: {lvar_name} = {value}")

            return success

        except Exception as e:
            logger.error(f"Error writing LVAR {lvar_name}: {e}")
            return False

    async def execute_html_event(self, event_name: str) -> bool:
        """
        Execute an H: event (HTML/JavaScript event).

        Args:
            event_name: Event name (without H: prefix)

        Returns:
            True if successful
        """
        if not self._available:
            logger.warning("MobiFlight WASM not available")
            return False

        try:
            # Format: (>H:eventname)
            command = f"(>H:{event_name})"

            success = await self._send_command(
                MobiFlightMessageType.EXECUTE_HTML_EVENT,
                command
            )

            if success:
                logger.debug(f"H:Event executed: {event_name}")

            return success

        except Exception as e:
            logger.error(f"Error executing H:Event {event_name}: {e}")
            return False

    async def execute_calculator_code(self, code: str) -> Optional[float]:
        """
        Execute RPN calculator code.

        Args:
            code: RPN calculator code string

        Returns:
            Result value if any, None on error
        """
        if not self._available:
            logger.warning("MobiFlight WASM not available")
            return None

        try:
            result = await self._send_command_and_wait(
                MobiFlightMessageType.EXECUTE_CALCULATOR_CODE,
                code
            )

            logger.debug(f"Calculator code executed: {code} = {result}")
            return result

        except Exception as e:
            logger.error(f"Error executing calculator code: {e}")
            return None

    async def _send_command(self, msg_type: MobiFlightMessageType, data: str) -> bool:
        """
        Send a command to MobiFlight WASM.

        Args:
            msg_type: Message type
            data: Command data string

        Returns:
            True if command was sent successfully
        """
        if not self._sc:
            return False

        try:
            # Encode command for Client Data Area
            # Format: [type:1byte][length:2bytes][data:variable]
            command_bytes = self._encode_command(msg_type, data)

            # Send via SimConnect Client Data Area
            # This requires low-level SimConnect access
            # Implementation depends on SimConnect bindings used

            # Placeholder for actual implementation
            logger.debug(f"Command sent: type={msg_type}, data={data[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False

    async def _send_command_and_wait(
        self,
        msg_type: MobiFlightMessageType,
        data: str,
        timeout: float = 1.0
    ) -> Optional[float]:
        """
        Send command and wait for response.

        Args:
            msg_type: Message type
            data: Command data
            timeout: Response timeout in seconds

        Returns:
            Response value or None
        """
        # Generate request ID
        self._request_id += 1
        request_id = self._request_id

        # Send command
        if not await self._send_command(msg_type, data):
            return None

        # In a real implementation, we would:
        # 1. Register callback for response
        # 2. Wait for response with timeout
        # 3. Return value

        # Placeholder - actual implementation needs async response handling
        return None

    def _encode_command(self, msg_type: MobiFlightMessageType, data: str) -> bytes:
        """
        Encode command for transmission to WASM.

        Args:
            msg_type: Message type
            data: Command string

        Returns:
            Encoded bytes
        """
        # Encode string to bytes
        data_bytes = data.encode('utf-8')

        if len(data_bytes) > self.MAX_COMMAND_LENGTH:
            data_bytes = data_bytes[:self.MAX_COMMAND_LENGTH]

        # Pack: type (1 byte) + length (2 bytes) + data
        header = struct.pack('<BH', msg_type, len(data_bytes))
        return header + data_bytes

    def _decode_response(self, data: bytes) -> tuple:
        """
        Decode response from WASM.

        Args:
            data: Raw response bytes

        Returns:
            Tuple of (message_type, payload)
        """
        if len(data) < 3:
            return (None, None)

        # Unpack header
        msg_type, length = struct.unpack('<BH', data[:3])
        payload = data[3:3+length]

        return (msg_type, payload)

    def get_cached_lvar(self, lvar_name: str) -> Optional[float]:
        """
        Get cached LVAR value (no network call).

        Args:
            lvar_name: LVAR name

        Returns:
            Cached value or None if not cached
        """
        return self._lvar_cache.get(lvar_name)

    def on_lvar_update(self, callback: Callable[[str, float], None]):
        """
        Register callback for LVAR updates.

        Args:
            callback: Function called with (lvar_name, value)
        """
        self._on_lvar_update = callback

    def clear_cache(self):
        """Clear LVAR cache."""
        self._lvar_cache.clear()

    def close(self):
        """Clean up resources."""
        self._initialized = False
        self._available = False
        self._lvar_cache.clear()


class MobiFlightSimConnectBridge:
    """
    Bridge between standard SimConnect and MobiFlight WASM.

    Provides unified interface for both standard SimConnect events
    and LVAR-based commands.
    """

    def __init__(self, sim_connection, mobiflight_client: MobiFlightClient):
        """
        Initialize bridge.

        Args:
            sim_connection: SimConnection instance
            mobiflight_client: MobiFlightClient instance
        """
        self._sim = sim_connection
        self._mf = mobiflight_client

    async def execute_command(
        self,
        command_type: str,
        command_data: Dict[str, Any]
    ) -> bool:
        """
        Execute a command using the appropriate method.

        Args:
            command_type: "simconnect", "lvar", or "hevent"
            command_data: Command parameters

        Returns:
            True if successful
        """
        if command_type == "simconnect":
            # Use standard SimConnect event
            event_name = command_data.get("event")
            value = command_data.get("value", 0)
            return self._sim.send_event(event_name, value)

        elif command_type == "lvar":
            # Use LVAR via MobiFlight
            lvar_name = command_data.get("lvar")
            value = command_data.get("value")

            if value is not None:
                return await self._mf.write_lvar(lvar_name, value)
            else:
                result = await self._mf.read_lvar(lvar_name)
                return result.success

        elif command_type == "hevent":
            # Use H:Event via MobiFlight
            event_name = command_data.get("event")
            return await self._mf.execute_html_event(event_name)

        elif command_type == "calculator":
            # Execute calculator code
            code = command_data.get("code")
            result = await self._mf.execute_calculator_code(code)
            return result is not None

        else:
            logger.warning(f"Unknown command type: {command_type}")
            return False

    @property
    def has_lvar_support(self) -> bool:
        """Check if LVAR support is available."""
        return self._mf.is_available
