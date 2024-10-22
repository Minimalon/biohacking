from .admin import router as admin_routers
from .analytics import router as analytics_router
from .create_user import router as create_user_router
from .create_post import router as create_post_router
from .set_admin import router as set_admin_router
from .operation_catalogs.catalogs import router as catalogs_router
from .operation_catalogs.products import router as products_router
from .orders_list import router as orders_list_router

admin_routers = [
    admin_routers,
    analytics_router,
    create_post_router,
    create_user_router,
    set_admin_router,
    catalogs_router,
    products_router,
    orders_list_router,
]
