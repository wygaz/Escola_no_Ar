from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from apps.core.permissions import PROD_SONHEMAISALTO, PROD_VOCACIONAL_75


SONHE_MAIS_ALTO_KEY = "sonhe_mais_alto"
VOCACIONAL_KEY = "vocacional"


@dataclass(frozen=True)
class ProductDefinition:
    """Metadata central dos produtos expostos pelo portal."""

    key: str
    public_name: str
    public_slug: str
    access_slug: str
    setting_flag: str
    entry_url_name: str
    legacy_names: tuple[str, ...] = ()


PRODUCTS: dict[str, ProductDefinition] = {
    SONHE_MAIS_ALTO_KEY: ProductDefinition(
        key=SONHE_MAIS_ALTO_KEY,
        public_name="Sonhe + Alto",
        public_slug="sonhe-mais-alto",
        access_slug=PROD_SONHEMAISALTO,
        setting_flag="SONHEMAISALTO_REQUIRE_BONUS",
        entry_url_name="projeto21:home",
        legacy_names=("Projeto 21", "Sonho de Ser"),
    ),
    VOCACIONAL_KEY: ProductDefinition(
        key=VOCACIONAL_KEY,
        public_name="Vocacional",
        public_slug="vocacional",
        access_slug=PROD_VOCACIONAL_75,
        setting_flag="VOCACIONAL_REQUIRE_BONUS",
        entry_url_name="vocacional:entrada",
    ),
}

PRODUCTS_BY_PUBLIC_SLUG: dict[str, ProductDefinition] = {
    product.public_slug: product for product in PRODUCTS.values()
}


def iter_products() -> Iterable[ProductDefinition]:
    return PRODUCTS.values()


def get_product_by_key(key: str) -> ProductDefinition:
    return PRODUCTS[key]


def get_product_by_public_slug(public_slug: str) -> ProductDefinition | None:
    return PRODUCTS_BY_PUBLIC_SLUG.get(public_slug)
