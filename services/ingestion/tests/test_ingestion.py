import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Import the modules we want to test
from app.change_detection import ChangeDetector
from app.acl_capture import ACLCapture
from app.mcp_client import MCPClient

@pytest.fixture
def mock_db():
    """Mock database for testing"""
    db = Mock()
    db.files = Mock()
    db.change_history = Mock()
    db.permissions = Mock()
    db.command = AsyncMock(return_value={"ok": 1})
    return db

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    redis = Mock()
    redis.ping = Mock(return_value=True)
    return redis

class TestChangeDetector:
    """Test the ChangeDetector class"""
    
    @pytest.mark.asyncio
    async def test_detect_changes_new_items(self, mock_db):
        """Test detecting new items"""
        detector = ChangeDetector(mock_db)
        
        # Mock stored items (empty)
        mock_db.files.find.return_value = []
        
        # Current items
        current_items = [
            {"id": "1", "name": "file1.txt", "size": 100},
            {"id": "2", "name": "file2.txt", "size": 200}
        ]
        
        changes = await detector.detect_changes("tenant1", "box", current_items)
        
        assert len(changes["added"]) == 2
        assert len(changes["modified"]) == 0
        assert len(changes["deleted"]) == 0
        assert len(changes["unchanged"]) == 0
    
    @pytest.mark.asyncio
    async def test_detect_changes_modified_items(self, mock_db):
        """Test detecting modified items"""
        detector = ChangeDetector(mock_db)
        
        # Mock stored items
        stored_items = [
            {"file_id": "1", "name": "file1.txt", "size": 100, "modified_at": "2023-01-01"}
        ]
        
        mock_cursor = Mock()
        mock_cursor.__aiter__ = lambda self: iter(stored_items)
        mock_db.files.find.return_value = mock_cursor
        
        # Current items (modified size)
        current_items = [
            {"id": "1", "name": "file1.txt", "size": 150, "modified_at": "2023-01-02"}
        ]
        
        changes = await detector.detect_changes("tenant1", "box", current_items)
        
        assert len(changes["added"]) == 0
        assert len(changes["modified"]) == 1
        assert len(changes["deleted"]) == 0
        assert len(changes["unchanged"]) == 0

class TestACLCapture:
    """Test the ACLCapture class"""
    
    def test_process_box_permission(self):
        """Test processing Box permissions"""
        acl = ACLCapture()
        
        box_permission = {
            "id": "perm1",
            "accessible_by": {
                "id": "user1",
                "name": "John Doe",
                "login": "john@example.com",
                "type": "user"
            },
            "role": "editor",
            "status": "accepted",
            "permissions": {
                "can_download": True,
                "can_preview": True,
                "can_edit": True,
                "can_delete": False,
                "can_upload": True,
                "can_comment": True
            }
        }
        
        processed = acl._process_permission(box_permission, "box")
        
        assert processed["permission_id"] == "perm1"
        assert processed["accessible_by"]["name"] == "John Doe"
        assert processed["permissions"]["can_edit"] == True
        assert processed["permissions"]["can_delete"] == False
    
    def test_process_microsoft_permission(self):
        """Test processing Microsoft permissions"""
        acl = ACLCapture()
        
        ms_permission = {
            "id": "perm1",
            "grantedTo": {
                "user": {
                    "id": "user1",
                    "displayName": "Jane Doe",
                    "mail": "jane@example.com"
                }
            },
            "roles": ["read", "write"],
            "link": {
                "type": "view",
                "scope": "anonymous"
            }
        }
        
        processed = acl._process_permission(ms_permission, "sharepoint")
        
        assert processed["permission_id"] == "perm1"
        assert processed["granted_to"]["user"]["displayName"] == "Jane Doe"
        assert "read" in processed["roles"]
        assert processed["link"]["type"] == "view"

class TestMCPClient:
    """Test the MCPClient class"""
    
    def test_initialization(self):
        """Test MCP client initialization"""
        client = MCPClient()
        
        assert "box" in client.base_urls
        assert "sharepoint" in client.base_urls
        assert "onedrive" in client.base_urls
        assert client.base_urls["box"] == "http://mcp-box-server:8086"
        assert client.base_urls["sharepoint"] == "http://mcp-files-server:8087"
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check when server is down"""
        client = MCPClient()
        
        # Mock httpx client to simulate failure
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get.return_value.raise_for_status.side_effect = Exception("Connection failed")
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            is_healthy = await client.health_check("box")
            assert is_healthy == False

if __name__ == "__main__":
    # Run basic tests
    print("Running ingestion service tests...")
    
    # Test ChangeDetector
    detector = ChangeDetector(Mock())
    print("✅ ChangeDetector initialized")
    
    # Test ACLCapture
    acl = ACLCapture()
    print("✅ ACLCapture initialized")
    
    # Test MCPClient
    mcp = MCPClient()
    print("✅ MCPClient initialized")
    
    print("All basic tests passed!")
