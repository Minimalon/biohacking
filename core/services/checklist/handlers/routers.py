from .start import router as msg_routers
from .admins import router as admin_routers
from .admin_history import router as admin_history_routers
from .admin_delete import router as admin_delete_routers

checklist_routers = [
    msg_routers,
    admin_routers,
    admin_history_routers,
    admin_delete_routers,
]