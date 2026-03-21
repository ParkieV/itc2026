from pathlib import Path

import jwt

class JWTProvider:
    def __init__(self, private_key_path: str, public_key_path: str, algorithm: str):
        self.private_key = Path(private_key_path).absolute().read_text()
        self.public_key = Path(public_key_path).absolute().read_text()
        self.algorithm = algorithm

    def encode(self, **claims) -> str:
        return jwt.encode(claims, self.private_key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        return jwt.decode(
            token,
            self.public_key,
            algorithms=[self.algorithm],
        )