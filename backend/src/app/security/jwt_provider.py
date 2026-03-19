import jwt

class JWTProvider:
    def __init__(self, private_key: str, public_key: str, algorithm: str = "RS256"):
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = algorithm

    def encode(self, **claims) -> str:
        return jwt.encode(claims, self.private_key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        return jwt.decode(
            token,
            self.public_key,
            algorithms=[self.algorithm],
        )