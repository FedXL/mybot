import os
import time
from PyInstaller.__main__ import run
from utils.config import MANAGER_TRADEINN, psws


def create_manager_script_exe(name):
    script = os.path.join(os.path.dirname(__name__), 'app_manager_script', 'manager_script.py')
    opts = [f'--name=manager_script_{name}', '--onefile', script]
    run(opts)
    print('Success')




if __name__ == "__main__":
    a = MANAGER_TRADEINN
    version = '1.02'
    config = os.path.join(os.path.dirname(__name__), 'app_manager_script', 'manager_config.py')
    for key, value in a.items():
        value = value + version
        psw = psws[key]
        with open(config, 'w') as file:
            file.write(f"manager = {key}\nKEY='{psw}'")
        time.sleep(1)
        create_manager_script_exe(value)
