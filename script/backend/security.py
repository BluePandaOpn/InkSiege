import hashlib
import os

class SecurityManager:
    @staticmethod
    def get_hash(file_path):
        """Genera un hash SHA256 para validar integridad."""
        if not os.path.exists(file_path): return None
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha.update(chunk)
        return sha.hexdigest()

    @staticmethod
    def is_safe(file_path, lock_path):
        """Compara el archivo actual con su 'candado' digital."""
        if not os.path.exists(lock_path): return True
        with open(lock_path, "r") as f:
            saved_hash = f.read().strip()
        return SecurityManager.get_hash(file_path) == saved_hash