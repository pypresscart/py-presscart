"""Resource classes for the presscart client."""

from pypresscart.resources.articles import ArticlesResource
from pypresscart.resources.auth import AuthResource
from pypresscart.resources.campaigns import CampaignsResource
from pypresscart.resources.files import FilesResource
from pypresscart.resources.folders import FoldersResource
from pypresscart.resources.order_items import OrderItemsResource
from pypresscart.resources.orders import OrdersResource
from pypresscart.resources.outlets import OutletsResource
from pypresscart.resources.products import ProductsResource
from pypresscart.resources.profiles import ProfilesResource

__all__ = [
    "ArticlesResource",
    "AuthResource",
    "CampaignsResource",
    "FilesResource",
    "FoldersResource",
    "OrderItemsResource",
    "OrdersResource",
    "OutletsResource",
    "ProductsResource",
    "ProfilesResource",
]
