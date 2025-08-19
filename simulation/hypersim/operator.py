from typing import TypedDict

import requests

# import HyWorksApiGRPC as HyWorksApi
from splight_lib.models import Asset
from splight_lib.settings import workspace_settings

from hypersim.reader import AssetAttributeDataReader, HypersimDataReader

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
        self, grid: str, lines: list[LineInfo], generators: list[GeneratorInfo]
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
        self._hy_reader = HypersimDataReader(breakers)
        self._spl_reader = AssetAttributeDataReader(
            addresses, data_type="String", limit=1
        )

    def run(self) -> None:
        breakers_status = self._hy_reader.read()
        for line_name, status in breakers_status.items():
            if status == 0:
                print(f"Found contingency on line {line_name}")
                self._run_operation(line_name)

    def update_operation_vectors(self) -> None:
        data = self._spl_reader.read()
        for line_id, vector in data.items():
            line_name = next(
                filter(lambda x: x["asset"] == line_id, self._lines)
            )
            self._generators_vector.update(
                {line_name["breaker"]: self._parse_generator_vector(vector)}
            )
        print(f"Operation vectors updated: {self._generators_vector}")

    def _run_operation(self, line_name: str) -> None:
        vector = self._generators_vector.get(line_name, None)
        if vector is None:
            raise ValueError(f"No operation vector found for line {line_name}")
        self._apply_vector(vector)

    def _apply_vector(self, vector: dict[str, int]) -> None:
        print(f"Applying operation vector: {vector}")
        for gen_name, value in vector.items():
            if value == 0:
                continue
            setpoint = 7 if value == 1 else 0
            generator = self._generators.get(gen_name, None)
            # TODO: Check if generator is None
            block, variable = generator["breaker"].split(".")
            # HyWorksApi.setComponentParameter(block, variable, str(setpoint))
            print(f"Setting generator {gen_name} to {setpoint}")

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
