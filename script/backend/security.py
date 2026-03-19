import hashlib
import os

class SecurityManager:
    """Maneja la integridad de los archivos del sistema."""

    @staticmethod
    def calculate_hash(file_path):
        """Genera un hash SHA256 de un archivo."""
        if not os.path.exists(file_path):
            return None
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def verify_integrity(file_path, expected_hash):
        """Compara el hash actual con el hash guardado."""
        current_hash = SecurityManager.calculate_hash(file_path)
        if current_hash == expected_hash:
            return True
        return False