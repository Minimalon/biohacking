from .message import router as msg_routers
from .bonus_card import router as bonus_card_routers
from .orders.message import router as message_order_routers
from .orders.history_orders import router as history_orders_routers
from .orders.start_shop import router as start_shop_routers
from .orders.current_orders import router as current_orders_routers
from .need_help import router as need_help_routers
from .energy_guide import router as energy_guide_routers
from .referals import router as referals_routers

routers = [
    msg_routers,
    bonus_card_routers,
    message_order_routers,
    history_orders_routers,
    start_shop_routers,
    need_help_routers,
    current_orders_routers,
    energy_guide_routers,
    referals_routers,
]