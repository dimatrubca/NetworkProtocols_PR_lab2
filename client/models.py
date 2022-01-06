class User:
    def __init__(self, login, email, password) -> None:
        self.name = login
        self.email = email
        self.password = password
        self.is_confirmed = False
        self.confirmation_code =  None
        self.score = 0