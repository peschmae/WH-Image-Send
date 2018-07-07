from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers import EventCallback
import datetime
import os
from yowsup.layers.protocol_contacts.protocolentities import *
from yowsup.layers.protocol_chatstate.protocolentities import *
from yowsup.layers.protocol_media.protocolentities import *
from yowsup.layers.protocol_media.mediauploader import MediaUploader
from yowsup.common.tools import Jid
import sys
from time import sleep


class WhatsappImageSendLayer(YowInterfaceLayer):
    PROP_RECEIPT_AUTO       = "org.openwhatsapp.yowsup.prop.cli.autoreceipt"
    PROP_RECEIPT_KEEPALIVE  = "org.openwhatsapp.yowsup.prop.cli.keepalive"
    PROP_CONTACT_JID        = "org.openwhatsapp.yowsup.prop.cli.contact.jid"
    EVENT_LOGIN             = "org.openwhatsapp.yowsup.event.cli.login"
    EVENT_START             = "org.openwhatsapp.yowsup.event.cli.start"
    EVENT_SENDANDEXIT       = "org.openwhatsapp.yowsup.event.cli.sendandexit"
    EVENT_REMOVE_PARTICIPANTS = "org.openwhatsapp.yowsup.event.cli.removeallparticipants"

    MESSAGE_FORMAT          = "[{FROM}({TIME})]:[{MESSAGE_ID}]\t {MESSAGE}"

    FAIL_OPT_PILLOW         = "No PIL library installed, try install pillow"
    FAIL_OPT_AXOLOTL        = "axolotl is not installed, try install python-axolotl"

    DISCONNECT_ACTION_PROMPT = 0
    DISCONNECT_ACTION_EXIT   = 1

    ACCOUNT_DEL_WARNINGS = 4

    def __init__(self, image_path=None, phone_number=None):
        super(WhatsappImageSendLayer, self).__init__()
        YowInterfaceLayer.__init__(self)
        self.accountDelWarnings = 0
        self.connected = False
        self.username = None
        self.sendReceipts = True
        self.sendRead = True
        self.disconnectAction = self.__class__.DISCONNECT_ACTION_PROMPT
        self.credentials = None
        self.image_path = image_path
        self.phone_number = phone_number

        #add aliases to make it user to use commands. for example you can then do:
        # /message send foobar "HI"
        # and then it will get automaticlaly mapped to foobar's jid
        self.jidAliases = {
            # "NAME": "PHONE@s.whatsapp.net"
        }


    def output(self, message, tag="general", prompt=True):
        if tag is not None:
            print("%s: %s" % (tag, message))
        else:
            print(message)

    def aliasToJid(self, calias):
        for alias, ajid in self.jidAliases.items():
            if calias.lower() == alias.lower():
                return Jid.normalize(ajid)

        return Jid.normalize(calias)

    def jidToAlias(self, jid):
        for alias, ajid in self.jidAliases.items():
            if ajid == jid:
                return alias
        return jid


    ######## receive #########

    @ProtocolEntityCallback("chatstate")
    def onChatstate(self, entity):
        self.output(entity)

    @ProtocolEntityCallback("iq")
    def onIq(self, entity):
        self.output(entity)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    @ProtocolEntityCallback("ack")
    def onAck(self, entity):
        if entity.getClass() == "message":
            self.output(entity.getId(), tag = "Sent")

    @ProtocolEntityCallback("success")
    def onSuccess(self, entity):
        self.connected = True
        self.output("Logged in!", "Auth", prompt = False)

        print("WhatsappImageSendLayer connected")
        print("Syncing contact: %s" % self.phone_number)
        self.contacts_sync(contacts=self.phone_number)
        sleep(2)
        print("Set state to typing to : %s" % self.phone_number)
        self.state_typing(number=self.phone_number)
        sleep(2)
        print("Send image '%s' to %s" % (self.image_path, self.phone_number))
        self.image_send(number=self.phone_number, path=self.image_path, caption="Test Test Test")
        print("Image send, waiting for image send to finish")

    def doSendMedia(self, mediaType, filePath, url, to, ip=None, caption=None):
        self.output("Do send media called %s" % filePath)
        if mediaType == RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE:
            entity = ImageDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to, caption=caption)
        elif mediaType == RequestUploadIqProtocolEntity.MEDIA_TYPE_AUDIO:
            entity = AudioDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to)
        elif mediaType == RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO:
            entity = VideoDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to, caption=caption)
        elif mediaType == RequestUploadIqProtocolEntity.MEDIA_TYPE_DOCUMENT:
            entity = DocumentDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to)
        self.toLower(entity)
        self.output("Should be save to disconnect")
        sleep(2)
        self.disconnect()

    ########### callbacks ############

    def onRequestUploadResult(self, jid, mediaType, filePath, resultRequestUploadIqProtocolEntity,
                              requestUploadIqProtocolEntity, caption=None):
        self.output("Request upload for file %s to %s received" % (filePath, jid))

        if resultRequestUploadIqProtocolEntity.isDuplicate():
            self.doSendMedia(mediaType, filePath, resultRequestUploadIqProtocolEntity.getUrl(), jid,
                             resultRequestUploadIqProtocolEntity.getIp(), caption)
        else:
            successFn = lambda filePath, jid, url: self.doSendMedia(mediaType, filePath, url, jid,
                                                                    resultRequestUploadIqProtocolEntity.getIp(),
                                                                    caption)
            mediaUploader = MediaUploader(jid, self.getOwnJid(), filePath,
                                          resultRequestUploadIqProtocolEntity.getUrl(),
                                          resultRequestUploadIqProtocolEntity.getResumeOffset(),
                                          successFn, self.onUploadError, self.onUploadProgress, async=False)
            mediaUploader.start()

    def onRequestUploadError(self, jid, path, errorRequestUploadIqProtocolEntity, requestUploadIqProtocolEntity):
        self.output("Request upload for file %s for %s failed" % (path, jid))

    def onUploadError(self, filePath, jid, url):
        self.output("Upload file %s to %s for %s failed!" % (filePath, url, jid))

    def onUploadProgress(self, filePath, jid, url, progress):
        sys.stdout.write("%s => %s, %d%% \r" % (os.path.basename(filePath), jid, progress))
        sys.stdout.flush()

    def image_send(self, number, path, caption=None):
        self.media_send(number, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE, caption)

    def media_send(self, number, path, mediaType, caption=None):
        if self.assertConnected():
            jid = self.aliasToJid(number)
            entity = RequestUploadIqProtocolEntity(mediaType, filePath=path)
            successFn = lambda successEntity, originalEntity: self.onRequestUploadResult(jid, mediaType, path,
                                                                                         successEntity,
                                                                                         originalEntity, caption)
            errorFn = lambda errorEntity, originalEntity: self.onRequestUploadError(jid, path, errorEntity,
                                                                                    originalEntity)
            self._sendIq(entity, successFn, errorFn)

    def state_typing(self, number):
        if self.assertConnected():
            entity = OutgoingChatstateProtocolEntity(ChatstateProtocolEntity.STATE_TYPING, self.aliasToJid(number))
            self.toLower(entity)

    def contacts_sync(self, contacts):
        if self.assertConnected():
            entity = GetSyncIqProtocolEntity(contacts.split(','))
            self.toLower(entity)

    def assertConnected(self):
        if self.connected:
            return True
        else:
            self.output("Not connected", tag="Error", prompt=False)
            return False