from hatchling.plugin import hookimpl

from .plugin import DuckDBExtensionBuildHook


@hookimpl
def hatch_register_build_hook():
    return DuckDBExtensionBuildHook
