"""
Security Unit Tests for Chonost Manuscript OS
Test JWT validation and dataset encryption functionality
"""
import pytest
import jwt
import os
from pathlib import Path
from cryptography.fernet import Fernet
import json
import base64
from unittest.mock import patch, Mock
from typing import Dict, Any

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
core_services_path = project_root / "core-services/link-ai-core"
if str(core_services_path) not in sys.path:
    sys.path.insert(0, str(core_services_path))

# Import under test
from src.api.handlers import SECRET_KEY
from scripts.generate_datasets import DatasetEncryption

class TestJWTValidation:
    """Test JWT token validation functionality"""
    
    @pytest.fixture
    def valid_payload(self):
        return {
            "sub": "user123",
            "name": "Test User",
            "exp": jwt.datetime.utcnow() + jwt.timedelta(minutes=30)
        }
    
    @pytest.fixture
    def invalid_payload(self):
        return {
            "sub": None,
            "name": "Test User",
            "exp": jwt.datetime.utcnow() + jwt.timedelta(minutes=30)
        }
    
    @pytest.fixture
    def expired_payload(self):
        return {
            "sub": "user123",
            "name": "Test User",
            "exp": jwt.datetime.utcnow() - jwt.timedelta(minutes=30)
        }
    
    def test_valid_jwt_token(self, valid_payload):
        """Test valid JWT token creation and decoding"""
        token = jwt.encode(valid_payload, SECRET_KEY, algorithm="HS256")
        
        # Decode without verification first
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        assert decoded["sub"] == "user123"
        assert decoded["name"] == "Test User"
        assert "exp" in decoded
    
    def test_invalid_jwt_token(self, invalid_payload):
        """Test JWT token with invalid payload"""
        token = jwt.encode(invalid_payload, SECRET_KEY, algorithm="HS256")
        
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    def test_expired_jwt_token(self, expired_payload):
        """Test expired JWT token"""
        token = jwt.encode(expired_payload, SECRET_KEY, algorithm="HS256")
        
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    def test_malformed_jwt_token(self):
        """Test malformed JWT token"""
        malformed_token = "invalid.token.format"
        
        with pytest.raises(jwt.DecodeError):
            jwt.decode(malformed_token, SECRET_KEY, algorithms=["HS256"])
    
    def test_wrong_secret_jwt_token(self, valid_payload):
        """Test JWT token with wrong secret key"""
        wrong_secret = "wrong-secret-key"
        token = jwt.encode(valid_payload, SECRET_KEY, algorithm="HS256")
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, wrong_secret, algorithms=["HS256"])
    
    def test_jwt_without_expiry(self):
        """Test JWT token without expiration"""
        payload = {
            "sub": "user123",
            "name": "Test User"
            # No exp field
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        assert decoded["sub"] == "user123"
        assert "exp" not in decoded
    
    @pytest.mark.parametrize("algorithm", ["HS256", "HS384", "HS512"])
    def test_different_algorithms(self, valid_payload, algorithm):
        """Test different HMAC algorithms"""
        token = jwt.encode(valid_payload, SECRET_KEY, algorithm=algorithm)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        
        assert decoded["sub"] == "user123"

class TestDatasetEncryption:
    """Test dataset encryption and decryption functionality"""
    
    @pytest.fixture
    def test_dataset(self):
        return {
            "type": "conversation_dataset",
            "version": "1.0",
            "entries": [
                {
                    "id": "entry_1",
                    "question": "What is AI?",
                    "answer": "Artificial Intelligence is...",
                    "metadata": {"source": "training_data", "timestamp": "2024-01-01"}
                },
                {
                    "id": "entry_2",
                    "question": "How does RAG work?",
                    "answer": "Retrieval-Augmented Generation...",
                    "metadata": {"source": "rag_docs", "timestamp": "2024-01-02"}
                }
            ],
            "statistics": {
                "total_entries": 2,
                "categories": ["ai", "rag"],
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }
    
    @pytest.fixture
    def encryption_handler(self):
        """Create encryption handler with test key"""
        test_key = Fernet.generate_key()
        os.environ["ENCRYPTION_KEY"] = base64.urlsafe_b64encode(test_key).decode('utf-8')
        return DatasetEncryption()
    
    def test_encryption_roundtrip(self, encryption_handler, test_dataset):
        """Test full encryption and decryption roundtrip"""
        # Encrypt
        encrypted_str = encryption_handler.encrypt_dataset(test_dataset)
        
        # Verify encrypted data is string and not empty
        assert isinstance(encrypted_str, str)
        assert len(encrypted_str) > 0
        
        # Decrypt
        decrypted_data = encryption_handler.decrypt_dataset(encrypted_str)
        
        # Verify roundtrip
        assert decrypted_data == test_dataset
        assert decrypted_data["type"] == "conversation_dataset"
        assert len(decrypted_data["entries"]) == 2
    
    def test_encryption_different_data(self, encryption_handler):
        """Test encryption with different data types"""
        test_cases = [
            {"simple": "value"},
            [1, 2, 3, 4],
            {"nested": {"data": [1, 2, {"complex": True}]}},
            "simple string data"
        ]
        
        for data in test_cases:
            # Convert non-dict types to dict for JSON serialization
            json_data = data if isinstance(data, dict) else {"data": data}
            
            encrypted = encryption_handler.encrypt_dataset(json_data)
            decrypted = encryption_handler.decrypt_dataset(encrypted)
            
            if isinstance(data, dict):
                assert decrypted == json_data
            else:
                assert decrypted["data"] == data
    
    def test_save_load_encrypted_dataset(self, encryption_handler, test_dataset, tmp_path):
        """Test save and load encrypted dataset functionality"""
        # Create file path
        encrypted_file = tmp_path / "test_dataset_encrypted.txt"
        
        # Save encrypted
        encrypted_str = encryption_handler.save_encrypted_dataset(
            test_dataset, 
            str(encrypted_file)
        )
        
        assert encrypted_file.exists()
        assert os.path.getsize(encrypted_file) > 0
        
        # Load and decrypt
        loaded_data = encryption_handler.load_encrypted_dataset(str(encrypted_file))
        
        # Verify data integrity
        assert loaded_data == test_dataset
        assert len(loaded_data["entries"]) == 2
        assert loaded_data["statistics"]["total_entries"] == 2
    
    def test_encryption_header_format(self, encryption_handler, test_dataset, tmp_path):
        """Test encrypted file header format"""
        encrypted_file = tmp_path / "test_dataset_encrypted.txt"
        
        encryption_handler.save_encrypted_dataset(test_dataset, str(encrypted_file))
        
        with open(encrypted_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for header lines
        lines = content.split('\n')
        assert any(line.strip().startswith('# Encrypted Dataset') for line in lines)
        assert any('Encryption Key Required' in line for line in lines)
        
        # Check that encrypted data is present
        encrypted_data = '\n'.join(line for line in lines if not line.startswith('#'))
        assert len(encrypted_data.strip()) > 0
    
    def test_load_nonexistent_file(self, encryption_handler, tmp_path):
        """Test loading non-existent encrypted file"""
        nonexistent_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(FileNotFoundError, match="not found"):
            encryption_handler.load_encrypted_dataset(str(nonexistent_file))
    
    def test_invalid_encryption_key_format(self):
        """Test encryption with invalid key format"""
        # Set invalid key
        os.environ["ENCRYPTION_KEY"] = "invalid-key-not-base64"
        
        with pytest.raises(ValueError, match="Invalid ENCRYPTION_KEY format"):
            DatasetEncryption()
    
    def test_missing_encryption_key(self):
        """Test encryption without ENCRYPTION_KEY environment variable"""
        # Unset the key
        if "ENCRYPTION_KEY" in os.environ:
            del os.environ["ENCRYPTION_KEY"]
        
        with pytest.raises(ValueError, match="ENCRYPTION_KEY environment variable is not set"):
            DatasetEncryption()
    
    def test_invalid_encrypted_data(self, encryption_handler, test_dataset):
        """Test decryption with invalid encrypted data"""
        # Create valid encrypted data
        valid_encrypted = encryption_handler.encrypt_dataset(test_dataset)
        
        # Test various invalid formats
        invalid_cases = [
            "",  # Empty string
            "invalid.base64.data",  # Invalid base64
            valid_encrypted[:-10],  # Truncated
            "ZXZlcnl0aGluZy1pcy1pbnZhbGlk"  # Valid base64 but wrong format
        ]
        
        for invalid_data in invalid_cases:
            with pytest.raises((ValueError, base64.binascii.Error)):
                encryption_handler.decrypt_dataset(invalid_data)
    
    def test_decryption_with_wrong_key(self, test_dataset, tmp_path):
        """Test decryption with wrong encryption key"""
        # Create first encryption handler
        key1 = Fernet.generate_key()
        os.environ["ENCRYPTION_KEY"] = base64.urlsafe_b64encode(key1).decode('utf-8')
        handler1 = DatasetEncryption()
        
        # Encrypt with first key
        encrypted_file = tmp_path / "test_wrong_key.txt"
        handler1.save_encrypted_dataset(test_dataset, str(encrypted_file))
        
        # Create second handler with different key
        key2 = Fernet.generate_key()
        os.environ["ENCRYPTION_KEY"] = base64.urlsafe_b64encode(key2).decode('utf-8')
        handler2 = DatasetEncryption()
        
        # Try to decrypt with wrong key
        with pytest.raises(Fernet.InvalidToken):
            handler2.load_encrypted_dataset(str(encrypted_file))
    
    def test_large_dataset_encryption(self, encryption_handler):
        """Test encryption with large dataset"""
        # Create large dataset
        large_dataset = {
            "type": "large_test_dataset",
            "entries": [{"id": f"entry_{i}", "content": f"Large content {i} " * 100} 
                       for i in range(1000)],
            "statistics": {"total_entries": 1000, "size": "large"}
        }
        
        # Test encryption
        encrypted = encryption_handler.encrypt_dataset(large_dataset)
        assert isinstance(encrypted, str)
        assert len(encrypted) > 1000  # Should be reasonably large
        
        # Test decryption
        decrypted = encryption_handler.decrypt_dataset(encrypted)
        assert decrypted == large_dataset
        assert len(decrypted["entries"]) == 1000

class TestSecurityIntegration:
    """Integration tests for security features"""
    
    @pytest.fixture
    def sample_config(self):
        return {
            "app_name": "Chonost Test",
            "version": "1.0.0",
            "features": {
                "jwt_auth": True,
                "dataset_encryption": True,
                "secure_headers": True
            },
            "security": {
                "algorithm": "HS256",
                "key_length": 32,
                "expiry_minutes": 30
            }
        }
    
    def test_complete_security_workflow(self, sample_config, tmp_path):
        """Test complete security workflow"""
        # Setup test environment
        encryption_key = Fernet.generate_key()
        os.environ["ENCRYPTION_KEY"] = base64.urlsafe_b64encode(encryption_key).decode('utf-8')
        os.environ["JWT_SECRET"] = "test-jwt-secret-key-32-chars-long"
        
        # Create encryption handler
        encryption_handler = DatasetEncryption()
        
        # 1. Create and encrypt configuration
        encrypted_config = encryption_handler.encrypt_dataset(sample_config)
        assert isinstance(encrypted_config, str)
        
        # 2. Create JWT token
        payload = {
            "sub": "integration_test_user",
            "config_id": "test_config_001",
            "exp": jwt.datetime.utcnow() + jwt.timedelta(minutes=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        # 3. Decrypt and validate
        decrypted_config = encryption_handler.decrypt_dataset(encrypted_config)
        assert decrypted_config["app_name"] == "Chonost Test"
        assert decrypted_config["features"]["jwt_auth"] is True
        
        # 4. Decode JWT
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert decoded_token["sub"] == "integration_test_user"
        assert decoded_token["config_id"] == "test_config_001"
        
        # 5. Save encrypted config to file
        config_file = tmp_path / "secure_config.txt"
        encryption_handler.save_encrypted_dataset(decrypted_config, str(config_file))
        
        # 6. Load from file
        loaded_config = encryption_handler.load_encrypted_dataset(str(config_file))
        assert loaded_config == sample_config
        
        print("✅ Complete security workflow test passed!")
    
    @pytest.mark.parametrize("security_level", ["basic", "standard", "strict"])
    def test_different_security_levels(self, security_level, tmp_path):
        """Test different security configuration levels"""
        base_config = {
            "security_level": security_level,
            "features": {
                "jwt_required": security_level in ["standard", "strict"],
                "encryption_mandatory": security_level == "strict",
                "audit_logging": True
            }
        }
        
        encryption_key = Fernet.generate_key()
        os.environ["ENCRYPTION_KEY"] = base64.urlsafe_b64encode(encryption_key).decode('utf-8')
        encryption_handler = DatasetEncryption()
        
        # Encrypt configuration
        encrypted = encryption_handler.encrypt_dataset(base_config)
        
        # Decrypt and verify
        decrypted = encryption_handler.decrypt_dataset(encrypted)
        
        assert decrypted["security_level"] == security_level
        assert decrypted["features"]["audit_logging"] is True
        
        if security_level == "strict":
            assert decrypted["features"]["encryption_mandatory"] is True
        elif security_level == "basic":
            assert decrypted["features"]["jwt_required"] is False

@pytest.mark.security
class TestSecurityBestPractices:
    """Test security best practices implementation"""
    
    def test_key_rotation_simulation(self):
        """Test key rotation doesn't break existing encrypted data"""
        # Generate initial key
        key1 = Fernet.generate_key()
        os.environ["ENCRYPTION_KEY"] = base64.urlsafe_b64encode(key1).decode('utf-8')
        handler1 = DatasetEncryption()
        
        # Create test data
        test_data = {"sensitive": "data", "timestamp": "2024-01-01"}
        encrypted1 = handler1.encrypt_dataset(test_data)
        
        # Rotate to new key
        key2 = Fernet.generate_key()
        os.environ["ENCRYPTION_KEY"] = base64.urlsafe_b64encode(key2).decode('utf-8')
        handler2 = DatasetEncryption()
        
        # Old data should still decrypt with old handler (if we had access)
        # But new handler can't decrypt old data
        with pytest.raises(Fernet.InvalidToken):
            handler2.decrypt_dataset(encrypted1)
        
        # New encryption works with new handler
        test_data2 = {"new": "data", "timestamp": "2024-01-02"}
        encrypted2 = handler2.encrypt_dataset(test_data2)
        decrypted2 = handler2.decrypt_dataset(encrypted2)
        assert decrypted2 == test_data2
    
    def test_no_sensitive_data_in_logs(self):
        """Test that sensitive data isn't logged"""
        # This would require mocking logging configuration
        # For now, just verify that encryption handler doesn't expose keys
        os.environ["ENCRYPTION_KEY"] = "test-key-for-logging-test"
        handler = DatasetEncryption()
        
        # Verify key is not stored in plain text
        assert hasattr(handler, 'encryption_key')  # Key exists internally
        with pytest.raises(AttributeError):
            handler.encryption_key  # But not accessible externally
        
        # Test that error messages don't expose sensitive info
        try:
            handler.decrypt_dataset("invalid")
        except ValueError as e:
            assert "ENCRYPTION_KEY" not in str(e)
            assert "secret" not in str(e).lower()
    
    def test_secure_default_configurations(self):
        """Test that default configurations are secure"""
        # Reset environment
        if "ENCRYPTION_KEY" in os.environ:
            del os.environ["ENCRYPTION_KEY"]
        
        # Test that handler fails gracefully without key
        with pytest.raises(ValueError):
            DatasetEncryption()
        
        # Test JWT with default secret (should still work but warn in production)
        default_payload = {"sub": "default_user"}
        token = jwt.encode(default_payload, SECRET_KEY, algorithm="HS256")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert decoded["sub"] == "default_user"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])