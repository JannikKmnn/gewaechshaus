"""Run migration scripts upgrades by navigating to root and run python -m migrations.run_migrations"""

import asyncio
import importlib
import pkgutil

from pathlib import Path


MIGRATIONS_PACKAGE = "migrations.migration_scripts"


async def run():

    package = importlib.import_module(MIGRATIONS_PACKAGE)

    migration_modules = []

    # discover modules dynamically
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        migration_modules.append(module_name)

    # sort → important for deterministic order
    migration_modules.sort()

    print(f"Running migrations: {migration_modules}")

    for module_name in migration_modules:

        full_module_name = f"{MIGRATIONS_PACKAGE}.{module_name}"
        module = importlib.import_module(full_module_name)

        print(f"Applying migration {module_name}")

        if hasattr(module, "upgrade"):
            await module.upgrade()
        else:
            print(f"⚠️ {module_name} has no upgrade()")


if __name__ == "__main__":
    asyncio.run(run())