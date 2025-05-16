import os
import typing
from typing import Callable, Literal

import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

from src.utils import from_current_file, load_json, save_json

# Documentation links
DOCS_INDEX_URL = "https://docs.python.org/3.12/py-modindex.html"
DOCS_URL_PREFIX = "https://docs.python.org/3.12/"

# FileSystem paths
SAVE_FOLDER = from_current_file("../data/scrapped")


def load_context(url: str) -> bs:
    response = requests.get(url)
    if response.status_code == 200:
        return bs(response.text, "html.parser")
    raise RuntimeError(f"Response code is {response.status_code}")


class ModulesIndex:
    def __init__(
        self, skip_platform_specific: bool = True, skip_deprecated: bool = True
    ) -> None:
        self._skip_platform_specific = skip_platform_specific
        self._skip_deprecated = skip_deprecated

        self._name = "index"
        self._settings = (
            f"{int(self._skip_platform_specific)}_{int(self._skip_deprecated)}"
        )
        self._path = os.path.join(
            SAVE_FOLDER,
            f"{self._name}_{self._settings}.json",
        )

        self._load()

    def _load(self):
        if os.path.exists(self._path):
            self._data = load_json(self._path)
            return
        os.makedirs(SAVE_FOLDER, exist_ok=True)
        self._data = self._scrap(load_context(DOCS_INDEX_URL))
        save_json(self._path, self._data)

    def _scrap(self, soup: bs) -> dict[str, dict[str, str]]:
        data = {}
        for row in soup.select("table > tr"):
            _, module_info, desc_info = row.select("td")
            platform_specific_part = module_info.select_one("em")

            if self._skip_platform_specific and (
                platform_specific_part is not None
                and platform_specific_part.text.startswith("(")
            ):
                continue

            module_a = module_info.select_one("a")
            if module_a is None:
                continue

            module_name: str = module_a.text
            if module_name.startswith("_"):
                continue

            module_ref = module_a.get("href")

            if module_ref is None:
                continue

            desc: str = desc_info.text.strip()
            if desc == "":
                continue
            if self._skip_deprecated and desc.startswith("Deprecated"):
                continue

            data[module_name] = {
                "link": f"{DOCS_URL_PREFIX}{module_ref}",
                "description": desc,
            }
        return data

    @property
    def data(self) -> dict[str, dict[str, str]]:
        return self._data

    @property
    def settings(self) -> str:
        return self._settings

    def __len__(self) -> int:
        return len(self._data)


class ModulesScrapper:
    ElementType = Literal["class", "function", "exception", "data"]
    valid_types: list[ElementType] = list(typing.get_args(ElementType))

    def __init__(
        self,
        modules_index: ModulesIndex,
        include: list[ElementType] = ["class", "function", "data"],
    ) -> None:
        self._selector_handlers: dict[
            ModulesScrapper.ElementType, Callable[[str, bs], None]
        ] = {
            "class": self._handle_class,
            "function": self._handle_function,
            # "exception": self._handle_exception,
            "data": self._handle_data,
        }

        self._selectors = include
        if len(self._selectors) == 0:
            raise RuntimeError("Selector is empty!")

        for t in self._selectors:
            if t not in self.valid_types:
                raise RuntimeError(f"Selector {t} is invalid!")

        self._modules_index = modules_index
        self._length = 0

        self._name = (
            f"{'_'.join(sorted(self._selectors))}__{self._modules_index.settings}"
        )
        self._path = os.path.join(SAVE_FOLDER, self._name)
        os.makedirs(self._path, exist_ok=True)

    def _save(self, name: str, data: str):
        try:
            with open(
                os.path.join(self._path, f"{name}.txt"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(data)
        except OSError:
            pass

    def _basic_handler(self, module_name: str, context: bs, element_type: ElementType):
        for element in context.select(f".py.{element_type}"):
            if element.select_one("dd>div.deprecated"):
                continue
            description = "\n".join(
                [x.text.strip() for x in element.select("dd>p, dd>div>p")]
            )
            for object in element.select("dt.sig-object"):
                # Name
                pre_names = object.select("span.sig-prename")
                pre_name = (
                    "".join([x.text.strip() for x in pre_names])
                    if len(pre_names) > 0
                    else ""
                )
                name = object.select_one("span.sig-name")

                if name is None:
                    continue
                full_name = f"{pre_name}{name.text.strip()}"

                # Parameters
                parameters_info = ""
                params = [x.text for x in object.select("em.sig-param")]
                if len(params) > 0:
                    parameters_info = ", ".join(params)

                parameters_section = (
                    f"PARAMETERS\n{parameters_info}\n\n" if parameters_info != "" else ""
                )

                # Save
                self._save(
                    full_name,
                    f"{element_type.upper()}\n\n{full_name} FROM {module_name}\n\n{parameters_section}DESCRIPTION\n{description}",
                )

    def _handle_data(self, module_name: str, context: bs):
        self._basic_handler(module_name, context, "data")

    def _handle_function(self, module_name: str, context: bs):
        self._basic_handler(module_name, context, "function")

    def _handle_class(self, module_name: str, context: bs):
        for element in context.select(".py.class"):
            if element.select_one("dd>div.deprecated"):
                continue

            description = "\n".join(
                [x.text.strip() for x in element.select("dd>p, dd>div>p")]
            )

            object = element.select_one("dt.sig-object")

            if object is None:
                continue
            # Name
            specification_obj = object.select_one("span.pre")
            specification = (
                specification_obj.text.strip()
                if specification_obj is not None
                else "class"
            )
            pre_names = object.select("span.sig-prename")
            pre_name = (
                "".join([x.text.strip() for x in pre_names]) if len(pre_names) > 0 else ""
            )
            name = object.select_one("span.sig-name")

            if name is None:
                continue
            full_name = f"{pre_name}{name.text.strip()}"

            # Save
            self._save(
                full_name,
                f"{specification.upper()}\n\n{full_name} FROM {module_name}\n\nDESCRIPTION\n{description}",
            )

            for method_object in element.select("dd>dl.py.method"):
                if method_object.select_one("dd>div.deprecated"):
                    continue

                # Description
                method_description = "\n".join(
                    [x.text.strip() for x in method_object.select("dd>p, dd>div>p")]
                )

                # Name
                method_name_obj = method_object.select_one("dt.sig-object>span.sig-name")

                if method_name_obj is None:
                    continue
                method_name = method_name_obj.text.strip()
                method_full_name = f"{full_name}.{method_name}"

                # Parameters
                parameters_info = ""
                params = [x.text for x in method_object.select("em.sig-param")]
                if len(params) > 0:
                    parameters_info = ", ".join(params)

                parameters_section = (
                    f"PARAMETERS\n{parameters_info}\n\n" if parameters_info != "" else ""
                )

                # Save
                self._save(
                    method_full_name,
                    f"METHOD OF {full_name}\n\n{method_full_name} FROM {module_name}\n\n{parameters_section}DESCRIPTION\n{method_description}",
                )

    def _scrap_and_save(self):
        modules_data = self._modules_index.data
        for module_name, info in tqdm(
            modules_data.items(), desc="Scrapping", total=len(modules_data)
        ):
            module_context = load_context(info["link"])

            for selector in self._selectors:
                self._selector_handlers[selector](module_name, module_context)

    def load(
        self,
        force: bool = False,
    ):
        if force or (not os.path.exists(self._path) or len(os.listdir(self._path)) == 0):
            self._scrap_and_save()
        self._length = len(os.listdir(self._path))

    def __len__(self) -> int:
        return self._length


def scrap(force: bool = False) -> int:
    modules_index = ModulesIndex()
    scrapper = ModulesScrapper(modules_index)
    scrapper.load(force=force)

    return len(scrapper)
