from datetime import datetime, timezone
from logging import getLogger
from time import time
from typing import Optional, Tuple, TypedDict

import HyWorksApiGRPC as HyWorksApi
import requests
from splight_lib.models import Asset
from splight_lib.settings import workspace_settings

from hypersim.interfaces import DataReader
from hypersim.reader import AssetAttributeDataReader

logger = getLogger("HypersimOperator")
GENERATOR_VECTOR_NAME = "generators_vector"


class LineInfo(TypedDict):
    name: str
    asset: str
    breaker: str


class GeneratorInfo(TypedDict):
    name: str
    asset: str
    breaker: str


def set_device_value(
    device: str, variable: str, value: str | int | float
) -> None:
    """Sets the value of a device variable in Hypersim."""
    HyWorksApi.setComponentParameter(device, variable, str(value))
    logger.debug(f"Setting {device}.{variable} to {value}")


class DCMHypersimOperator:
    def __init__(
        self,
        grid: str,
        lines: list[LineInfo],
        generators: list[GeneratorInfo],
        hypersim_reader: DataReader,
    ):
        self._grid = grid
        addresses = []
        breakers = []
        for line_info in lines:
            line = Asset.retrieve(line_info["asset"])
            attrs = {attr.name: attr for attr in line.attributes}
            address = {
                "asset": line.id,
                "attribute": attrs[GENERATOR_VECTOR_NAME].id,
            }
            addresses.append(address)
            breakers.append(line_info["breaker"])
        self._lines = lines
        self._lines_breakers = breakers
        self._generators = {item["name"]: item for item in generators}
        self._generators_vector: dict[str, list[int]] = {}
        self._hy_reader = hypersim_reader
        self._spl_reader = AssetAttributeDataReader(
            addresses, data_type="String", limit=1
        )

        self._in_contingency = False
        self._last_contingency: datetime | None = None

    # def run(self) -> None:
    #     t0 = time()
    #     self._run()
    #     t1 = time()
    #     if self._contingency:
    #         logger.info(
    #             f"\n\n\nOperation time: {(t1 - t0) * 1000:.3f} ms\n\n\n"
    #         )

    def run(self) -> None:
        t0 = time()
        contingency = self._check_for_contingency()
        new_contingency = self._process_contingency(contingency)
        t1 = time()
        if new_contingency:
            logger.info(
                f"\n\n\nOperation time: {(t1 - t0) * 1000:.3f} ms\n\n\n"
            )

    def _process_contingency(
        self, contingency: Optional[Tuple[str, int]]
    ) -> bool:
        new_contingency = False
        if self._in_contingency:
            if contingency is None:
                logger.info("Recovering system from contingency")
                self._recover_system()
                self._in_contingency = False
            else:
                logger.info(
                    "System still in contingency. Waiting for recovery"
                )
        else:
            if contingency is not None:
                logger.info(f"Contingency found on line {contingency[0]}")
                self._run_operation(contingency[0])
                new_contingency = True
                self._in_contingency = True
                self._last_contingency = datetime.now(timezone.utc)
            else:
                logger.info("No contingency found.")
        return new_contingency

    def _check_for_contingency(self) -> Optional[Tuple[str, int]]:
        breakers_status = self._hy_reader.read()
        line_in_contingency = next(
            filter(
                lambda x: x[1] == 0 and x[0] in self._lines_breakers,
                breakers_status.items(),
            ),
            None,
        )
        return line_in_contingency

    # def _run(self) -> None:
    #     breakers_status = self._hy_reader.read()
    #
    #     in_contingency = next(
    #         filter(lambda x: x[1] == 0, breakers_status.items()),
    #         None,
    #     )
    #     if in_contingency is None:
    #         if self._contingency:
    #             logger.info("Recovering system from contingency")
    #             self._recover_system()
    #         logger.info("No contingency found.")
    #         self._contingency = False
    #     elif in_contingency:
    #         if not self._contingency:
    #             logger.info(f"Contingency found on line {in_contingency[0]}")
    #             self._run_operation(in_contingency[0])
    #             self._contingency = True
    #             self._last_contingency = datetime.now(timezone.utc)
    #             # TODO: Report contingency to splight
    #         else:
    #             logger.info(
    #                 f"Contingency already handled on line {in_contingency[0]}"
    #             )
    #             logger.info("Waiting for system to recover")

    def update_operation_vectors(self) -> None:
        data = self._spl_reader.read()
        for line_id, vector in data.items():
            line_name = next(
                filter(lambda x: x["asset"] == line_id, self._lines)
            )
            self._generators_vector.update(
                {line_name["breaker"]: self._parse_generator_vector(vector)}
            )
        logger.info(f"Operation vectors updated: {self._generators_vector}")

    def _run_operation(self, line_breaker: str) -> None:
        vector = self._generators_vector.get(line_breaker, None)
        if vector is None:
            line_name = next(
                filter(lambda x: x["breaker"] == line_breaker, self._lines)
            )["name"]
            raise ValueError(f"No operation vector found for line {line_name}")
        self._apply_vector(vector)

    def _apply_vector(self, vector: dict[str, int]) -> None:
        logger.info(f"Applying operation vector: {vector}")
        for gen_name, value in vector.items():
            if value == 0:
                continue
            # In Hypersim, the setpoint is 0 to open the breaker and 7 to
            # close it
            setpoint = 0 if value == 1 else 7
            generator = self._generators.get(gen_name, None)
            # TODO: Check if generator is None
            block, variable = generator["breaker"].split(".")
            set_device_value(block, variable, setpoint)
            logger.debug(f"Setting generator {gen_name} to {setpoint}")

    def _parse_generator_vector(self, vector: str) -> list[int]:
        generator_ordering = self._fetch_gen_ordering(self._grid)
        splitted_vector = [int(x) for x in vector.split(",")]
        sorted_gens = []
        for gen in generator_ordering:
            gen_id = gen["id"]
            full_gen = next(
                filter(
                    lambda x: x["asset"] == gen_id, self._generators.values()
                )
            )
            sorted_gens.append(full_gen)
        parsed_vector = {
            gen["name"]: value
            for gen, value in zip(sorted_gens, splitted_vector)
        }
        return parsed_vector

    def _recover_system(self) -> None:
        for generator in self._generators.values():
            block, variable = generator["breaker"].split(".")
            set_device_value(block, variable, 7)
            logger.debug(f"Closing breaker for generator {generator['name']}")

    @staticmethod
    def _fetch_gen_ordering(grid_id: str) -> list[str]:
        host = workspace_settings.SPLIGHT_PLATFORM_API_HOST
        url = f"{host}/v4/engine/asset/grids/{grid_id}/structure/"
        access_id = workspace_settings.SPLIGHT_ACCESS_ID
        secret_key = workspace_settings.SPLIGHT_SECRET_KEY
        header = {
            "Authorization": f"Splight {access_id} {secret_key}",
        }
        response = requests.get(url, headers=header)
        response.raise_for_status()
        data = response.json()
        return data["generators"]
