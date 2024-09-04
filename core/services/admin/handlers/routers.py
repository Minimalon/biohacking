from .admin import router as admin_routers
from .analytics import router as analytics_router
from .create_user import router as create_user_router
from .create_post import router as create_post_router
from .set_admin import router as set_admin_router

admin_routers = [
    admin_routers,
    analytics_router,
    create_post_router,
    create_user_router,
    set_admin_router,
]