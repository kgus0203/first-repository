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
