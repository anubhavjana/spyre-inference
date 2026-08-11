#!/usr/bin/env bash
# Single source of truth for TEST_TYPE: the valid set and its defaulting.
# Shared by the Makefile TEST_TYPE resolution and _test_matrix.yaml's resolve
# and gate steps, so every entry point applies the same validation. To add a
# new test type, edit ONLY this file (VALID_TYPES); the callers do not change.
#
# Usage: resolve_test_type.sh TEST_TYPE
# Prints the resolved canonical type to stdout. unit/integration/regression/
# trunk/perf are literal, first-class values -- there is no alias-resolution
# layer (no more unit->core / integration->smoke / regression->full mapping).
# Empty/no arg resolves to "regression". If the (defaulted) value is not in
# VALID_TYPES, prints a GitHub Actions ::error:: line to stderr and exits 1,
# so callers do not re-validate.

set -euo pipefail

# The canonical test types. This is the ONLY list to edit when adding a type.
VALID_TYPES="unit integration regression trunk perf"

RAW_TEST_TYPE="${1:-}"

case "$RAW_TEST_TYPE" in
    '') resolved=regression ;;
    smoke)
        # "smoke" is the internal marker-combo this repo's Makefile maps
        # "integration" to (see MARK_EXPR) -- not itself a valid top-level
        # tier, so a caller reaching for the old name gets pointed at the
        # replacement instead of the generic "Invalid test_type" error below.
        echo "::error::TEST_TYPE=smoke is not a valid tier -- use TEST_TYPE=integration to run that suite. Valid: ${VALID_TYPES// / | }" >&2
        exit 1
        ;;
    *) resolved="$RAW_TEST_TYPE" ;;
esac

case " $VALID_TYPES " in
    *" $resolved "*) ;;
    *)
        valid_display="${VALID_TYPES// / | }"
        echo "::error::Invalid test_type '${RAW_TEST_TYPE}'. Valid: ${valid_display}" >&2
        exit 1
        ;;
esac

echo "$resolved"
