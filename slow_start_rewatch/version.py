# -*- coding: utf-8 -*-

import importlib_metadata as metadata

distribution_name = "slow-start-rewatch"


def version() -> str:
    """Return the package version."""
    return metadata.version(distribution_name)
