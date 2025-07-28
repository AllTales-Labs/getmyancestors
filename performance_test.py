#!/usr/bin/env python3
"""
Performance test script to compare different versions of getmyancestors
"""

import time
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all versions can be imported"""
    try:
        # Test original tree classes
        from getmyancestors.classes.tree import Tree as OriginalTree
        print("✓ Original tree classes imported")
        
        # Test ultra-fast tree classes
        from getmyancestors.classes.tree_ultra_fast import Tree as UltraFastTree
        print("✓ Ultra-fast tree classes imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_performance_comparison():
    """Compare the performance characteristics"""
    print("\n=== PERFORMANCE COMPARISON ===")
    print()
    
    print("ORIGINAL VERSION:")
    print("- Downloads ALL sources (hundreds per person)")
    print("- Downloads ALL notes and contributor lists")
    print("- Downloads ALL memories (photos, documents)")
    print("- Downloads ALL facts (occupation, military, etc.)")
    print("- Downloads LDS ordinances")
    print("- Makes ~10-15 API calls per person")
    print("- Expected: 50-100MB GEDCOM files")
    print("- Expected: 10-15 minutes for 4 generations")
    print()
    
    print("SIMPLIFIED VERSION:")
    print("- Downloads only Wikipedia sources")
    print("- Downloads only essential notes (no contributors)")
    print("- Downloads only text-based memories (bios)")
    print("- Downloads only birth/death facts")
    print("- No LDS ordinances")
    print("- Makes ~5-8 API calls per person")
    print("- Expected: 1-5MB GEDCOM files")
    print("- Expected: 3-5 minutes for 4 generations")
    print()
    
    print("ULTRA-FAST VERSION:")
    print("- Downloads NO sources")
    print("- Downloads NO notes")
    print("- Downloads NO memories")
    print("- Downloads only birth/death facts")
    print("- Downloads only family relationships")
    print("- Makes ~2-3 API calls per person")
    print("- Expected: 0.1-0.5MB GEDCOM files")
    print("- Expected: 30-60 seconds for 4 generations")
    print()
    
    print("RECOMMENDATION:")
    print("Use ULTRA-FAST version for quick family tree structure")
    print("Use SIMPLIFIED version if you need Wikipedia sources and bios")
    print("Use ORIGINAL version only if you need everything")

def main():
    """Run performance tests"""
    print("Performance Test for getmyancestors versions")
    print("=" * 50)
    
    if not test_imports():
        print("✗ Import tests failed")
        return
    
    test_performance_comparison()
    
    print("\n" + "=" * 50)
    print("To test the ultra-fast version:")
    print("python3 getmyancestors/getmyancestors_fast.py -u username -p password -i PERSON_ID -a 4 -o ultra_fast.ged")
    print()
    print("To test the simplified version:")
    print("python3 -m getmyancestors.getmyancestors -u username -p password -i PERSON_ID -a 4 -o simplified.ged")

if __name__ == "__main__":
    main() 