#-*- coding: utf-8 -*-

from concurrent import futures
import os, sys, time, logging, grpc, datetime 
from uuid import uuid4

from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp

import network_pb2 as desc
import network_pb2_grpc as ngrpc

from session import Session, Memory as MemorySession
from authentication import Authentication, Memory as MemoryAuthentication

# 서비스 할 클래스 정의 # proto 파일에 정의 하여 컴파일 된 파일을 참조 한다.
class NetworkServicer (ngrpc.NetworkServicer):
    PLAYBACK_LIMIT = 50
    ONE_DAY_IN_SECONDS = 60 * 60 * 24

    def __init__(self, session_impl, authentication_impl):
        assert isinstance(session_impl, Session)
        assert isinstance(authentication_impl, Authentication)

        self._playback = []

        self._session = session_impl
        self._authentication = authentication_impl

    def Login(self, request, context):
        username = request.username
        password = request.password

        # 사용자 아이디와 비밀번호 확인.
        if not self._authentication.authenticate(username, password):
            print("[{username}] Invalid connection information".format(username=username))
            raise ValueError('invalid credentials')

        session_id = str(uuid4())

        # 인증 처리 이후 세션 생성
        self._session.initialize(session_id, username)

        # 이전 메세지를 보여주기 위해 해당 접속 세션에 메세지를 넣어준다.
        for message in self._playback:
            self._session.append_unread_message(session_id, message)

        print("[SESSION ID:{}] <{}> Login...".format(session_id, username))
        return desc.LoginResponse(session = desc.Session(id=session_id))

    def Logout(self, request, context):
        session_id = request.session.id

        print("[SESSION ID:{}] <{}> Logout...".format(session_id, self._session.get_username(session_id)))
        self._session.delete(session_id)
        return desc.LogoutResponse()

    def SendMessage(self, request, context):
        session_id = request.session.id

        if not self._session.has(session_id):
            raise ValueError('invalid sesion')

        username = self._session.get_username(session_id)
        text = request.text

        message = {
            'timestamp': time.time(),
            'username': username,
            'text': text
        }

        self._playback.append(message)

        self._playback = self._playback[-self.PLAYBACK_LIMIT:]

        for other_session_id in self._session.get_sessions():
            self._session.append_unread_message(other_session_id, message)

        print("[SESSION ID:{}] <{}> {}".format(session_id, username, text))
        return Empty()

    def Stream(self, request, context):
        session_id = request.session.id

        if not self._session.has(session_id):
            #return desc.StreamResponse(username = session_id, text = "Does not exists User.")
            raise ValueError('invalid session')

        for message in self._session.pop_unread_messages(session_id):
            yield desc.StreamResponse(
                timestamp = Timestamp(seconds=int(message['timestamp'])),
                username = message['username'],
                text = message['text']
            )


def serve():
    servicer = NetworkServicer(MemorySession(), MemoryAuthentication({}))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ngrpc.add_NetworkServicer_to_server(servicer, server)

    server.add_insecure_port('[::]:50051')
    server.start()

    try:
        while True:
            time.sleep(NetworkServicer.ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        print("\nServer stop...")
        server.stop(0)








