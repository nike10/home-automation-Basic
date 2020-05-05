import RPi.GPIO as GPIO
import time

import logging
import asyncio
from hbmqtt.broker import Broker
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1
#import nest_asyncio
#nest_asyncio.apply()
logger = logging.getLogger(__name__)
import time
import datetime

in1 = 16
in2 = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)

#GPIO.output(in1, False)
#GPIO.output(in2, False)
i=0

config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': ''+':9999'    # 0.0.0.0:1883
        }
    },
    'sys_interval': 10,
    'topic-check': {
        'enabled': False
    }
}

broker = Broker(config)

@asyncio.coroutine
def startBroker():
    yield from broker.start()
i=0

@asyncio.coroutine
def brokerGetMessage():
    C = MQTTClient()
    yield from C.connect('mqtt://localhost:9999/')
    yield from C.subscribe([
        ("relay", QOS_1)
    ])
    logger.info('Subscribed!')
    try:
        for i in range(1,100):
            message = yield from C.deliver_message()
            packet = message.publish_packet
            print(packet.payload.data.decode('utf-8'))
            data=str(packet.payload.data.decode('utf-8'))
            print(data)
            if data=='off':
                GPIO.output(in1, False)
                GPIO.output(in2, False)
            if data=='on':
                GPIO.output(in1, True)
                GPIO.output(in2, True)
            i=i+1
            print(i)
    except ClientException as ce:
        logger.error("Client exception : %s" % ce)

if __name__ == '__main__':
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)
    asyncio.get_event_loop().run_until_complete(startBroker())
    asyncio.ensure_future(brokerGetMessage())
    asyncio.get_event_loop().run_forever()