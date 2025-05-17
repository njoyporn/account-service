from backend_shared.api import router
from backend_shared.configurator import Configurator
from backend_shared.database import setup as dbSetup
from backend_shared.security import setup as securitySetup
from backend_shared.api.utils import Utils
import os

configurator = Configurator(f"{os.getcwd()}/config/account.config.json")
configurator.load_config()
security_setup = securitySetup.Setup(configurator.config)
security_setup.setup_keys()
db_setup = dbSetup.Setup(configurator.config)
db_setup.init_db()
utils = Utils(configurator.config)
utils.verwaltung_create_default_admin_account()
router.run(configurator.config)