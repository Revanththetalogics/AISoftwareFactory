#!/usr/bin/env python3
"""Analyze coverage.xml to find modules with lowest coverage."""

import xml.etree.ElementTree as ET

def analyze_coverage():
    """Analyze coverage report and print modules with lowest coverage."""
    try:
        tree = ET.parse('coverage.xml')
        root = tree.getroot()
        
        files = []
        for package in root.findall('.//package'):
            for cls in package.findall('class'):
                name = cls.get('filename')
                rate = float(cls.get('line-rate', 0))
                if rate < 1.0:
                    files.append((name, rate))
        
        # Sort by coverage rate (ascending)
        files.sort(key=lambda x: x[1])
        
        print("Modules with lowest coverage:")
        print("-" * 50)
        for name, rate in files[:30]:
            print(f"{rate:6.1%}: {name}")
            
        print(f"\nTotal uncovered modules: {len(files)}")
        print(f"Average coverage of uncovered modules: {sum(rate for _, rate in files) / len(files):.1%}")
        
    except FileNotFoundError:
        print("coverage.xml not found. Run tests with --cov=. first.")
    except Exception as e:
        print(f"Error analyzing coverage: {e}")

if __name__ == "__main__":
    analyze_coverage()