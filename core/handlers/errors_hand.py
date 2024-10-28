from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent

from core.loggers.bot_logger import Logger
from core.loggers.make_loggers import except_log
from core.utils import texts


async def error_tgBadRequest(event: ErrorEvent):
    await event.update.callback_query.answer('Не нажимайте 2 раза подряд на кнопку')
    except_log.exception(event.exception)
    return


async def error_valueError(event: ErrorEvent, log: Logger):
    except_log.exception(event.exception)
    log.error(str(event.exception))
    if event.update.message is not None:
        await event.update.message.answer(texts.error_head + str(event.exception))
    else:
        await event.update.callback_query.message.answer(texts.error_head + str(event.exception))


async def error_validationError(event: ErrorEvent, log: Logger):
    errors = event.exception.errors()
    log.error(str(event.exception))
    if 'Value error' not in str(event.exception):
        except_log.exception(event.exception)
    for error in errors:
        log.error(str(error))
        if event.update.message is not None:
            await event.update.message.answer(texts.error_head + error['msg'])
        else:
            await event.update.callback_query.message.answer(texts.error_head + error['msg'])


async def error_ConnectionError(event: ErrorEvent, log: Logger):
    log.error(str(event.exception))
    except_log.exception(event.exception)
    if event.update.message is not None:
        await event.update.message.answer(texts.error_head + str(event.exception))
    else:
        await event.update.callback_query.message.answer(texts.error_head + str(event.exception))


async def error_total(event: ErrorEvent, log: Logger):
    except_log.exception(event.exception)
    log.error(str(event.exception))
    if event.update.message is not None:
        await event.update.message.answer(texts.error_head + str(event.exception))
    else:
        await event.update.callback_query.message.answer(texts.error_head + str(event.exception))
