from utls.encrypt import encrypt


class Identity:
    SALT = "?$zrgj2023$?"
    EXISTING_DURATION = 60 * 10

    def __init__(self, ID, account, request, response):
        self.account = account
        self.uuid = encrypt(ID)
        self.request = request
        self.response = response

    def get_account(request):
        return request.get_signed_cookie(key="account", default=-1, salt=Identity.SALT)

    def sign(self):
        r"""
        签名
        """
        self._set_session()
        self._set_cookie()

    def _set_session(self):
        self.request.session["uuid"] = self.uuid
        self.request.session["account"] = self.account
        self.request.session.set_expiry(self.EXISTING_DURATION)

    def _set_cookie(self):
        self.response.set_signed_cookie(
            key="uuid", value=self.uuid, salt=self.SALT, max_age=self.EXISTING_DURATION
        )
        self.response.set_signed_cookie(
            key="account",
            value=self.account,
            salt=self.SALT,
            max_age=self.EXISTING_DURATION,
        )

    @staticmethod
    def valid(request):
        # 取出cookie存储信息
        uuid = request.get_signed_cookie(key="uuid", default=-1, salt=Identity.SALT)
        account = request.get_signed_cookie(
            key="account", default=-1, salt=Identity.SALT
        )
        if (uuid == -1) or (account == -1):
            return False
        # 验证session
        s_uuid = request.session.get("uuid", -1)
        s_account = request.session.get("account", -1)
        if s_uuid == uuid and s_account == account:
            return True
        return False

    @staticmethod
    def drop(request, response):
        # 删除cookie存储信息

        uuid = request.get_signed_cookie(key="uuid", default=-1, salt=Identity.SALT)
        account = request.get_signed_cookie(
            key="account", default=-1, salt=Identity.SALT
        )
        if (uuid != -1) and (account != -1):
            response.delete_cookie("uuid")
            response.delete_cookie("account")
        # 删除session
        request.session.clear()

    @staticmethod
    def set_code(request, code):
        request.session["code"] = code
        request.session.set_expiry(60)

    @staticmethod
    def valid_code(request, code):
        store_code = request.session.get('code', None)
        if store_code is None or str(store_code) != str(code):
            return False
        return True
