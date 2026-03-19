class Scope:
    def __init__(self, scopes: str):
        self.values = set(scopes.split())

    def is_allowed(self, allowed: set[str]) -> bool:
        return self.values.issubset(allowed)