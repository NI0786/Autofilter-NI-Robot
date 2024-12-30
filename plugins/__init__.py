#----------------------------------------------------------------------👻👻👻👻👻👻👻-----------------------------------------------------------------------------------
from aiohttp import web
from .route import routes

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app


# THANKS TO NISHANT
# CREDIT @IM_NISHANTT
# PLZ.. DON'T REMOVE THIS CREDIT
# CONTACT FOR DOUBTS ON TG - @IM_NISHANT
#--------------------------------------------------------------------------👻👻👻👻👻👻--------------------------------------------------------------------------