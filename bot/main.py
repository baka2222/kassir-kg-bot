from .bot import dp, bot
import asyncio
from .handlers.authorization import authorization_router
from .handlers.menu import menu_router
from .handlers.help_handler import help_router
from .handlers.operator_handler import operator_router


async def main():
    dp.include_router(authorization_router)
    dp.include_router(menu_router)
    dp.include_router(help_router)
    dp.include_router(operator_router)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())