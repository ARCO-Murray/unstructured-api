import json
import logging

from azure.servicebus.aio import ServiceBusClient

from src import env


max_message_count = int(env.QUEUE_MESSAGE_COUNT)
max_wait_time = int(env.QUEUE_WAIT_TIME)

async def retrieve_messages():
    connection_string = env.SERVICE_BUS_CONNECTION_STRING

    async with ServiceBusClient.from_connection_string(
        conn_str=connection_string, logging_enable=True
    ) as client:
        async with client.get_queue_receiver(queue_name=env.QUEUE_NAME) as receiver:
            messages = await receiver.receive_messages(
                max_message_count=max_message_count,
                max_wait_time=max_wait_time,
            )  # defaults to fetch 1 message
            msg_list = []
            for m in messages:
                await receiver.complete_message(m)
                logging.info(f"message {m.message_id} was completed")
                msg_list.append(json.loads(next(m.body)))
                # receiver.defer_message(m) # Defers message to be retrived by id (arco-wally)
            return msg_list
