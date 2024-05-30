#!/usr/bin/env python3
# setup a ipv6 TCP server
import socket
import sys

def main():
      # Create a TCP/IP socket
      sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
   
      # Bind the socket to the address
      host = '::0'
      port = 5010
      sock.bind((host, port))

      # Listen for incoming connections
      sock.listen(1)

      connection = None
      while True:
            try:
                  # Wait for a connection
                  print('waiting for a connection')
                  # print socket status
                  print('Socket status: ', sock)
                  connection, client_address = sock.accept()
                  print('connection from', client_address)
                  while True:
                        # print  data received from client
                        data = connection.recv(1024)
                        print('received {!r}'.format(data))
            except KeyboardInterrupt:
                  print('Closing server')
                  if connection:
                        connection.close()
                  sock.close()
                  sys.exit()
            except ConnectionResetError:
                  if connection:
                        connection.close()

if __name__ == '__main__':
      main()