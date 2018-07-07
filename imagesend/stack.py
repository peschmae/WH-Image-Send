from .layer import WhatsappImageSendLayer
from yowsup.stacks import YowStackBuilder
from yowsup.layers.auth import AuthError
from yowsup.layers import YowLayerEvent
from yowsup.layers.axolotl.props import PROP_IDENTITY_AUTOTRUST
import sys


class WhatsappImageStack(object):
    def __init__(self, credentials, image_path, encryptionEnabled = True):
        stackBuilder = YowStackBuilder()

        self.stack = stackBuilder\
            .pushDefaultLayers(encryptionEnabled)\
            .push(WhatsappImageSendLayer)\
            .build()

        self.stack.setCredentials(credentials)
        self.stack.setProp(PROP_IDENTITY_AUTOTRUST, True)

    def start(self):
        print("Whatsapp image stack started")
        self.stack.broadcastEvent(YowLayerEvent(WhatsappImageSendLayer.EVENT_START))

        try:
            self.stack.loop()
        except AuthError as e:
            print("Auth Error, reason %s" % e)
        except KeyboardInterrupt:
            print("\nYowsdown")
            sys.exit(0)