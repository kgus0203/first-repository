#프렌드유저, 블록 유저, 프렌드 매니저 클래스, 함수 구현

class FriendUser:
    def __init__(self, user_id, name, profile_info):
        """
        FriendUser 클래스는 사용자의 기본 정보를 관리하고,
        친구 및 차단 관리를 위한 메서드를 제공합니다.
        """
        self.__user_id = user_id  # 사용자 고유 식별자
        self.__name = name  # 사용자 이름
        self.__profile_info = profile_info  # 프로필 정보
        self.__friend_list = []  # 친구 목록
        self.__block_list = []  # 차단 목록

    # 사용자 ID getter
    def get_user_id(self):
        return self.__user_id

    # 사용자 이름 getter
    def get_name(self):
        return self.__name

    # 사용자 프로필 정보 getter
    def get_profile_info(self):
        return self.__profile_info

    # 친구 추가
    def add_friend(self, friend_id):
        if friend_id not in self.__friend_list and friend_id != self.__user_id:
            self.__friend_list.append(friend_id)
            return True
        return False

    # 친구 삭제
    def delete_friend(self, friend_id):
        if friend_id in self.__friend_list:
            self.__friend_list.remove(friend_id)
            return True
        return False

    # 사용자 차단
    def block_user(self, user_id):
        if user_id not in self.__block_list and user_id != self.__user_id:
            self.__block_list.append(user_id)
            return True
        return False

    # 차단 해제
    def unblock_user(self, user_id):
        if user_id in self.__block_list:
            self.__block_list.remove(user_id)
            return True
        return False

    # 친구 목록 반환
    def get_friends(self):
        return self.__friend_list

    # 차단된 사용자 목록 반환
    def get_blocked_users(self):
        return self.__block_list

class FriendManager:
    def __init__(self):
        """
        FriendManager 클래스는 사용자의 친구 목록을 관리하며,
        친구 추가, 삭제, 조회 기능을 제공합니다.
        """
        self.__friend_list = []  # 사용자 친구 목록

    # 친구 추가
    def add_friend(self, friend_id):
        """
        친구 목록에 지정된 ID의 사용자를 추가.
        :param friend_id: 추가할 친구의 ID
        :return: 성공 시 True, 실패 시 False
        """
        if friend_id not in self.__friend_list:
            self.__friend_list.append(friend_id)
            return True
        return False

    # 친구 삭제
    def delete_friend(self, friend_id):
        """
        친구 목록에서 지정된 ID의 사용자를 삭제.
        :param friend_id: 삭제할 친구의 ID
        :return: 성공 시 True, 실패 시 False
        """
        if friend_id in self.__friend_list:
            self.__friend_list.remove(friend_id)
            return True
        return False

    # 현재 친구 목록 조회
    def get_friends(self):
        """
        현재 친구 목록 반환.
        :return: 친구 ID 목록
        """
        return self.__friend_list

    # 친구 여부 확인
    def is_friend(self, friend_id):
        """
        지정된 사용자가 친구인지 확인.
        :param friend_id: 확인할 사용자 ID
        :return: 친구인 경우 True, 아니면 False
        """
        return friend_id in self.__friend_list

class BlockManager:
    def __init__(self):
        """
        BlockManager 클래스는 사용자의 차단 목록을 관리하며,
        차단 추가, 해제, 조회 및 확인 기능을 제공합니다.
        """
        self.__block_list = []  # 사용자 차단 목록

    # 사용자 차단
    def block_user(self, user_id):
        """
        차단 목록에 지정된 ID의 사용자를 추가.
        :param user_id: 차단할 사용자의 ID
        :return: 성공 시 True, 실패 시 False
        """
        if user_id not in self.__block_list:
            self.__block_list.append(user_id)
            return True
        return False

    # 차단 해제
    def unblock_user(self, user_id):
        """
        차단 목록에서 지정된 ID의 사용자를 삭제.
        :param user_id: 차단 해제할 사용자의 ID
        :return: 성공 시 True, 실패 시 False
        """
        if user_id in self.__block_list:
            self.__block_list.remove(user_id)
            return True
        return False

    # 차단 여부 확인
    def is_blocked(self, user_id):
        """
        지정된 사용자가 차단 목록에 있는지 확인.
        :param user_id: 확인할 사용자의 ID
        :return: 차단된 경우 True, 아니면 False
        """
        return user_id in self.__block_list

    # 차단 목록 조회
    def get_blocked_users(self):
        """
        현재 차단된 사용자 목록 반환.
        :return: 차단된 사용자 ID 목록
        """
        return self.__block_list
        
