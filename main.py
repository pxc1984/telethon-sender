import asyncio
import toml
from telethon import TelegramClient
from telethon.errors import RPCError, PeerFloodError, ChatAdminRequiredError, UserNotParticipantError

# Load configuration from the .toml file
config = toml.load('config.toml')

api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']
phone_number = config['telegram']['phone_number']
channel_id = config['telegram']['channel_id']

# Initialize the TelegramClient
client = TelegramClient('anon', api_id, api_hash)

async def send_test_message():
    try:
        # Attempt to get the input entity for the channel
        entity = await client.get_input_entity(channel_id)
        
        await client.send_message(entity, "Test message from my bot!")
        print("Message sent successfully")
    except RPCError as e:
        print(f"Failed to send message: {e}")
    except ValueError as e:
        print(f"ValueError: {e}. Please check the channel ID.")
    except (PeerFloodError, ChatAdminRequiredError, UserNotParticipantError) as e:
        print(f"Error related to permissions or bot participation: {e}")

# Main function that runs the bot every hour
async def run_bot():
    await client.start(phone_number)
    while True:
        await send_test_message()
        await asyncio.sleep(10)  # Sleep for 1 hour

# Running the bot
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())
