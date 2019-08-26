#-*- coding: utf-8 -*-

from abc import ABC, abstractmethod

class Authentication(ABC):
    @abstractmethod
    def authenticate(self, username, password):
        pass

class Memory(Authentication):
    def __init__(self, users):
        if len(users.keys()) <= 0:
            # db 연동 하여 사용자 정보를 가져오도록 변경 해야 한다.
            self._users = { "admin":"admin", "user1" : "user1", "user2" : "user2" }
        else: 
            self._users = users

    # 인증 함수 : 서버를 구동시 설정 된 사용자 이름과 비밀번호를 확인 한다.
    def authenticate(self, username, password):
        
        if not username in self._users:
            return False

        return self._users[username] == str(password)


