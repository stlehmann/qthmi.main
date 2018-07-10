# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
from typing import Iterable

try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__: Iterable[str] = extend_path(__path__, __name__)
