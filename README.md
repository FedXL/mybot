# BOT
### Story of the project
https://youtu.be/WR8vDC4_mnI

## To start bot u should create config.py in utils directory:
from sqlalchemy import create_engine


TOKEN_ASKAR_BOT_HANDLER = 'TELE TOKEN for cms'  
TOKEN_ASKAR = 'TLE TOKEN for crm'  
TOKEN_FED_TEST = 'TELE TOKEN for crm tests'  
TOKEN_BOT_HANDLER = 'TELE TOKEN for cms'  
NAME = "channel name" 



### Admins
TEST_MODE = True  mode for testing  
ADMINS = [Admin1:int,Admin2:int,...] Admins telegram id.  


### Groups and channels for bot
ShipKZ_ORDERS = telegram group id. Bot will send orders here.  
ShipKZ_CATCH_KAZAKHSTAN = telegram group id. Bot will send speaking messages with Tradeinn here.  
ShipKZ_CATCH_TRADINN = telegram group id. Bot will send speaking messages with KAZ here.  
ShipKZ_alerts = telegram channel. Bot will send alerts for Tradeinn managers here.  

### Testing groups

test_orders = test_orders telegram id group. Bot will send orders messages here.
test_group = test kazakhstan telegram id group. Bot will send speaking messages wih KAZ here.
test_chanel = test channel;
test_group_tradinn = test tradeinn group for 
text_channel_support = -1001936578982


### Signature
The clients will see manager short name:
So write anwer like: Hello! The string in sistem will be [Manage short name]: Hello!  
MANAGER = {
    manager_telegram_id: "Manager short name",
}
p.s manager telegram id shold be int.

### Managers in Tradeinn
MANAGER_TRADEINN ={
    telegram_id:'Manager short name',
    109284019: "Alex",
}

### BD test mode
db_user = "user"  
db_host = "host"
db_port = "port"
db_password = "pass"
db_name = "db name"

### BD server mode
db_server_user = "user"
db_server_host = "host"
db_sever_port = "port"
db_server_password = "password"
db_server_name = "name"


if TEST_MODE:  
    orders_chat_storage = test_orders  
    kazakhstan_chat = test_group  
    tradeinn_chat = test_group_tradinn  
    API_TOKEN = TOKEN_FED_TEST  
    user = db_user  
    host = db_host  
    port = db_port  
    password = db_password  
    database = db_name  
    alerts = test_orders  
    flask_host = '0.0.0.0'  
    flask_port = '5000'  
    supported_channel = text_channel_support  
    supported_bot = TOKEN_BOT_HANDLER  
else:  
    orders_chat_storage = ShipKZ_ORDERS  
    kazakhstan_chat = ShipKZ_CATCH_KAZAKHSTAN  
    tradeinn_chat = ShipKZ_CATCH_TRADINN  
    API_TOKEN = TOKEN_ASKAR  
    user = db_server_user  
    host = db_server_host  
    port = db_sever_port  
    password = db_server_password  
    database = db_server_name  
    alerts = ShipKZ_alerts  
    flask_host = 'host'  
    flask_port = 'port'  
    supported_channel = ShipKZ_main_channel  
    supported_bot = TOKEN_ASKAR_BOT_HANDLER  


engine_app = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}', echo=False)  
engine = engine_app  




## Run 5 scripts together:
You can use demons or some task managers
### connector with google sheets
app.py
### Telegram bot
botStart.py
### exchange values parcing
loop_exchange_doble.py
### shop baskets parcing
loop_extract_money.py
### database support
loop_head.py   

