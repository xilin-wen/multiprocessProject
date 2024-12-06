import jwt

class Authority:
    """
        构造并发送一个完整的 HTTP 响应。

        :param token: token信息
        :param verify_identity: 是否需要验证角色信息
        :param verify_token: 是否需要验证token
    """

    def __init__(self, token: str = None, *, verify_identity: bool = True, verify_token: bool = True):
        self.token = token
        self.secret_key = "pandage"
        self.verify_token = verify_token
        self.verify_identity = verify_identity
        self.user_info = None  # 存储解析后的用户信息
        self.decode_token = None

        if self.verify_token and self.token:
            if self.validate_token():
                if self.verify_identity:
                    self.user_info = self.validate_identity()

    def validate_token(self):
        try:
            # self.decode_token = jwt.decode(self.token, self.secret_key, algorithms=['HS256'])
            self.decode_token = "这是一个解析后的token"
            return True
        except jwt.ExpiredSignatureError:
            return False  # 如果 token 已过期
        except jwt.InvalidTokenError:
            return False  # 如果 token 无效

    def validate_identity(self):
        if not self.decode_token:
            self.validate_token()

        user_role = self.decoded_token.get('user_role')

        if user_role:
            return {"user_role": user_role}
        else:
            return None

    def get_decoded_info(self):
        return_info = {
            "user_token": self.decode_token
        }

        if self.user_info:
            return_info["role"] = self.user_info

        return return_info