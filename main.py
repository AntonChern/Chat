from client import *
from server import *

import grpc

import proto.chat_pb2_grpc as rpc

port = 11912


if __name__ == '__main__':
    root = Tk()
    frame = Frame(root, width=300, height=300)
    frame.pack()
    root.withdraw()
    # retrieve a ... so we can distinguish all the different clients
    address = simpledialog.askstring("Address",
                                     "Enter the address to connect (or leave this field empty if you want to be a "
                                     "server)")

    username = None
    while username is None:
        # retrieve a username so we can distinguish all the different clients
        username = simpledialog.askstring("Username", "What's your username?", parent=root)

    root.deiconify()

    if address == '':
        address = "localhost"

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # create a gRPC server
        rpc.add_ChatServerServicer_to_server(ChatServer(username, frame), server)  # register the server to gRPC

        server.add_insecure_port('[::]:' + str(port))
        server.start()

        frame.mainloop()
        server.stop(10)
    else:
        c = Client(address, port, username, frame)
