# common.mk - Shared Makefile fragments for service Makefiles.
#
# Include this file near the top of a service Makefile:
#   include ../../scripts/lib/common.mk
#
# Provides:
#   check-mode  - Validates that MODE is set to "docker" or "bare"

SHELL := /usr/bin/env bash

.PHONY: check-mode
check-mode:
	@if [[ "$(MODE)" != "docker" && "$(MODE)" != "bare" ]]; then \
		echo "Unsupported MODE='$(MODE)'. Use MODE=docker or MODE=bare."; \
		exit 1; \
	fi
