from imagesend.layer import WhatsappImageSendLayer

from yowsup.stacks import  YowStackBuilder
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.axolotl.props import PROP_IDENTITY_AUTOTRUST

credentials = ("436645643863", "hHbeotbYI07EXn+AyeTAaeuD7pA=") # replace with your phone and password
phone_number = "41797428555"
path = "/home/peschmae/projects/photobooth/whatsapp/peterclown.jpg"


if __name__=="__main__":
    print("Initialize StackBuild")
    stackBuilder = YowStackBuilder()

    whatsapp_layer = WhatsappImageSendLayer(phone_number=phone_number, image_path=path)

    print("Starting to build Stack")
    stack = stackBuilder\
        .pushDefaultLayers(True)\
        .push(whatsapp_layer)\
        .build()

    print("Set credentials")
    stack.setCredentials(credentials)
    print("Trying to connect")
    stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))   #sending the connect signal
    stack.setProp(PROP_IDENTITY_AUTOTRUST, True)
    print("start stack.loop")
    stack.loop() #this is the program mainloop. We disconnect from WhatsApp in the main loop, to get back the prompt