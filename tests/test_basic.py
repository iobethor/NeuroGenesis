"""
Basic tests for NeuroGenesis
"""

import pytest
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_import():
    """Test that the main module can be imported"""
    import src
    assert hasattr(src, '__version__')


def test_project_structure():
    """Test that project structure exists"""
    project_root = Path(__file__).parent.parent
    
    assert (project_root / 'src').exists()
    assert (project_root / 'src' / 'main.py').exists()
    assert (project_root / 'src' / 'core').exists()
    assert (project_root / 'src' / 'memory').exists()
    assert (project_root / 'src' / 'utils').exists()


def test_readme_exists():
    """Test that README exists"""
    project_root = Path(__file__).parent.parent
    assert (project_root / 'README.md').exists()


def test_requirements_exists():
    """Test that requirements.txt exists"""
    project_root = Path(__file__).parent.parent
    assert (project_root / 'requirements.txt').exists()
