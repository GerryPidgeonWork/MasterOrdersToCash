# ====================================================================================================
# G04a_app_state.py                                                                      [v1.0.0]
# ----------------------------------------------------------------------------------------------------
# Centralised, strongly-typed application state manager for the GUI framework.
#
# Purpose:
#   - Provide a SINGLE source of truth for all runtime GUI variables.
#   - Maintain a strict schema of allowed state keys with type hints and defaults.
#   - Provide safe get/set/update operations with validation.
#   - Support JSON serialisation for session persistence.
#   - Support full reset-to-defaults capability.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-12
# Project:      SimpleTk v1.0
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ----------------------------------------------------------------------------------------------------

# --- Future behaviour & type system enhancements -----------------------------------------------------
from __future__ import annotations           # Future-proof type hinting (PEP 563 / PEP 649)

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys                                   # Python interpreter access (path, environment, runtime)
from pathlib import Path                     # Modern, object-oriented filesystem path handling

# --- Ensure project root DOES NOT override site-packages --------------------------------------------
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Remove '' (current working directory) which can shadow installed packages -----------------------
if "" in sys.path:
    sys.path.remove("")

# --- Prevent creation of __pycache__ folders ---------------------------------------------------------
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in shared external packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external + stdlib packages MUST be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# C01_set_file_paths is a pure core module and must not import GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------


# ====================================================================================================
# 3. TYPE DEFINITIONS
# ====================================================================================================

StateSchemaType = Dict[str, Tuple[Tuple[type, ...], Any]]


# ====================================================================================================
# 4. APPLICATION STATE MANAGER
# ====================================================================================================

class AppState:
    """
    Strongly-typed centralised state manager for all GUI runtime variables.

    All valid state keys must be declared in the schema. Mutable defaults are
    deep-copied to prevent instance contamination. No GUI imports allowed.
    """

    DEFAULT_SCHEMA: StateSchemaType = {
        "current_page": ((str, type(None)), None),
        "previous_page": ((str, type(None)), None),
        "navigation_history": ((list,), []),
        "history_index": ((int,), -1),
        "theme": ((str,), "default"),
        "debug_mode": ((bool,), False),
        "session_data": ((dict,), {}),
    }

    def __init__(self, schema: StateSchemaType | None = None) -> None:
        """
        Description:
            Initialise state with schema and deep-copied mutable defaults.

        Args:
            schema: Optional custom schema. If None, uses DEFAULT_SCHEMA.

        Returns:
            None.

        Raises:
            None.

        Notes:
            Pass custom schema to extend for application-specific keys.
        """
        self._schema: StateSchemaType = schema if schema is not None else self.DEFAULT_SCHEMA.copy()
        self._state_map: Dict[str, Any] = {}
        self._initialise_defaults()
        logger.info("[G04a] AppState initialised with %d keys.", len(self._schema))

    def _initialise_defaults(self) -> None:
        """Populate state_map with deep-copied default values from schema."""
        for key, (_, default) in self._schema.items():
            if isinstance(default, (dict, list, set)):
                self._state_map[key] = deepcopy(default)
            else:
                self._state_map[key] = default

    # ------------------------------------------------------------------------------------------------
    # VALIDATION HELPERS
    # ------------------------------------------------------------------------------------------------

    def _validate_key(self, key: str) -> None:
        """
        Description:
            Validate that the supplied key exists in the schema.

        Args:
            key: The key to validate.

        Returns:
            None.

        Raises:
            KeyError: If the key is not in the schema.

        Notes:
            Ensures all state access is schema-safe.
        """
        if key not in self._schema:
            raise KeyError(
                f"Invalid state key '{key}'. Allowed keys: {list(self._schema.keys())}"
            )

    def _validate_type(self, key: str, value: Any) -> None:
        """
        Description:
            Validate that the value matches allowed types for a key.

        Args:
            key: The state key.
            value: The value to validate.

        Returns:
            None.

        Raises:
            TypeError: If the value type is not among allowed types.

        Notes:
            Allowed types are defined in the schema.
        """
        expected_types = self._schema[key][0]
        if not isinstance(value, expected_types):
            raise TypeError(
                f"Invalid type for '{key}': expected {expected_types}, "
                f"got {type(value).__name__} (value={value!r})"
            )

    # ------------------------------------------------------------------------------------------------
    # PUBLIC API — GET / SET / UPDATE
    # ------------------------------------------------------------------------------------------------

    def get_state(self, key: str) -> Any:
        """
        Description:
            Retrieve a state value after validating the key.

        Args:
            key: The state key to retrieve.

        Returns:
            Any: The current value for this key.

        Raises:
            KeyError: If the key is invalid.

        Notes:
            Values are returned exactly as stored.
        """
        self._validate_key(key)
        return self._state_map[key]

    def set_state(self, key: str, value: Any) -> None:
        """
        Description:
            Assign a value after validating both key and type.

        Args:
            key: State key.
            value: New value to assign.

        Returns:
            None.

        Raises:
            KeyError: Invalid key.
            TypeError: Invalid value type.

        Notes:
            Mutable values are assigned directly (caller manages lifecycle).
        """
        self._validate_key(key)
        self._validate_type(key, value)
        self._state_map[key] = value
        logger.debug("[G04a] State set: %s = %r", key, value)

    def update_state(self, **kwargs: Any) -> None:
        """
        Description:
            Update multiple state fields at once.

        Args:
            **kwargs: Key/value pairs to update.

        Returns:
            None.

        Raises:
            KeyError: For any invalid key.
            TypeError: For any invalid value.

        Notes:
            Equivalent to multiple calls to set_state().
        """
        for key, value in kwargs.items():
            self.set_state(key, value)

    def reset_state(self) -> None:
        """Reset all state keys to their default values."""
        self._initialise_defaults()
        logger.info("[G04a] State reset to defaults.")

    # ------------------------------------------------------------------------------------------------
    # SCHEMA EXTENSION
    # ------------------------------------------------------------------------------------------------

    def extend_schema(self, additional_keys: StateSchemaType) -> None:
        """
        Description:
            Add additional keys to the schema at runtime.

        Args:
            additional_keys: Dictionary of new keys with type/default definitions.

        Returns:
            None.

        Raises:
            ValueError: If any key already exists in the schema.

        Notes:
            New keys are initialised to their defaults immediately.
        """
        for key in additional_keys:
            if key in self._schema:
                raise ValueError(f"State key '{key}' already exists in schema.")

        self._schema.update(additional_keys)

        for key, (_, default) in additional_keys.items():
            if isinstance(default, (dict, list, set)):
                self._state_map[key] = deepcopy(default)
            else:
                self._state_map[key] = default

        logger.info("[G04a] Schema extended with %d new keys.", len(additional_keys))

    # ------------------------------------------------------------------------------------------------
    # SERIALISATION
    # ------------------------------------------------------------------------------------------------

    def save_to_json(self, filepath: str | Path) -> bool:
        """
        Description:
            Save the current application state to a JSON file.

        Args:
            filepath: Path to the JSON file.

        Returns:
            bool: True on success, False on failure.

        Raises:
            None.

        Notes:
            File is written in UTF-8 with indentation. Errors logged, not raised.
        """
        try:
            filepath = Path(filepath)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._state_map, f, indent=4)
            logger.info("[G04a] State saved to '%s'.", filepath)
            return True
        except Exception as exc:
            logger.error("[G04a] Failed to save state to '%s': %s", filepath, exc)
            return False

    def load_from_json(self, filepath: str | Path) -> bool:
        """
        Description:
            Load application state from a JSON file.

        Args:
            filepath: Path to the JSON file.

        Returns:
            bool: True if loaded successfully, False otherwise.

        Raises:
            None.

        Notes:
            Invalid keys/types are skipped with warnings. Errors logged, not raised.
        """
        try:
            filepath = Path(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            loaded_count = 0
            for key, value in data.items():
                if key not in self._schema:
                    logger.warning("[G04a] Ignoring unknown key '%s' from JSON.", key)
                    continue
                try:
                    self.set_state(key, value)
                    loaded_count += 1
                except TypeError as te:
                    logger.warning("[G04a] Skipping key '%s': %s", key, te)
                    continue

            logger.info("[G04a] State loaded from '%s' (%d keys).", filepath, loaded_count)
            return True

        except FileNotFoundError:
            logger.warning("[G04a] State file not found: '%s'.", filepath)
            return False
        except Exception as exc:
            logger.error("[G04a] Failed to load state from '%s': %s", filepath, exc)
            return False

    # ------------------------------------------------------------------------------------------------
    # UTILITY METHODS
    # ------------------------------------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return a shallow copy of the current state dictionary."""
        return dict(self._state_map)

    def diff_state(self, other: Dict[str, Any]) -> Dict[str, Any]:
        """
        Description:
            Compare this state against another dictionary.

        Args:
            other: Dictionary to compare against.

        Returns:
            Dict[str, Any]: Mapping of differing keys to current values.

        Raises:
            None.

        Notes:
            Useful for debugging and change detection.
        """
        return {
            k: v for k, v in self._state_map.items()
            if k not in other or other[k] != v
        }

    def keys(self) -> list[str]:
        """Return list of all valid state keys from the schema."""
        return list(self._schema.keys())

    # ------------------------------------------------------------------------------------------------
    # DUNDER METHODS
    # ------------------------------------------------------------------------------------------------

    def __contains__(self, key: str) -> bool:
        """Support membership checks using `in` on the AppState instance."""
        return key in self._schema

    def __repr__(self) -> str:
        """Return a string representation of the AppState instance."""
        return f"AppState({self._state_map})"


# ====================================================================================================
# 5. PUBLIC API
# ====================================================================================================

__all__ = [
    "AppState",
    "StateSchemaType",
]


# ====================================================================================================
# 6. SELF-TEST
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("=" * 60)
    logger.info("[G04a] AppState — Self Test")
    logger.info("=" * 60)

    try:
        logger.info("[Test 1] Basic initialisation...")
        state = AppState()
        logger.info("Initial state: %s", state.snapshot())
        assert "current_page" in state
        assert state.get_state("debug_mode") is False
        logger.info("[Test 1] PASSED")

        logger.info("[Test 2] Set and get...")
        state.set_state("current_page", "home")
        assert state.get_state("current_page") == "home"
        state.set_state("debug_mode", True)
        assert state.get_state("debug_mode") is True
        logger.info("[Test 2] PASSED")

        logger.info("[Test 3] Type validation...")
        try:
            state.set_state("debug_mode", "not_a_bool")
            logger.error("[Test 3] FAILED - should have raised TypeError")
        except TypeError:
            logger.info("[Test 3] PASSED - TypeError raised correctly")

        logger.info("[Test 4] Key validation...")
        try:
            state.set_state("invalid_key", "value")
            logger.error("[Test 4] FAILED - should have raised KeyError")
        except KeyError:
            logger.info("[Test 4] PASSED - KeyError raised correctly")

        logger.info("[Test 5] Bulk update...")
        state.update_state(theme="dark", debug_mode=False)
        assert state.get_state("theme") == "dark"
        assert state.get_state("debug_mode") is False
        logger.info("[Test 5] PASSED")

        logger.info("[Test 6] Reset to defaults...")
        state.reset_state()
        assert state.get_state("current_page") is None
        assert state.get_state("theme") == "default"
        logger.info("[Test 6] PASSED")

        logger.info("[Test 7] Schema extension...")
        state.extend_schema({
            "custom_setting": ((str,), "custom_default"),
            "custom_flag": ((bool,), True),
        })
        assert "custom_setting" in state
        assert state.get_state("custom_setting") == "custom_default"
        state.set_state("custom_setting", "new_value")
        assert state.get_state("custom_setting") == "new_value"
        logger.info("[Test 7] PASSED")

        logger.info("[Test 8] JSON serialisation...")
        state.set_state("current_page", "settings")
        state.set_state("theme", "dark")

        test_file = Path("test_app_state.json")
        assert state.save_to_json(test_file) is True

        state2 = AppState()
        state2.extend_schema({
            "custom_setting": ((str,), "custom_default"),
            "custom_flag": ((bool,), True),
        })
        assert state2.load_from_json(test_file) is True
        assert state2.get_state("current_page") == "settings"
        assert state2.get_state("theme") == "dark"

        test_file.unlink(missing_ok=True)
        logger.info("[Test 8] PASSED")

        logger.info("[Test 9] Diff comparison...")
        state_a = AppState()
        state_a.set_state("theme", "dark")
        state_b_snapshot = AppState().snapshot()
        diff = state_a.diff_state(state_b_snapshot)
        assert "theme" in diff
        assert diff["theme"] == "dark"
        logger.info("[Test 9] PASSED")

        logger.info("[Test 10] Mutable default isolation...")
        state_x = AppState()
        state_y = AppState()
        state_x.get_state("session_data")["key"] = "value"
        assert "key" not in state_y.get_state("session_data")
        logger.info("[Test 10] PASSED")

        logger.info("=" * 60)
        logger.info("[G04a] All tests PASSED")
        logger.info("=" * 60)

    except Exception as exc:
        log_exception(exc, logger, "[G04a] Self-test failure")
        sys.exit(1)