from collections import namedtuple

from importlib.metadata import entry_points, PackageNotFoundError

from plover.oslayer.config import PLUGINS_PLATFORM
from plover import log


_FALLBACK_PLUGINS = {
    "gui": {
        "none": "plover.gui_none.main",
        "qt": "plover.gui_qt.main",
    },
    "gui.qt.tool": {
        "add_translation": "plover.gui_qt.add_translation_dialog:AddTranslationDialog",
        "lookup": "plover.gui_qt.lookup_dialog:LookupDialog",
        "paper_tape": "plover.gui_qt.paper_tape:PaperTape",
        "plugins_manager": "plover.gui_qt.plugins_manager:PluginsManager",
        "suggestions": "plover.gui_qt.suggestions_dialog:SuggestionsDialog",
    },
}


class Plugin:
    def __init__(self, plugin_type, name, obj):
        self.plugin_type = plugin_type
        self.name = name
        self.obj = obj
        self.__doc__ = obj.__doc__ or ""

    def __str__(self):
        return f"{self.plugin_type}:{self.name}"


PluginDistribution = namedtuple("PluginDistribution", "dist plugins")


class Registry:
    PLUGIN_TYPES = (
        "command",
        "dictionary",
        "extension",
        "gui",
        "gui.qt.machine_option",
        "gui.qt.tool",
        "machine",
        "macro",
        "meta",
        "system",
    )

    def __init__(self, suppress_errors=True):
        self._plugins = {}
        self._distributions = {}
        self._suppress_errors = suppress_errors
        for plugin_type in self.PLUGIN_TYPES:
            self._plugins[plugin_type] = {}

    def register_plugin(self, plugin_type, name, obj):
        plugin = Plugin(plugin_type, name, obj)
        self._plugins[plugin_type][name.lower()] = plugin
        return plugin

    def register_plugin_from_entrypoint(self, plugin_type, entrypoint):
        log.info("%s: %s (from %s)", plugin_type, entrypoint.name, entrypoint.group)
        try:
            obj = entrypoint.load()
        except Exception:
            log.error(
                "error loading %s plugin: %s (from %s)",
                plugin_type,
                entrypoint.name,
                entrypoint.value,
                exc_info=True,
            )
            if not self._suppress_errors:
                raise
        else:
            plugin = self.register_plugin(plugin_type, entrypoint.name, obj)
            # Keep track of distributions providing plugins.
            dist_id = entrypoint.group
            dist = self._distributions.get(dist_id)
            if dist is None:
                dist = PluginDistribution(entrypoint.group, set())
                self._distributions[dist_id] = dist
            dist.plugins.add(plugin)

    def _register_fallback_plugins(self, plugin_type):
        fallback_plugins = _FALLBACK_PLUGINS.get(plugin_type)
        if fallback_plugins is None:
            return
        for name, module_path in fallback_plugins.items():
            if name in self._plugins[plugin_type]:
                continue
            module_name, _, attr_name = module_path.partition(":")
            module = __import__(module_name, fromlist=[attr_name or "main"])
            obj = getattr(module, attr_name or "main")
            self.register_plugin(plugin_type, name, obj)

    def get_plugin(self, plugin_type, plugin_name):
        return self._plugins[plugin_type][plugin_name.lower()]

    def list_plugins(self, plugin_type):
        return sorted(self._plugins[plugin_type].values(), key=lambda p: p.name)

    def list_distributions(self):
        return [dist for _, dist in sorted(self._distributions.items())]

    def update(self):
        # Is support for the QT GUI available?
        try:
            qt_entry_points = entry_points(group="plover.gui")
            has_gui_qt = any(ep.name == "qt" for ep in qt_entry_points)
        except PackageNotFoundError:
            has_gui_qt = False
        # Register available plugins.
        for plugin_type in self.PLUGIN_TYPES:
            if plugin_type.startswith("gui.qt.") and not has_gui_qt:
                continue
            entrypoint_type = f"plover.{plugin_type}"
            for entrypoint in entry_points(group=entrypoint_type):
                if "gui_qt" in entrypoint.extras and not has_gui_qt:
                    continue
                self.register_plugin_from_entrypoint(plugin_type, entrypoint)
            self._register_fallback_plugins(plugin_type)
            if PLUGINS_PLATFORM is None:
                continue
            entrypoint_type = f"plover.{PLUGINS_PLATFORM}.{plugin_type}"
            for entrypoint in entry_points(group=entrypoint_type):
                self.register_plugin_from_entrypoint(plugin_type, entrypoint)


registry = Registry()
