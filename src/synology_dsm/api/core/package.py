"""DSM package data."""

from __future__ import annotations

import re
from typing import TypedDict

from synology_dsm.api import SynoBaseApi
from synology_dsm.exceptions import (
    SynologyDSMAPIErrorException,
    SynologyDSMAPINoDataException,
)


class SynoPackageCatalogueData(TypedDict, total=False):
    """Data type of a package in the catalogue."""

    changelog: str
    id: str
    version: str


class SynoPackageAdditionalData(TypedDict, total=False):
    """Data type of the additional package data."""

    install_type: str


class SynoPackageData(TypedDict, total=False):
    """Data type of an installed package."""

    additional: SynoPackageAdditionalData
    id: str
    name: str
    version: str


def _version_key(version: str) -> tuple[tuple[int, ...], ...]:
    """Return a key that orders package versions, such as 1.10-0002 > 1.9-0003."""
    return tuple(
        tuple(int(number) for number in re.findall(r"\d+", part))
        for part in version.rsplit("-", 1)
    )


class SynoPackage:
    """A representation of an installed package."""

    def __init__(
        self, data: SynoPackageData, available: SynoPackageCatalogueData | None = None
    ) -> None:
        """Initialize a package."""
        self._data = data
        self._available: SynoPackageCatalogueData = available or {}

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
    def update_available(self) -> bool | None:
        """Return whether a newer version is available, None if that is unknown."""
        if (available_version := self.available_version) is None:
            return None
        # Only DSM 6 marks the upgrades in the catalogue, so compare the versions.
        return _version_key(available_version) > _version_key(self.version)

    @property
    def available_version(self) -> str | None:
        """Return the version available in the catalogue, None if that is unknown."""
        return self._available.get("version")

    @property
    def available_version_changelog(self) -> str | None:
        """Return the HTML changelog of the available version, None if unknown."""
        return self._available.get("changelog")


class SynoCorePackage(SynoBaseApi["dict[str, SynoPackage]"]):
    """Class containing installed packages and the versions available for them."""

    API_KEY = "SYNO.Core.Package"
    SERVER_API_KEY = "SYNO.Core.Package.Server"
    REQUEST_DATA = {"additional": '["install_type"]', "ignore_hidden": "false"}
    SERVER_REQUEST_DATA = {"blforcereload": "false", "blloadothers": "false"}

    async def update(self) -> None:
        """Update the installed packages and the versions available for them.

        The available versions come from the package catalogue, so they are unknown
        if DSM can't load it, such as without internet access.
        """
        packages = await self._list_packages()
        catalogue = await self._load_catalogue()
        self._data = {
            package["id"]: SynoPackage(package, catalogue.get(package["id"]))
            for package in packages
        }

    def get_all_packages(self) -> list[SynoPackage]:
        """Return a list of all installed packages."""
        return list(self._data.values())

    def get_package(self, package_id: str) -> SynoPackage | None:
        """Return an installed package by id."""
        return self._data.get(package_id)

    async def _list_packages(self) -> list[SynoPackageData]:
        """Return the installed packages."""
        # The request helper adds session data to the params it receives.
        raw_data = await self._dsm.get(
            self.API_KEY, "list", dict(self.REQUEST_DATA), max_version=2
        )
        if (
            not isinstance(raw_data, dict)
            or (data := raw_data.get("data")) is None
            or (packages := data.get("packages")) is None
        ):
            raise SynologyDSMAPINoDataException(self.API_KEY)
        packages_data: list[SynoPackageData] = packages
        return packages_data

    async def _load_catalogue(self) -> dict[str, SynoPackageCatalogueData]:
        """Return the catalogue packages by id, an empty dict if DSM can't load it."""
        try:
            raw_data = await self._dsm.post(
                self.SERVER_API_KEY,
                "list",
                data=dict(self.SERVER_REQUEST_DATA),
                max_version=2,
            )
        except SynologyDSMAPIErrorException:
            # Such as error 117 without internet access
            return {}
        if (
            not isinstance(raw_data, dict)
            or (data := raw_data.get("data")) is None
            or (packages := data.get("packages")) is None
        ):
            raise SynologyDSMAPINoDataException(self.SERVER_API_KEY)
        return {package["id"]: package for package in packages}
