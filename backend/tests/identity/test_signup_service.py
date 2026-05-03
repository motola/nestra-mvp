import unittest

from identity.api.schemas import LoginRequest, SignupRequest
from identity.services.signup import _hash_password, _slugify, _verify_password


class TestSlugify(unittest.TestCase):
    def test_lowercase(self) -> None:
        self.assertEqual(_slugify("Acme Corp"), "acme-corp")

    def test_special_characters_replaced(self) -> None:
        self.assertEqual(_slugify("Acme & Sons, Ltd."), "acme-sons-ltd")

    def test_leading_trailing_hyphens_stripped(self) -> None:
        self.assertEqual(_slugify("  AlphaCon  "), "alphacon")

    def test_multiple_spaces_become_single_hyphen(self) -> None:
        self.assertEqual(_slugify("Big   Property   Group"), "big-property-group")

    def test_already_slug(self) -> None:
        self.assertEqual(_slugify("already-slug"), "already-slug")


class TestPasswordHashing(unittest.TestCase):
    def test_hash_is_not_plaintext(self) -> None:
        hashed = _hash_password("secret123")
        self.assertNotEqual(hashed, "secret123")

    def test_verify_correct_password(self) -> None:
        hashed = _hash_password("correct-horse")
        self.assertTrue(_verify_password("correct-horse", hashed))

    def test_verify_wrong_password(self) -> None:
        hashed = _hash_password("correct-horse")
        self.assertFalse(_verify_password("wrong-horse", hashed))

    def test_two_hashes_differ(self) -> None:
        h1 = _hash_password("password")
        h2 = _hash_password("password")
        self.assertNotEqual(h1, h2)


class TestSignupRequestSchema(unittest.TestCase):
    def _valid(self) -> dict[str, str]:
        return {
            "email": "alice@example.com",
            "full_name": "Alice Smith",
            "password": "supersecret",
            "org_name": "Acme Property Group",
            "legal_name": "Acme Property Group Ltd",
        }

    def test_valid_request_parses(self) -> None:
        req = SignupRequest(**self._valid())
        self.assertEqual(req.email, "alice@example.com")

    def test_short_password_rejected(self) -> None:
        from pydantic import ValidationError

        data = self._valid()
        data["password"] = "short"
        with self.assertRaises(ValidationError):
            SignupRequest(**data)

    def test_invalid_email_rejected(self) -> None:
        from pydantic import ValidationError

        data = self._valid()
        data["email"] = "not-an-email"
        with self.assertRaises(ValidationError):
            SignupRequest(**data)


class TestLoginRequestSchema(unittest.TestCase):
    def test_valid_login_request(self) -> None:
        req = LoginRequest(email="bob@example.com", password="anypassword")
        self.assertEqual(req.email, "bob@example.com")


if __name__ == "__main__":
    unittest.main()
