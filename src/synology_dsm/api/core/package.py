"""DSM package data."""

from __future__ import annotations

from asyncio import sleep
from time import monotonic
from typing import TYPE_CHECKING, TypedDict

from synology_dsm.api import SynoBaseApi
from synology_dsm.exceptions import SynologyDSMAPINoDataException

if TYPE_CHECKING:
    from synology_dsm import SynologyDSM


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

    def __init__(
        self,
        data: SynoPackageData,
        upgrade: SynoPackageUpgradeData | None = None,
        updates_checked: bool = False,
    ) -> None:
        """Initialize a package."""
        self._data = data
        self._upgrade: SynoPackageUpgradeData = upgrade or {}
        self._updates_checked = updates_checked

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
        """Return whether an update is available, None if that is unknown."""
        if self.available_version is not None:
            return True
        return False if self._updates_checked else None

    @property
    def available_version(self) -> str | None:
        """Return the version available for update, None if none is known."""
        return self._upgrade.get("version")

    @property
    def available_version_changelog(self) -> str | None:
        """Return the HTML changelog of the available version, if any."""
        return self._upgrade.get("changelog")


class SynoCorePackage(SynoBaseApi["dict[str, SynoPackage]"]):
    """Class containing installed packages.

    DSM only reports an available update after its package catalogue was loaded, and
    stops reporting it some time later, so a package list without an update doesn't
    mean there is none. Use `update` to refresh the installed packages and the less
    frequent `check_updates` to find out which updates are available.
    """

    API_KEY = "SYNO.Core.Package"
    SERVER_API_KEY = "SYNO.Core.Package.Server"
    REQUEST_DATA = {
        "additional": '["available_operation","install_type"]',
        "ignore_hidden": "false",
    }
    SERVER_REQUEST_DATA = {"blforcereload": "false", "blloadothers": "false"}
    # DSM can repeat an earlier package list response for several seconds, and that
    # response wouldn't include the result of a catalogue load.
    LIST_CACHE_SECONDS = 20

    def __init__(self, dsm: SynologyDSM) -> None:
        """Initialize the package api."""
        super().__init__(dsm)
        self._packages: list[SynoPackageData] = []
        self._upgrades: dict[str, SynoPackageUpgradeData] = {}
        self._updates_checked = False
        self._last_list = float("-inf")

    async def update(self) -> None:
        """Update the installed packages, keeping the updates already known.

        This doesn't load the catalogue, so it can't rule out an available update.
        """
        self._store(await self._list_packages(), update_check=False)

    async def check_updates(self) -> None:
        """Load the catalogue, then update the installed packages and their updates.

        This may make the NAS contact Synology and transfers a large response, so call
        it less often than `update`. It can wait up to `LIST_CACHE_SECONDS`, if a
        package list was requested just before.

        If this fails, packages without a known update report it as unknown.
        """
        try:
            packages = await self._list_packages_after_catalogue()
        except BaseException:
            self._updates_checked = False
            self._build_packages()
            raise
        self._updates_checked = True
        self._store(packages, update_check=True)

    def get_all_packages(self) -> list[SynoPackage]:
        """Return a list of all installed packages."""
        return list(self._data.values())

    def get_package(self, package_id: str) -> SynoPackage | None:
        """Return an installed package by id."""
        return self._data.get(package_id)

    async def _list_packages_after_catalogue(self) -> list[SynoPackageData]:
        """Load the catalogue, then return a package list that includes its result."""
        raw_data = await self._dsm.post(
            self.SERVER_API_KEY,
            "list",
            data=dict(self.SERVER_REQUEST_DATA),
            max_version=2,
        )
        if not isinstance(raw_data, dict) or raw_data.get("data") is None:
            raise SynologyDSMAPINoDataException(self.SERVER_API_KEY)

        # This repeats the check as `update` may have listed packages during the wait.
        while (
            remaining := self._last_list + self.LIST_CACHE_SECONDS - monotonic()
        ) > 0:
            await sleep(remaining)
        return await self._list_packages()

    async def _list_packages(self) -> list[SynoPackageData]:
        """Return the installed packages."""
        self._last_list = monotonic()
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

    def _store(self, packages: list[SynoPackageData], update_check: bool) -> None:
        """Store a package list and work out which updates are known.

        A package list without an update is only trusted after a catalogue load.
        Otherwise a known update is kept until the installed version changes.
        """
        installed = {package["id"]: package["version"] for package in self._packages}
        upgrades: dict[str, SynoPackageUpgradeData] = {}
        for package in packages:
            package_id = package["id"]
            additional = package.get("additional") or {}
            operations = additional.get("available_operation") or {}
            if upgrade := operations.get("upgrade"):
                upgrades[package_id] = upgrade
            elif (
                not update_check
                and package_id in self._upgrades
                and installed.get(package_id) == package["version"]
            ):
                upgrades[package_id] = self._upgrades[package_id]

        self._packages = packages
        self._upgrades = upgrades
        self._build_packages()

    def _build_packages(self) -> None:
        """Build the package objects from the stored data."""
        self._data = {
            package["id"]: SynoPackage(
                package, self._upgrades.get(package["id"]), self._updates_checked
            )
            for package in self._packages
        }
