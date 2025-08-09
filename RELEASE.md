# Estos incrementarían patch (0.1.0 → 0.1.1)
git commit -m "fix: resolve memory leak"
git commit -m "chore: update dependencies"

# Estos incrementarían minor (0.1.1 → 0.2.0)  
git commit -m "feat: add new CLI command"

# Estos incrementarían major (0.2.0 → 1.0.0)
git commit -m "feat!: BREAKING CHANGE: remove deprecated API"

python3.12 scripts/bump_version.py major && python -m build
python3.12 scripts/bump_version.py minor && python -m build
python3.12 scripts/bump_version.py && python -m build

pip install dist/gclit-1.0.1-py3-none-any.whl 


