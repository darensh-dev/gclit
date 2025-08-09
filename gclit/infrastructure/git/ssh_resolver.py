# gclit/infrastructure/git/ssh_resolver.py
import platform
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from gclit.domain.exceptions.exception import GitProviderException


class SSHConfigResolver:
    """Resuelve configuraciones SSH para identificar proveedores Git"""

    @staticmethod
    def get_ssh_config_path() -> Path:
        """Obtiene la ruta del archivo SSH config según el sistema operativo"""
        home = Path.home()

        if platform.system() == "Windows":
            # Windows: %UserProfile%\.ssh\config
            return home / ".ssh" / "config"
        else:
            # Linux/macOS: ~/.ssh/config
            return home / ".ssh" / "config"

    @staticmethod
    def parse_ssh_config() -> Dict[str, Dict[str, str]]:
        """
        Parsea el archivo SSH config y retorna un diccionario con las configuraciones

        Returns:
            Dict[host_alias, {hostname, user, identity_file, etc.}]
        """
        config_path = SSHConfigResolver.get_ssh_config_path()

        if not config_path.exists():
            return {}

        config = {}
        current_host = None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()

                    # Ignorar comentarios y líneas vacías
                    if not line or line.startswith('#'):
                        continue

                    # Host directive
                    if line.lower().startswith('host '):
                        host_match = re.match(r'host\s+(.+)', line, re.IGNORECASE)
                        if host_match:
                            current_host = host_match.group(1).strip()
                            config[current_host] = {}

                    # Configuraciones del host actual
                    elif current_host and ' ' in line:
                        # Separar clave y valor
                        parts = line.split(None, 1)  # Split en máximo 2 partes
                        if len(parts) == 2:
                            key, value = parts
                            config[current_host][key.lower()] = value

        except Exception as e:
            # Si hay error leyendo el archivo, retornar diccionario vacío
            return {}

        return config

    @staticmethod
    def resolve_git_remote_from_ssh(remote_url: str) -> Optional[Tuple[str, Dict[str, str]]]:
        """
        Intenta resolver información Git usando configuración SSH

        Args:
            remote_url: URL remota Git (ej: git@azure-haintech:Organization/Project/_git/repo)

        Returns:
            Tupla (provider_type, provider_info) o None si no se pudo resolver
        """
        ssh_config = SSHConfigResolver.parse_ssh_config()

        # Extraer host de la URL SSH
        # Formatos soportados:
        # git@host:path
        # ssh://git@host/path
        # host:path

        host_match = None

        # Formato git@host:path
        if '@' in remote_url and ':' in remote_url:
            host_match = re.match(r'git@([^:]+):', remote_url)
        # Formato ssh://git@host/path
        elif remote_url.startswith('ssh://'):
            host_match = re.match(r'ssh://git@([^/]+)/', remote_url)
        # Formato host:path
        elif ':' in remote_url and not remote_url.startswith('http'):
            host_match = re.match(r'([^:]+):', remote_url)

        if not host_match:
            return None

        ssh_host_alias = host_match.group(1)

        # Buscar en la configuración SSH
        if ssh_host_alias not in ssh_config:
            return None

        host_config = ssh_config[ssh_host_alias]
        hostname = host_config.get('hostname', ssh_host_alias)

        # Determinar el proveedor basado en el hostname
        if 'github.com' in hostname:
            # Extraer información del repositorio para GitHub
            repo_match = re.search(r'[:/]([^/]+/[^/]+?)(\.git)?/?$', remote_url)
            if repo_match:
                repo = repo_match.group(1)
                return ('github', {'repo': repo, 'hostname': hostname})

        elif 'ssh.dev.azure.com' in hostname or 'dev.azure.com' in hostname:
            # Formato clásico: git@azure-host:Organization/Project/_git/Repository
            # Formato v3: git@azure-host:v3/Organization/Project/_git/Repository
            repo_match = re.search(r'(?:[:/](?:\w+)[/:])([^/]+)/([^/]+)/([^/]+?)(?:\.git)?$', remote_url)
            if repo_match:
                organization, project, repo = repo_match.groups()
                return ('azure_devops', {
                    'organization': organization,
                    'project': project,
                    'repo': repo,
                    'hostname': hostname
                })

        return None


def get_enhanced_git_remote() -> Tuple[str, Dict[str, str]]:
    """
    Función mejorada para obtener información del remoto Git

    Returns:
        Tupla (provider_type, provider_info)
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True
        )
        url = result.stdout.strip()
    except subprocess.CalledProcessError:
        raise GitProviderException("No se pudo obtener la URL remota del repositorio")

    if "github.com" in url:
        match = re.search(r"(github\.com[:/])(.+?)(\.git)?$", url)
        if match:
            repo = match.group(2)
            return ('github', {'repo': repo})

    elif "dev.azure.com" in url:
        match = re.search(r"dev\.azure\.com/([^/]+)/([^/]+)/_git/([^/]+)", url)
        if match:
            organization, project, repo = match.groups()
            return ('azure_devops', {
                'organization': organization,
                'project': project,
                'repo': repo,
            })

    ssh_result = SSHConfigResolver.resolve_git_remote_from_ssh(url)
    if ssh_result:
        provider_type, provider_info = ssh_result

        if provider_type == 'github':
            return (provider_type, provider_info)

        elif provider_type == 'azure_devops':
            return (provider_type, provider_info)

    # Asumir que es GitHub como último recurso
    if not url.startswith('http'):
        repo_match = re.search(r'[:/]([^/]+/[^/]+?)(\.git)?/?$', url)
        if repo_match:
            repo = repo_match.group(1)
            return ('github', {'repo': repo})

    raise GitProviderException(f"No se pudo determinar el proveedor Git para la URL: {url}")
