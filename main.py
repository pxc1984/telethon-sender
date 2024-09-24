#!/usr/bin/env python3

import logging
import asyncio
import toml
import datetime
import random
from telethon import TelegramClient
from telethon.errors import RPCError, PeerFloodError, ChatAdminRequiredError, UserNotParticipantError


class GoodNightNotifier:
    def __init__(self, entity) -> None:
        self.entity = entity
        
        self.prev_notify = datetime.datetime.now()
        self.next_notify = self.prev_notify
    
    def get_text(self) -> str:
        return random.choice(messages)
    
    def set_time(self) -> None:
        delta_seconds = base_step + random.randint(0, delta_minus + delta_plus) - delta_minus
        self.next_notify = self.prev_notify + datetime.timedelta(seconds=delta_seconds)

    async def run(self) -> None:
        if (datetime.datetime.now() >= self.next_notify):
            await self.send_message()
            self.prev_notify = datetime.datetime.now()
            self.set_time()

    async def send_message(self, message=None) -> None:
        if message == None:
            message = self.get_text()
        
        await client.send_message(self.entity, message)
        logger.info(f"Sent message \"{message}\" to {self.entity.access_hash} with delay {datetime.datetime.now() - self.prev_notify}")


def load_messages() -> None:
    global messages
    with open("messages.dat", mode="r") as f:
        messages = [i.strip() for i in f.readlines()]
    return

def setup_logging():
    global logger, file_handler, formatter

    logger = logging.getLogger("main_logger")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

async def setup_handlers():
    global call_stack
    call_stack = []
    for i in channel_id:
        try: 
            entity = await client.get_input_entity(i)
            call_stack.append(GoodNightNotifier(entity))
            
            logger.info(f"Call generated for {entity.access_hash} successfully")
        except RPCError as e:
            logger.error(f"Failed to send message: {e}")
        except ValueError as e:
            logger.error(f"ValueError: {e}. Please check the channel ID.")
        except (PeerFloodError, ChatAdminRequiredError, UserNotParticipantError) as e:
            logger.error(f"Error related to permissions or bot participation: {e}")


async def run_bot():
    await client.start(phone_number)
    await setup_handlers()
    while True:
        for handler in call_stack:
            await handler.run()
        
        await asyncio.sleep(60)

def load_config():
    global config, api_id, api_hash, phone_number, channel_id, DEBUG, client_name, \
        delay, enable_randomization, base_step, delta_minus, delta_plus, \
            log_file_name, log_format
    
    config = toml.load('config.toml')
    
    if ('app' in config):
        client_name = config['app']['client_name']
        delay = config['app']['delay']
    else:
        print("config.toml not configured properly [app section]")
        exit(1)
    
    if ('randomization' in config):
        enable_randomization = config['randomization']['enabled']
        if enable_randomization:
            base_step = config['randomization']['base_step']
            delta_minus = config['randomization']['delta_minus']
            delta_plus = config['randomization']['delta_plus']
        else:
            if ('base_step' in config['randomization']):
                base_step = config['randomization']['base_step']
            else:
                base_step = 86400
            delta_minus = 0
            delta_plus = 0
    else:
        base_step = 86400
        delta_minus = 0
        delta_plus = 0
    
    if ('logging' in config):
        log_file_name = config['logging']['file']
        log_format = config['logging']['format']
    else:
        print("config.toml not configured properly [logging section]")
        exit(1)

    if ('telegram' in config):
        api_id = config['telegram']['api_id']
        api_hash = config['telegram']['api_hash']
        phone_number = config['telegram']['phone_number']
        channel_id = config['telegram']['channel_id'].split(';')
    else:
        print("config.toml not configured properly [telegram section]")
        exit(1)


if __name__ == '__main__':
    load_config()
    setup_logging()
    load_messages()
    
    client = TelegramClient(client_name, api_id, api_hash)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())
