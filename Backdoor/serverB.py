import socket 
import os
import subprocess

def config():
    global server
    global target
    global ip 
    global port

    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ip = "192.168.1.12"
    port = 7680

    server.bind((ip, port))

    server.listen(5)
    print("servidor iniciado, esperando conecciones...")

    while True:
        target, addr = server.accept()
        print("coneccion iniciada", addr)
        break


config()
target.close()
