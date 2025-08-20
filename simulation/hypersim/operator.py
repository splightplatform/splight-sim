from time import time
from datetime import datetime, timezone
from typing import TypedDict

import HyWorksApiGRPC as HyWorksApi
import requests
from splight_lib.logging import getLogger
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
        self._generators = {item["name"]: item for item in generators}
        self._generators_vector: dict[str, list[int]] = {}
        self._hy_reader = hypersim_reader
        # self._hy_reader = HypersimDataReader(breakers)
        self._spl_reader = AssetAttributeDataReader(
            addresses, data_type="String", limit=1
        )

        self._contingency = False
        self._last_contingency: datetime | None = None

    def run(self) -> None:
        t0 = time()
        self._run()
        t1 = time()
        if self._contingency:
            logger.info(f"\n\n\nOperation time: {t1 - t0:.3f} seconds\n\n\n")

    def _run(self) -> None:
        breakers_status = self._hy_reader.read()

        in_contingency = next(
            filter(lambda x: x[1] == 0, breakers_status.items()),
            None,
        )
        if in_contingency is None:
            if self._contingency:
                logger.info("Recovering system from contingency")
                self._recover_system()
            logger.info("No contingency found.")
            self._contingency = False
        elif in_contingency:
            if not self._contingency:
                logger.info(f"Contingency found on line {in_contingency[0]}")
                self._run_operation(in_contingency[0])
                self._contingency = True
                self._last_contingency = datetime.now(timezone.utc)
            else:
                logger.info(
                    f"Contingency already handled on line {in_contingency[0]}"
                )
                logger.info("Waiting for system to recover")

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

    def _run_operation(self, line_name: str) -> None:
        vector = self._generators_vector.get(line_name, None)
        if vector is None:
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
            HyWorksApi.setComponentParameter(block, variable, str(setpoint))
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
            HyWorksApi.setComponentParameter(block, variable, "7")
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
