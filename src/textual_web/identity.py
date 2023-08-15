import os

SEPARATOR = "-"
IDENTITY_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTUVWYZ"
IDENTITY_SIZE = 12


def generate(size: int = IDENTITY_SIZE) -> str:
    """Generate a random identifier."""
    alphabet = IDENTITY_ALPHABET
    return "".join(alphabet[byte % 31] for byte in os.urandom(size))
