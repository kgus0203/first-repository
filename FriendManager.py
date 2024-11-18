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
