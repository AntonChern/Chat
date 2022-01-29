from tkinter import *

import time

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc


class ChatServer(rpc.ChatServerServicer):  # inheriting here from the protobuf rpc file which is generated

    def __init__(self, u: str, window):
        # List with all the chat history
        self.chats = []
        # the frame to put GUI components on
        self.window = window
        self.username = u

        self.__setup_ui()

    def send_message(self, event):
        """
        This method is called when user enters something into the textbox
        """
        message = self.entry_message.get()  # retrieve message from the UI
        if message != '':
            n = chat.Note()  # create protobug message
            n.name = self.username  # set the username
            n.message = message  # set the actual message of the note
            # Add it to the chat history
            self.chats.append(n)
            # Add it to UI
            self.chat_list.insert(END, "[{} ({})] {}\n".format(n.name, time.ctime(), n.message))

    def __setup_ui(self):
        self.chat_list = Text()
        self.chat_list.pack(side=TOP)
        self.lbl_username = Label(self.window, text=self.username)
        self.lbl_username.pack(side=LEFT)
        self.entry_message = Entry(self.window, bd=5)
        self.entry_message.bind('<Return>', self.send_message)
        self.entry_message.focus()
        self.entry_message.pack(side=BOTTOM)

    # The stream which will be used to send new messages to clients
    def ChatStream(self, request_iterator, context):
        """
        This is a response-stream type call. This means the server can keep sending messages
        Every client opens this connection and waits for server to send new messages

        :param request_iterator:
        :param context:
        :return:
        """
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n

    def SendNote(self, request: chat.Note, context):
        """
        This method is called when a clients sends a Note to the server.

        :param request:
        :param context:
        :return:
        """
        # Add request to the chat history
        self.chats.append(request)
        # Add request to UI
        self.chat_list.insert(END, "[{} ({})] {}\n".format(request.name, time.ctime(), request.message))
        return chat.Empty()
