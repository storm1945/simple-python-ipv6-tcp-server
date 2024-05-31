#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import socket
from threading import Thread

import select


class SimSocketServer(Thread):
    def __init__(self, addr, logger=None):
        Thread.__init__(self, name="SimSocketServer")
        self.connected_clients = []
        self.addr = addr
        self.seqNo = 1
        self.socket_server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.logger = logger
        self.jsonTemplate = {
            "Command": "FORWARD_ELEV_INFO",
            "DeviceId": "C0002T",
        }

    def run(self):
        self.logger.info('-----------------------------------------------------------')
        self.logger.info("HC SimBattery Server addr:{} started listen...".format(self.addr))
        self.logger.info('-----------------------------------------------------------')
        # setup a server socket and bind to the address and port
        self.socket_server.bind(self.addr)
        self.socket_server.listen(5)
        # 将 socket_server set to non-blocking mode
        self.socket_server.setblocking(False)

        # store connected client_socket
        self.connected_clients = []

        while True:
            # use select to check if there are any readable sockets
            readable_sockets, _, _ = select.select([self.socket_server] + self.connected_clients, [], [], 1)

            # handle readable sockets
            for sock in readable_sockets:
                # if sock is self.socket_server, it means there is a new client connection
                if sock is self.socket_server:
                    client_socket, client_address = self.socket_server.accept()
                    self.connected_clients.append(client_socket)
                    self.logger.info(f"New client connected: {client_address}")
                # otherwise, it means there is data to be read from the client socket
                else:
                    try:
                        data = sock.recv(1024)
                        if not data:
                            # if no data received, it means the client has disconnected
                            sock.close()
                            self.logger.info(f"Client {sock.getpeername()} disconnected")
                            self.connected_clients.remove(sock)
                            continue
                        print(f"Received data from {sock.getpeername()}: {data.decode()}")

                    except Exception as e:
                        # error handling
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


if __name__ == '__main__':
    simSocketServer = SimSocketServer(("::", 5010), logging)
    simSocketServer.start()
    while True:
        try:
            pc_cmd = input('输入命令：\n')
            cmd = bytearray()
            cmd.append(0x01)
            simSocketServer.send_msg2client(cmd)
        except Exception as e:
            print(f'cmd error {e}')
