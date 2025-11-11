#!/usr/bin/env python3
"""
Validation script to check test files and code structure.
Run this before running actual tests to ensure everything is set up correctly.
"""
import sys
import importlib.util
from pathlib import Path

def check_imports():
    """Check if all required modules can be imported."""
    print("Checking imports...")
    errors = []
    
    try:
        from main import app
        print("  ✓ main.py imports successfully")
    except Exception as e:
        errors.append(f"  ✗ main.py: {e}")
        print(f"  ✗ main.py: {e}")
    
    try:
        from routers import calculator, products, outlets, chat
        print("  ✓ All routers import successfully")
    except Exception as e:
        errors.append(f"  ✗ routers: {e}")
        print(f"  ✗ routers: {e}")
    
    try:
        from services import agent_planner, memory_manager, tool_executor, rag_service, text2sql_service
        print("  ✓ All services import successfully")
    except Exception as e:
        errors.append(f"  ✗ services: {e}")
        print(f"  ✗ services: {e}")
    
    try:
        from models import schemas, database
        print("  ✓ All models import successfully")
    except Exception as e:
        errors.append(f"  ✗ models: {e}")
        print(f"  ✗ models: {e}")
    
    return errors

def check_test_files():
    """Check if test files are syntactically correct."""
    print("\nChecking test files...")
    errors = []
    test_dir = Path(__file__).parent / "tests"
    
    test_files = [
        "test_calculator.py",
        "test_products.py",
        "test_outlets.py",
        "test_agent.py"
    ]
    
    for test_file in test_files:
        test_path = test_dir / test_file
        if not test_path.exists():
            errors.append(f"  ✗ {test_file} not found")
            print(f"  ✗ {test_file} not found")
            continue
        
        try:
            # Try to compile the file
            with open(test_path, 'r') as f:
                code = f.read()
            compile(code, str(test_path), 'exec')
            print(f"  ✓ {test_file} syntax is valid")
        except SyntaxError as e:
            errors.append(f"  ✗ {test_file} has syntax error: {e}")
            print(f"  ✗ {test_file} has syntax error: {e}")
        except Exception as e:
            errors.append(f"  ✗ {test_file} error: {e}")
            print(f"  ✗ {test_file} error: {e}")
    
    return errors

def check_routes():
    """Check if all routes are registered."""
    print("\nChecking routes...")
    try:
        from main import app
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        expected_routes = [
            '/', '/health', '/calculate', '/products', 
            '/outlets', '/chat'
        ]
        
        missing = []
        for expected in expected_routes:
            if expected not in routes:
                missing.append(expected)
                print(f"  ✗ Missing route: {expected}")
            else:
                print(f"  ✓ Route exists: {expected}")
        
        if missing:
            return [f"Missing routes: {', '.join(missing)}"]
        return []
    except Exception as e:
        return [f"Error checking routes: {e}"]

def check_dependencies():
    """Check if required dependencies are available."""
    print("\nChecking dependencies...")
    missing = []
    
    dependencies = {
        'fastapi': 'FastAPI',
        'pydantic': 'Pydantic',
        'sqlalchemy': 'SQLAlchemy',
        'httpx': 'httpx (required for tests)',
        'pytest': 'pytest (required for tests)',
    }
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {name} is available")
        except ImportError:
            missing.append(name)
            print(f"  ✗ {name} is not installed")
    
    return missing

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("Test Validation Script")
    print("=" * 60)
    
    all_errors = []
    missing_deps = []
    
    # Check imports
    errors = check_imports()
    all_errors.extend(errors)
    
    # Check test files
    errors = check_test_files()
    all_errors.extend(errors)
    
    # Check routes
    errors = check_routes()
    all_errors.extend(errors)
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if all_errors:
        print(f"\n❌ Found {len(all_errors)} error(s):")
        for error in all_errors:
            print(f"  {error}")
    else:
        print("\n✓ No structural errors found!")
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies ({len(missing_deps)}):")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nTo install dependencies, run:")
        print("  pip install -r requirements.txt")
        print("\nNote: Tests require pytest and httpx to run.")
    else:
        print("\n✓ All dependencies are installed!")
    
    if not all_errors and not missing_deps:
        print("\n✅ All checks passed! You can run tests with:")
        print("  pytest tests/ -v")
        return 0
    elif not all_errors:
        print("\n⚠️  Code structure is valid, but dependencies are missing.")
        print("   Install dependencies to run tests.")
        return 1
    else:
        print("\n❌ Please fix the errors above before running tests.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

