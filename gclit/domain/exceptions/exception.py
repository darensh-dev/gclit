# gclit/exceptions.py

class GclitException(Exception):
    """Excepción base para todas las excepciones personalizadas de gclit"""
    pass


class GitProviderException(GclitException):
    """Errores relacionados con el proveedor Git"""
    pass


class LLMProviderException(GclitException):
    """Errores relacionados con el proveedor LLM"""
    pass


class ConfigException(GclitException):
    """Errores de configuración de gclit"""
    pass
