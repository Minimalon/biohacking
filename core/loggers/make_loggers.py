from pathlib import Path
import config
from loguru import logger

MAIN_FORMAT="{time} | {level} | {message} | {extra}"

# Фильтер для логов
def make_filters(name):
    def filter(record):
        return record["extra"].get("filter") == name
    return filter

# region Создание директорий для логов
main_log_dir = Path(config.dir_path, 'logs')
main_log_dir.mkdir(parents=True, exist_ok=True)

curl_dir = main_log_dir / 'curl'
curl_dir.mkdir(exist_ok=True)
# endregion

# region Создаёт пути для лога файлов
bot_path = main_log_dir / 'bot.log'
setCommands_path = main_log_dir / 'set_commands.log'
foreman_path = curl_dir / 'foreman.log'
cs_path = curl_dir / 'cs.log'
# endregion

# region Создание лог файлов
async def create_loggers():
    logger.add(bot_path, format=MAIN_FORMAT, filter=make_filters('bot'))
    logger.add(setCommands_path, format=MAIN_FORMAT, filter=make_filters('commands'))
    logger.add(foreman_path, format=MAIN_FORMAT, filter=make_filters('foreman'), rotation='1 week', compression='zip')
    logger.add(cs_path, format=MAIN_FORMAT, filter=make_filters('cs'), rotation='1 week', compression='zip')
# endregion

# region Переменные для логирования
bot_log = logger.bind(filter='bot')
setCommands_log = logger.bind(filter='commands')
foreman_log = logger.bind(filter='foreman')
cs_log = logger.bind(filter='cs')
# endregion