"""
Validation Script for DocumentFiller v2.0
Checks environment, dependencies, and configuration
"""

import sys
import os
import subprocess
import json

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.11+)")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} not found: {filepath}")
        return False

def check_backend_structure():
    """Check backend file structure"""
    print("\n" + "="*60)
    print("Backend Structure")
    print("="*60)

    files = [
        ("backend/app.py", "Original API"),
        ("backend/app_enhanced.py", "Enhanced API (v2.0)"),
        ("backend/auth.py", "Authentication module"),
        ("backend/database.py", "Database module"),
        ("backend/batch_processor.py", "Batch processor"),
        ("backend/requirements.txt", "Python dependencies"),
    ]

    results = [check_file_exists(f, desc) for f, desc in files]
    return all(results)

def check_frontend_structure():
    """Check frontend file structure"""
    print("\n" + "="*60)
    print("Frontend Structure")
    print("="*60)

    files = [
        ("frontend/package.json", "Node dependencies"),
        ("frontend/vite.config.ts", "Vite configuration"),
        ("frontend/src/App.tsx", "Main app component"),
        ("frontend/src/pages/Login.tsx", "Login page"),
        ("frontend/src/pages/Dashboard.tsx", "Dashboard page"),
        ("frontend/src/pages/DocumentEditor.tsx", "Document editor"),
        ("frontend/src/pages/Configuration.tsx", "Configuration page"),
        ("frontend/src/components/Layout.tsx", "Layout component"),
        ("frontend/src/components/ProtectedRoute.tsx", "Protected route"),
        ("frontend/src/utils/auth.ts", "Auth utilities"),
    ]

    results = [check_file_exists(f, desc) for f, desc in files]
    return all(results)

def check_docker_setup():
    """Check Docker configuration"""
    print("\n" + "="*60)
    print("Docker Configuration")
    print("="*60)

    files = [
        ("docker-compose.yml", "Docker Compose"),
        ("Dockerfile.backend", "Backend Dockerfile"),
        ("frontend/Dockerfile", "Frontend Dockerfile"),
        (".dockerignore", "Docker ignore"),
        (".env.example", "Environment template"),
    ]

    results = [check_file_exists(f, desc) for f, desc in files]
    return all(results)

def check_documentation():
    """Check documentation files"""
    print("\n" + "="*60)
    print("Documentation")
    print("="*60)

    files = [
        ("WEB_APP_README.md", "Web app guide"),
        ("V2_UPDATES.md", "v2.0 changelog"),
        ("MIGRATION_STATUS.md", "Migration status"),
        ("CODEBASE_OVERVIEW.md", "Codebase overview"),
    ]

    results = [check_file_exists(f, desc) for f, desc in files]
    return all(results)

def check_python_imports():
    """Check if critical Python modules can be imported"""
    print("\n" + "="*60)
    print("Python Module Imports")
    print("="*60)

    modules = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "passlib",
        "jose",
    ]

    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} (not installed)")
            all_ok = False

    return all_ok

def validate_backend_code():
    """Validate backend Python code syntax"""
    print("\n" + "="*60)
    print("Backend Code Validation")
    print("="*60)

    files = [
        "backend/app.py",
        "backend/app_enhanced.py",
        "backend/auth.py",
        "backend/database.py",
        "backend/batch_processor.py",
    ]

    all_ok = True
    for filepath in files:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    compile(f.read(), filepath, 'exec')
                print(f"✅ {filepath} (syntax OK)")
            except SyntaxError as e:
                print(f"❌ {filepath} (syntax error: {e})")
                all_ok = False
        else:
            print(f"⚠️  {filepath} (not found)")
            all_ok = False

    return all_ok

def check_api_endpoints():
    """Check API endpoint definitions"""
    print("\n" + "="*60)
    print("API Endpoints (from app_enhanced.py)")
    print("="*60)

    try:
        with open("backend/app_enhanced.py", 'r') as f:
            content = f.read()

        # Count endpoints
        endpoints = {
            "POST": content.count('@app.post('),
            "GET": content.count('@app.get('),
            "WebSocket": content.count('@app.websocket('),
        }

        print(f"✅ POST endpoints: {endpoints['POST']}")
        print(f"✅ GET endpoints: {endpoints['GET']}")
        print(f"✅ WebSocket endpoints: {endpoints['WebSocket']}")

        total = sum(endpoints.values())
        print(f"✅ Total endpoints: {total}")

        return total >= 10  # Should have at least 10 endpoints
    except Exception as e:
        print(f"❌ Error checking endpoints: {e}")
        return False

def check_database_models():
    """Check database model definitions"""
    print("\n" + "="*60)
    print("Database Models")
    print("="*60)

    try:
        with open("backend/database.py", 'r') as f:
            content = f.read()

        models = [
            "UserModel",
            "DocumentModel",
            "SectionModel",
            "SessionModel",
            "PromptTemplateModel",
            "GenerationHistoryModel",
            "ReviewHistoryModel",
        ]

        all_ok = True
        for model in models:
            if f"class {model}(Base):" in content:
                print(f"✅ {model}")
            else:
                print(f"❌ {model} (not found)")
                all_ok = False

        return all_ok
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def main():
    """Run all validation checks"""
    print("\n" + "="*70)
    print(" "*15 + "DocumentFiller v2.0 Validation")
    print("="*70)

    checks = [
        ("Python Version", check_python_version),
        ("Backend Structure", check_backend_structure),
        ("Frontend Structure", check_frontend_structure),
        ("Docker Setup", check_docker_setup),
        ("Documentation", check_documentation),
        ("Python Imports", check_python_imports),
        ("Backend Code Syntax", validate_backend_code),
        ("API Endpoints", check_api_endpoints),
        ("Database Models", check_database_models),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ {name} check failed with error: {e}")
            results[name] = False

    # Summary
    print("\n" + "="*70)
    print("Validation Summary")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("\n" + "-"*70)
    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    print("-"*70)

    if failed == 0:
        print("\n🎉 All validation checks passed! v2.0 is ready to use.")
        print("\nNext steps:")
        print("1. Start the application: docker-compose up -d")
        print("2. Access at: http://localhost:3000")
        print("3. Register an account and configure OpenWebUI")
        return True
    else:
        print(f"\n⚠️  {failed} validation check(s) failed.")
        print("Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
