#!/usr/bin/env python3
"""
NeuroGenesis - Growing Mind with Active Semantic Memory
Main entry point
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠ python-dotenv not installed, skipping .env loading")


def setup_logging():
    """Setup logging configuration"""
    try:
        from loguru import logger
        logs_dir = Path(os.getenv('LOGS_DIR', './logs'))
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / f"neurogenesis_{datetime.now().strftime('%Y%m%d')}.log"
        logger.add(
            log_file,
            rotation="100 MB",
            retention="30 days",
            level=os.getenv('LOG_LEVEL', 'INFO')
        )
        return logger
    except ImportError:
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)


def check_environment():
    """Check if all necessary directories exist"""
    directories = {
        'data': Path(os.getenv('DATA_DIR', './data')),
        'models': Path(os.getenv('MODELS_DIR', './models')),
        'logs': Path(os.getenv('LOGS_DIR', './logs')),
        'config': Path('./config')
    }
    
    print("📁 Checking directories...")
    for name, path in directories.items():
        if path.exists():
            print(f"  ✓ {name}: {path}")
        else:
            print(f"  ⚠ {name}: {path} (creating...)")
            path.mkdir(parents=True, exist_ok=True)
    
    return directories


def display_banner():
    """Display welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🧠  N E U R O G E N E S I S  🧠                ║
║                                                           ║
║          Growing Mind with Semantic Memory                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_dependencies():
    """Check if critical dependencies are installed"""
    dependencies = {
        'numpy': 'numpy',
        'torch': 'PyTorch',
        'transformers': 'Transformers',
    }
    
    print("\n📦 Checking dependencies...")
    missing = []
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} (not installed)")
            missing.append(name)
    
    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main entry point"""
    display_banner()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting NeuroGenesis...")
    
    # Check environment
    dirs = check_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return 1
    
    print("\n" + "="*60)
    print("🚀 System initialized successfully!")
    print("="*60)
    
    print("\n📊 System Status:")
    print(f"  • Python version: {sys.version.split()[0]}")
    print(f"  • Project root: {project_root}")
    print(f"  • Debug mode: {os.getenv('DEBUG', 'False')}")
    print(f"  • Log level: {os.getenv('LOG_LEVEL', 'INFO')}")
    
    print("\n🎯 Next steps:")
    print("  1. Implement semantic memory system (src/memory/)")
    print("  2. Add neural network components (src/core/)")
    print("  3. Create training scripts")
    print("  4. Add data processing utilities")
    print("  5. Implement API endpoints (optional)")
    
    print("\n📚 Documentation:")
    print("  • README.md - Full documentation")
    print("  • QUICK_START.md - Quick start guide")
    
    print("\n💡 Tips:")
    print("  • Use 'make help' to see available commands")
    print("  • Check logs in the logs/ directory")
    print("  • Modify .env file for configuration")
    
    logger.info("NeuroGenesis initialization complete")
    
    # Here you can add your main application logic
    # For example, start a web server, begin training, etc.
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
