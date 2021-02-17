from abc import ABC, abstractmethod


class LoginHandler(ABC):

    @abstractmethod
    def login(self, login_url: str, redirect_uri: str) -> str:  # pragma: no cover
        pass
