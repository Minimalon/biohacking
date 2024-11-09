from core.utils.tasks import send_message, add

send_message.apply_async()
# add.delay(1, 2)