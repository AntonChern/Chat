import threading
from tkinter import *

import grpc

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc

import time


class Client:

    def __init__(self, address, port, u: str, window):
        # the frame to put GUI components on
        self.window = window
        self.username = u
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServerStub(channel)
        # create new listening thread for when new message streams come in
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()
        self.__setup_ui()
        self.window.mainloop()

    def __listen_for_messages(self):
        """
        This method will be ran in a separate thread as the main/ui thread, because the for-in call is blocking
        when waiting for new messages
        """
        for note in self.conn.ChatStream(chat.Empty()):  # this line will wait for new messages from the server
            # Add the message to the UI
            self.chat_list.insert(END, "[{} ({})] {}\n".format(note.name, time.ctime(), note.message))

    def send_message(self, event):
        """
        This method is called when user enters something into the textbox
        """
        message = self.entry_message.get()  # retrieve message from the UI
        if message != '':
            n = chat.Note()  # create protobug message
            n.name = self.username  # set the username
            n.message = message  # set the actual message of the note
            self.conn.SendNote(n)  # send the Note to the server

    def __setup_ui(self):
        self.chat_list = Text()
        self.chat_list.pack(side=TOP)
        self.lbl_username = Label(self.window, text=self.username)
        self.lbl_username.pack(side=LEFT)
        self.entry_message = Entry(self.window, bd=5)
        self.entry_message.bind('<Return>', self.send_message)
        self.entry_message.focus()
        self.entry_message.pack(side=BOTTOM)
