#!/usr/bin/env python3
"""
Test Azure AI Search functionality with real credentials
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_create_search_index():
    """Test creating a search index"""
    print("🔍 Testing Azure AI Search Index Creation...")
    
    search_service = os.getenv('AZURE_SEARCH_SERVICE_NAME')
    search_key = os.getenv('AZURE_SEARCH_API_KEY')
    
    if not search_service or not search_key:
        print("❌ Azure AI Search credentials not found")
        return False
    
    # Test index definition
    index_definition = {
        "name": "test-unstructured-data",
        "fields": [
            {
                "name": "id",
                "type": "Edm.String",
                "key": True,
                "searchable": False
            },
            {
                "name": "content",
                "type": "Edm.String",
                "searchable": True,
                "filterable": False,
                "sortable": False,
                "facetable": False
            },
            {
                "name": "tenant_id",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "sortable": True,
                "facetable": False
            },
            {
                "name": "file_id",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "sortable": True,
                "facetable": False
            },
            {
                "name": "source",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "sortable": True,
                "facetable": True
            },
            {
                "name": "upload_time",
                "type": "Edm.DateTimeOffset",
                "searchable": False,
                "filterable": True,
                "sortable": True,
                "facetable": False
            }
        ]
    }
    
    try:
        url = f"https://{search_service}.search.windows.net/indexes/{index_definition['name']}?api-version=2023-11-01"
        headers = {
            "api-key": search_key,
            "Content-Type": "application/json"
        }
        
        response = requests.put(url, headers=headers, json=index_definition)
        
        if response.status_code == 201:
            print(f"✅ Search index '{index_definition['name']}' created successfully")
            return True
        elif response.status_code == 409:
            print(f"⚠️  Search index '{index_definition['name']}' already exists")
            return True
        else:
            print(f"❌ Failed to create search index: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating search index: {e}")
        return False

def test_search_index():
    """Test searching the index"""
    print("🔎 Testing Azure AI Search...")
    
    search_service = os.getenv('AZURE_SEARCH_SERVICE_NAME')
    search_key = os.getenv('AZURE_SEARCH_API_KEY')
    
    if not search_service or not search_key:
        print("❌ Azure AI Search credentials not found")
        return False
    
    try:
        url = f"https://{search_service}.search.windows.net/indexes/test-unstructured-data/docs?api-version=2023-11-01&search=test"
        headers = {"api-key": search_key}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search query successful - {data.get('@odata.count', 0)} results")
            return True
        else:
            print(f"❌ Search query failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error searching index: {e}")
        return False

def test_document_upload():
    """Test uploading a document to the search index"""
    print("📄 Testing Document Upload...")
    
    search_service = os.getenv('AZURE_SEARCH_SERVICE_NAME')
    search_key = os.getenv('AZURE_SEARCH_API_KEY')
    
    if not search_service or not search_key:
        print("❌ Azure AI Search credentials not found")
        return False
    
    # Test document
    test_document = {
        "value": [
            {
                "id": "test-doc-1",
                "content": "This is a test document for unstructured data indexing",
                "tenant_id": "test-tenant",
                "file_id": "test-file-1",
                "source": "test",
                "upload_time": "2024-01-01T00:00:00Z"
            }
        ]
    }
    
    try:
        url = f"https://{search_service}.search.windows.net/indexes/test-unstructured-data/docs/index?api-version=2023-11-01"
        headers = {
            "api-key": search_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=test_document)
        
        if response.status_code == 200:
            print(f"✅ Document uploaded successfully")
            return True
        else:
            print(f"❌ Document upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading document: {e}")
        return False

def main():
    """Run Azure AI Search tests"""
    print("🚀 Azure AI Search Test Suite")
    print("=" * 40)
    
    tests = [
        test_create_search_index,
        test_document_upload,
        test_search_index
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    passed = sum(results)
    total = len(tests)
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Azure AI Search tests passed!")
    else:
        print("⚠️  Some tests failed - check configuration")
    
    return passed == total

if __name__ == "__main__":
    main()
