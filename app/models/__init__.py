import pkgutil, importlib, pathlib
_pkg = pathlib.Path(__file__).parent
for m in pkgutil.iter_modules([str(_pkg)]):
    if not m.ispkg and m.name not in {"__init__"}:
        importlib.import_module(f"{__name__}.{m.name}")
