#!/usr/bin/env python3
import re
import subprocess
from pathlib import Path

def get_current_version():
    """Lee la versión actual de pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if match:
        return tuple(map(int, match.groups()))
    return (0, 1, 0)

def bump_version(version_type="patch"):
    """Incrementa la versión según el tipo"""
    major, minor, patch = get_current_version()
    
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    return f"{major}.{minor}.{patch}"

def update_files(new_version):
    """Actualiza archivos con la nueva versión"""
    files_to_update = [
        ("pyproject.toml", r'version = "\d+\.\d+\.\d+"', f'version = "{new_version}"'),
        ("gclit/__init__.py", r'__version__ = "\d+\.\d+\.\d+"', f'__version__ = "{new_version}"'),
    ]
    
    for file_path, pattern, replacement in files_to_update:
        path = Path(file_path)
        if path.exists():
            content = path.read_text()
            updated_content = re.sub(pattern, replacement, content)
            path.write_text(updated_content)
            print(f"✅ Updated {file_path}")

def main():
    import sys
    version_type = sys.argv[1] if len(sys.argv) > 1 else "patch"
    
    new_version = bump_version(version_type)
    update_files(new_version)
    
    print(f"🚀 Version bumped to {new_version}")
    
    # Opcional: crear commit y tag automáticamente
    if "--commit" in sys.argv:
        subprocess.run(["git", "add", "pyproject.toml", "gclit/__init__.py"])
        subprocess.run(["git", "commit", "-m", f"chore: bump version to {new_version}"])
        subprocess.run(["git", "tag", f"v{new_version}"])
        print(f"📝 Created commit and tag v{new_version}")

if __name__ == "__main__":
    main()