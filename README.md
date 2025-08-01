# gclit 🚀

Git CLI assistant powered by LLMs for intelligent commit messages and pull request documentation.

## 📋 Description

**gclit** is a command-line tool that leverages Large Language Models (LLMs) to automatically generate meaningful commit messages and pull request documentation by analyzing your Git diffs. It supports multiple Git providers (GitHub, Azure DevOps) and LLM providers (OpenAI).

## ✨ Features

- 🤖 **AI-powered commit messages**: Generate contextual commit messages from staged changes
- 📝 **Smart PR documentation**: Create comprehensive pull request titles and descriptions
- 🔄 **Multi-provider support**: Works with GitHub and Azure DevOps
- 🌐 **Multi-language**: Support for English and Spanish
- ⚙️ **Flexible configuration**: Easy setup via config files or environment variables
- 🎯 **Clean Architecture**: Built with hexagonal architecture principles

## 🛠️ Installation

### Prerequisites

- Python >= 3.8
- Git repository
- API tokens for your Git provider and LLM provider

### Install from source

```bash
git clone <repository-url>
cd gclit
pip install -e .
```

### Install dependencies

```bash
bashpip install -r requirements.txt
```

# ⚙️ Configuration

gclit can be configured via environment variables or a config file located at `~/.gclit/config.json`.

### Initial Setup

```bash
# Set your OpenAI API key
gclit config set openai.api_key "your-openai-api-key"

### Set your GitHub token
gclit config set github.token "your-github-token"

### Optional: Set your preferred language
gclit config set lang "en"  # or "es"

### Optional: Set your preferred model
gclit config set model "gpt-4o-mini"
```

### View current configuration

```bash
bashgclit config show
```

### Environment Variables

Alternatively, you can use environment variables with the GCLIT\_ prefix:

```bash
export GCLIT_OPENAI__API_KEY="your-openai-api-key"
export GCLIT_GITHUB__TOKEN="your-github-token"
export GCLIT_PROVIDER="openai"
export GCLIT_MODEL="gpt-4o-mini"
export GCLIT_LANG="en"
```

# 🚀 Usage

### Generate Commit Messages

Generate a commit message for your staged changes:

```bash
# Stage your changes first
git add .

### Generate commit message
gclit commit

### Generate and auto-commit
gclit commit --auto

### Generate in Spanish
gclit commit --lang es
```

### Generate Pull Request Documentation

Create a new PR

```bash
# Generate PR from current branch to main
gclit pr --from feature-branch --to main

### Generate PR in Spanish
gclit pr --from feature-branch --to main --lang es
```

Update existing PR

```bash
# Update PR #123 with new documentation
gclit pr --pr 123

### Update PR in Spanish
gclit pr --pr 123 --lang es
```

# 🏗️ Architecture

gclit follows hexagonal architecture principles:

```bash
gclit/
├── domain/           # Business logic and entities
│   ├── models/       # Data models
│   ├── ports/        # Interfaces/contracts
│   └── exceptions/   # Domain exceptions
├── application/      # Use cases
│   └── use_cases/    # Application services
├── infrastructure/   # External adapters
│   ├── git/          # Git provider implementations
│   └── llm/          # LLM provider implementations
├── cli/              # Command-line interface
└── config/           # Configuration management
```

# 🔌 Supported Providers

### Git Providers

- ✅ GitHub: Full support for creating and updating PRs
- ✅ Azure DevOps: Full support for creating and updating PRs

### LLM Providers

- ✅ OpenAI: GPT-4, GPT-3.5-turbo, etc.
- 🔄 Claude: Coming soon
- 🔄 Local models: Coming soon

# 📖 Examples

## Typical Workflow

### 1. Work on your feature:

```bash
git checkout -b feature/user-authentication

# ... make changes ...

git add .
```

### 2. Generate commit message:

```bash
gclit commit --auto
```

### 3. Push and create PR:

```bash
git push origin feature/user-authentication
gclit pr --from feature/user-authentication --to main
```

# Configuration Examples

### GitHub Enterprise

```bash
gclit config set github.token "ghp_your_token_here"
```

### Azure DevOps

```bash
gclit config set azure_devops.token "your_ado_token_here"
```

### Different OpenAI Model

```bash
gclit config set model "gpt-4"
gclit config set provider "openai"
```

# 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`gclit commit --auto`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request (`gclit pr --from feature/amazing-feature --to main`)

# 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# 🆘 Troubleshooting

### Common Issues

#### "Unsupported LLM provider" error:

- Make sure you've set the correct provider: `gclit config set provider "openai`

#### "No staged changes" message:

- Stage your changes first: `git add .`

#### GitHub API errors:

- Verify your token has the necessary permissions (repo scope)
- Check if you're in a Git repository with GitHub remote

#### Azure DevOps connection issues:

- Ensure your token has Code (read & write) permissions
- Verify the repository URL format is correct

#### Getting Help
If you encounter issues:

1. Check your configuration: `gclit config show`
2. Verify your API tokens are valid
3. Ensure you're in a Git repository
4. Check that you have staged changes for commit generation

# 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI interface
- Uses [Pydantic](https://docs.pydantic.dev/latest/) for data validation
- Powered by OpenAI's GPT models
