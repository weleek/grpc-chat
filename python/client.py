#-*- coding: utf-8 -*-

import os, sys, time, logging, grpc, datetime
from concurrent import futures
from threading import Thread

import network_pb2 as desc
import network_pb2_grpc as ngrpc

class Client():
    _instance = None
    _isStop = False

    @classmethod
    def _getInstance(cls):
        return cls._instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls._instance = cls(*args, **kargs)
        cls.instance = cls._getInstance
        return cls._instance

    # 멀티 프로세싱을 이용하여 입력과 출력을 구분하기 위해 멤버 변수로 선언 및 초기화
    def __init__(self, username: str, password: str):
        self._username = username
        self._channel = grpc.insecure_channel('localhost:50051')
        self._stub = ngrpc.NetworkStub(self._channel)
        self._session = self._stub.Login(desc.LoginRequest(username=self._username, password=password)).session

    # 로그아웃을 하기 위해 해당 함수를 호출한다.
    def destroy(self):
        print("\nClient stop...")
        self._isStop = True
        self._stub.Logout(desc.LogoutRequest(session=self._session))

    # Object로 전달 받은 메세지 protobuf를 string 형태로 포맷하여 돌려준다.
    def format_message(self, message):
        return '\n<{username}> {text}'.format(
                username = message.username,
                text = message.text
        )

    # 응답 메세지 출력
    def chat_output(self):
        while self._isStop is False:
            for message in self._stub.Stream(desc.StreamRequest(session=self._session)):
                if message.username != self._username: print(self.format_message(message))

    # 메세지 전달
    def chat_input(self):
        while True:
            text = input("{} > ".format(self._username))  # 메세지 입력
            if text == "": continue                 # 엔터만 입력한 경우는 전송되지 않음
            if text == "exit":
                self._isStop = True
                break
            self._stub.SendMessage(desc.SendMessageRequest(session=self._session, text=text))   # 메세지 전달

def start():
    c = None
    while True: # 유효한 인증정보로 연결이 완료 될때까지 시도 한다.
        username = input("What's your name?\nusername > ")
        while username is None or username is "":
            username = input("What's your name?\nusername > ")
   
        password = input("Enter the password.\npassword > ")
        while password is None or password is "":
            password = input("Enter the password.\npassword > ")

        try:
            c = Client.instance(username, password)
        except:
            print("Invalid connection information.")
        if c is not None: break

    try:
        th = Thread(target=c.chat_output)   # 서버로부터 수신된 내역을 출력한다.
        th.start()                          # 해당 기능 쓰레드로 동작 시켜서 입력과 관계없이 출력할 수 있도록 한다.
    
        c.chat_input()                      # 사용자로부터 입력 받는 부분을 구동한다.
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    finally:
        if c is not None: c.destroy()       # 임의로 종료 하였을 경우 로그아웃을 호출한다.
        
