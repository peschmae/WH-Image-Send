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
    stack.loop() #this is the program mainloop


#    path="/home/peschmae/projects/photobooth/image-send/peterclown.jpg"
#    whatsapp_stack = WhatsappImageStack(credentials=credentials)
#    print("Trying to login")
#    whatsapp_stack.login(username=username, password=password)
#    print("Syncing: %s" % phone_number)
#    whatsapp_stack.contacts_sync(contact=phone_number)
#    sleep(2)
#    print("Syncing: %s" % phone_number)
#    whatsapp_stack.state_typing(number=phone_number)
#    sleep(2)
#    print("Send image '%s' to %s" % (path, phone_number))
#    whatsapp_stack.image_send(number=phone_number, path=path, caption="Test Test Test")
#    print("Image send, waiting 5 seconds before disconnect")
#    sleep(5)
#    whatsapp_stack.disconnect()
#    print("Disconnected from WhatsApp")
