from .start import router as msg_routers
from .openshift import router as openshift
from .closeshift import router as closeshift

routers = [
    msg_routers,
    openshift,
    closeshift,
]