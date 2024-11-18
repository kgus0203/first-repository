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
