#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
from threading import Thread
import select
import time

TIMEOUT = 60

class SimSocketServer(Thread):
    def __init__(self, addr):
        Thread.__init__(self, name="SimSocketServer")
        self.connected_clients = []
        self.addr = addr
        self.seqNo = 1
        self.socket_server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.jsonTemplate = {
            "Command": "FORWARD_ELEV_INFO",
            "DeviceId": "C0002T",
        }

    def run(self):
        # setup a server socket and bind to the address and port
        self.socket_server.bind(self.addr)
        self.socket_server.listen(5)
        # 将 socket_server set to non-blocking mode
        self.socket_server.setblocking(False)
        print("Server is listening on", self.addr)
        # store connected client_socket
        self.connected_clients = []
        tp = time.time()
        while True:
            # use select to check if there are any readable sockets
            readable_sockets, _, _ = select.select([self.socket_server] + self.connected_clients, [], [], 30)
            # if no readable sockets and tp is more than 30 seconds ago, close all connected clients
            if not readable_sockets and time.time() - tp > TIMEOUT and self.connected_clients:
                for client in self.connected_clients:
                    client.close()
                self.connected_clients = []
                tp = time.time()
                print("All clients disconnected due to timeout.")

            # handle readable sockets
            for sock in readable_sockets:
                tp = time.time()
                # if sock is self.socket_server, it means there is a new client connection
                if sock is self.socket_server:
                    client_socket, client_address = self.socket_server.accept()
                    self.connected_clients.append(client_socket)
                    print("New client connected:", client_address)
                    print("Current connected clients:", len(self.connected_clients))
                # otherwise, it means there is data to be read from the client socket
                else:
                    try:
                        # if the client is idle for more than 10 seconds, rasie a timeout exception
                        data = sock.recv(1024)
                        if not data:
                            # if no data received, it means the client has disconnected
                            sock.close()
                            print("Client disconnected.")
                            self.connected_clients.remove(sock)
                            continue
                        else:
                            print("Received data:", data.hex())
                    except Exception as e:
                        # error handling
                        print("Error:", e)
                        print("Client disconnected.")
                        sock.close()
                        self.connected_clients.remove(sock)

    def send_msg2client(self, msg):
        assert type(msg) == bytearray
        try:
            # send msg to all connected clients
            for client in self.connected_clients:
                client.send(msg)
        except Exception as e:
            print('send msg error:'.format(e))

# main
if __name__ == '__main__':
    server = SimSocketServer(('::', 5010))
    server.start()
    while True:
        pass