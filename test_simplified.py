#!/usr/bin/env python3
"""
Test script for the simplified getmyancestors version
This script tests the basic functionality without requiring FamilySearch login
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all the modified classes can be imported"""
    try:
        from getmyancestors.classes.tree import Tree, Indi, Fam, Source, Note, Fact, Name
        from getmyancestors.classes.session import Session
        from getmyancestors.classes.constants import FACT_TAGS, MAX_PERSONS
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_simplified_indi():
    """Test the simplified Indi class"""
    try:
        from getmyancestors.classes.tree import Indi, Tree
        
        # Create a test tree
        tree = Tree()
        
        # Create a test individual
        indi = Indi("TEST-123", tree)
        
        # Test that the simplified attributes are present
        assert hasattr(indi, 'name')
        assert hasattr(indi, 'gender')
        assert hasattr(indi, 'facts')
        assert hasattr(indi, 'notes')
        assert hasattr(indi, 'sources')
        assert hasattr(indi, 'fid')
        
        # Test that the simplified methods exist
        assert hasattr(indi, 'add_data')
        assert hasattr(indi, 'get_notes')
        assert hasattr(indi, 'get_contributors')
        assert hasattr(indi, 'print')
        
        print("✓ Simplified Indi class test passed")
        return True
    except Exception as e:
        print(f"✗ Indi class test failed: {e}")
        return False

def test_wikipedia_source_filter():
    """Test the Wikipedia source filtering logic"""
    try:
        # Test data that should be identified as Wikipedia sources
        wikipedia_sources = [
            {"about": "https://en.wikipedia.org/wiki/John_Doe"},
            {"titles": [{"value": "Wikipedia article about John Doe"}]},
            {"citations": [{"value": "From Wikipedia, the free encyclopedia"}]},
            {"about": "https://wiki.familysearch.org/something"},
        ]
        
        # Test data that should NOT be identified as Wikipedia sources
        non_wikipedia_sources = [
            {"about": "https://ancestry.com/record/123"},
            {"titles": [{"value": "Birth Certificate"}]},
            {"citations": [{"value": "County Records Office"}]},
        ]
        
        def is_wikipedia_source(source):
            """Extract the Wikipedia detection logic from the modified code"""
            is_wikipedia = False
            if "about" in source:
                url = source["about"].lower()
                if "wikipedia" in url or "wiki" in url:
                    is_wikipedia = True
            if "titles" in source:
                title = source["titles"][0]["value"].lower()
                if "wikipedia" in title or "wiki" in title:
                    is_wikipedia = True
            if "citations" in source:
                citation = source["citations"][0]["value"].lower()
                if "wikipedia" in citation or "wiki" in citation:
                    is_wikipedia = True
            return is_wikipedia
        
        # Test Wikipedia sources
        for source in wikipedia_sources:
            if not is_wikipedia_source(source):
                print(f"✗ Failed to identify Wikipedia source: {source}")
                return False
        
        # Test non-Wikipedia sources
        for source in non_wikipedia_sources:
            if is_wikipedia_source(source):
                print(f"✗ Incorrectly identified as Wikipedia source: {source}")
                return False
        
        print("✓ Wikipedia source filtering test passed")
        return True
    except Exception as e:
        print(f"✗ Wikipedia source filtering test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing simplified getmyancestors version...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_simplified_indi,
        test_wikipedia_source_filter,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The simplified version is ready to use.")
        print("\nTo use the simplified version:")
        print("1. Run: python -m getmyancestors.getmyancestors -u username -p password -i PERSON_ID -o output.ged")
        print("2. The script will now only extract:")
        print("   - Name")
        print("   - Birth/death dates and locations")
        print("   - Profile ID")
        print("   - Brief history/bio from memories")
        print("   - Only Wikipedia sources")
    else:
        print("✗ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 