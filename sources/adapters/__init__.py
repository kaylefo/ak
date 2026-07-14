"""Source adapters for Tsubo ingestion."""

from adapters.athome_discovery import AtHomeDiscoveryAdapter
from adapters.athome_listings import AtHomeListingsAdapter
from adapters.generic_html import GenericHtmlAdapter
from adapters.generic_json_ld import GenericJsonLdAdapter
from adapters.generic_table import GenericTableAdapter
from adapters.lifull_discovery import LifullDiscoveryAdapter
from adapters.lifull_listings import LifullListingsAdapter
from adapters.mlit_discovery import MlitDiscoveryAdapter
from adapters.mlit_municipal_links import MlitMunicipalLinksAdapter
from adapters.no_inventory import NoInventoryClassifier

ALL_ADAPTERS = [
    MlitDiscoveryAdapter(),
    MlitMunicipalLinksAdapter(),
    LifullDiscoveryAdapter(),
    LifullListingsAdapter(),
    AtHomeDiscoveryAdapter(),
    AtHomeListingsAdapter(),
    GenericHtmlAdapter(),
    GenericTableAdapter(),
    GenericJsonLdAdapter(),
]

__all__ = [
    "ALL_ADAPTERS",
    "AtHomeDiscoveryAdapter",
    "AtHomeListingsAdapter",
    "GenericHtmlAdapter",
    "GenericJsonLdAdapter",
    "GenericTableAdapter",
    "LifullDiscoveryAdapter",
    "LifullListingsAdapter",
    "MlitDiscoveryAdapter",
    "MlitMunicipalLinksAdapter",
    "NoInventoryClassifier",
]
