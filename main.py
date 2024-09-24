#!/usr/bin/env python3

import random
import logging
import asyncio
import toml
import datetime
from telethon import TelegramClient
from telethon.errors import RPCError, PeerFloodError, ChatAdminRequiredError, UserNotParticipantError


config = toml.load('config.toml')

if ('telegram' in config):
    api_id = config['telegram']['api_id']
    api_hash = config['telegram']['api_hash']
    phone_number = config['telegram']['phone_number']
    channel_id: list[str] = config['telegram']['channel_id'].split(';')
else:
    print("config.toml not configured properly")
    exit(1)

DEBUG = False
if ('debug' in config):
    DEBUG = config['debug']['enabled']

client = TelegramClient('anon', api_id, api_hash)

call_stack = []

logger = logging.getLogger("main_logger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('sent.log')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class GoodNightNotifier:
    def __init__(self, entity) -> None:
        self.entity = entity
        
        self.prev_notify = datetime.datetime.now()
        self.next_notify = self.prev_notify
        
        if not DEBUG:
            self.min_delta = 23 * 60 * 60  # 23 часа в секундах
            self.max_delta = 25 * 60 * 60  # 25 часов в секундах
        else:
            self.min_delta = 1
            self.max_delta = 10
        
        self.notify_text = [ "Спокойной ночи" ]
    
    def get_text(self) -> str:
        return random.choice(self.notify_text)
    
    def set_time(self) -> None:
        # Устанавливаем следующее уведомление с рандомной задержкой от 23 до 25 часов
        delta_seconds = random.randint(self.min_delta, self.max_delta)
        self.next_notify = self.prev_notify + datetime.timedelta(seconds=delta_seconds)

    async def run(self) -> None:
        if (datetime.datetime.now() >= self.next_notify):
            await self.send_message()
            self.prev_notify = datetime.datetime.now()
            self.set_time()

    async def send_message(self) -> bool:
        message = self.get_text()
        await client.send_message(self.entity, message)
        logger.info(f"Sent message \"{message}\" to {self.entity.access_hash} with delay {datetime.datetime.now() - self.prev_notify}")
        return True

async def setup_handlers():
    for i in channel_id:
        try: 
            entity = await client.get_input_entity(i)
            
            call_stack.append(GoodNightNotifier(entity))
            logger.info(f"Call generated for {entity.access_hash} successfully")
        except RPCError as e:
            print(f"Failed to send message: {e}")
        except ValueError as e:
            print(f"ValueError: {e}. Please check the channel ID.")
        except (PeerFloodError, ChatAdminRequiredError, UserNotParticipantError) as e:
            print(f"Error related to permissions or bot participation: {e}")


async def run_bot():
    await client.start(phone_number)
    await setup_handlers()
    while True:
        for handler in call_stack:
            await handler.run()
        
        if DEBUG:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(60)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())
