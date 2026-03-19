import hashlib
import os

class SecurityManager:
    @staticmethod
    def calculate_hash(file_path):
        if not os.path.exists(file_path): return None
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha.update(chunk)
        return sha.hexdigest()

    @staticmethod
    def verify(file_path, expected_hash):
        return SecurityManager.calculate_hash(file_path) == expected_hash