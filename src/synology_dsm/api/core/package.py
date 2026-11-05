"""DSM package data."""

from __future__ import annotations

from typing import TypedDict

from synology_dsm.api import SynoBaseApi
from synology_dsm.exceptions import SynologyDSMAPINoDataException


class SynoPackageUpgradeData(TypedDict, total=False):
    """Data type of an available package upgrade."""

    changelog: str
    version: str


class SynoPackageAvailableOperationData(TypedDict, total=False):
    """Data type of the operations available for a package."""

    upgrade: SynoPackageUpgradeData


class SynoPackageAdditionalData(TypedDict, total=False):
    """Data type of the additional package data."""

    available_operation: SynoPackageAvailableOperationData
    install_type: str


class SynoPackageData(TypedDict, total=False):
    """Data type of a package."""

    additional: SynoPackageAdditionalData
    id: str
    name: str
    version: str


class SynoPackage:
    """A representation of an installed package."""

    def __init__(self, data: SynoPackageData) -> None:
        """Initialize a package."""
        self._data = data

    @property
    def _upgrade(self) -> SynoPackageUpgradeData:
        """Return the available upgrade, empty if there is none."""
        additional = self._data.get("additional", {})
        return additional.get("available_operation", {}).get("upgrade", {})

    @property
    def package_id(self) -> str:
        """Return the id of the package."""
        return self._data["id"]

    @property
    def name(self) -> str:
        """Return the display name of the package."""
        return self._data["name"]

    @property
    def version(self) -> str:
        """Return the installed version of the package."""
        return self._data["version"]

    @property
    def install_type(self) -> str | None:
        """Return the install type, such as "system" or "system_hidden"."""
        return self._data.get("additional", {}).get("install_type")

    @property
    def update_available(self) -> bool:
        """Return True if an update is available for the package."""
        return self.available_version is not None

    @property
    def available_version(self) -> str | None:
        """Return the version available for update, None if there is none."""
        return self._upgrade.get("version")

    @property
    def available_version_changelog(self) -> str | None:
        """Return the HTML changelog of the available version, if any."""
        return self._upgrade.get("changelog")


class SynoCorePackage(SynoBaseApi["dict[str, SynoPackage]"]):
    """Class containing installed packages."""

    API_KEY = "SYNO.Core.Package"
    REQUEST_DATA = {
        "additional": '["available_operation","install_type"]',
        "ignore_hidden": "false",
    }

    async def update(self) -> None:
        """Updates package data."""
        # The request helper adds session data to the params it receives.
        raw_data = await self._dsm.get(
            self.API_KEY, "list", dict(self.REQUEST_DATA), max_version=2
        )
        if not isinstance(raw_data, dict) or (data := raw_data.get("data")) is None:
            raise SynologyDSMAPINoDataException(self.API_KEY)

        self._data = {
            package["id"]: SynoPackage(package) for package in data["packages"]
        }

    def get_all_packages(self) -> list[SynoPackage]:
        """Return a list of all installed packages."""
        return list(self._data.values())

    def get_package(self, package_id: str) -> SynoPackage | None:
        """Return an installed package by id."""
        return self._data.get(package_id)
