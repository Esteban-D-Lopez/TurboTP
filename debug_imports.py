import pkgutil
import langchain
import langchain_community
import importlib
import sys

print(f"LangChain version: {langchain.__version__}")
print(f"LangChain path: {langchain.__path__}")

def find_class(package, class_name):
    print(f"Searching in {package.__name__}...")
    for _, name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            module = importlib.import_module(name)
            if hasattr(module, class_name):
                print(f"FOUND {class_name} in {name}")
                return name
        except Exception as e:
            pass
    return None

print("Searching for EnsembleRetriever...")
# Try standard locations first
try:
    from langchain.retrievers import EnsembleRetriever
    print("Imported from langchain.retrievers")
except ImportError as e:
    print(f"Failed langchain.retrievers: {e}")

try:
    from langchain.retrievers.ensemble import EnsembleRetriever
    print("Imported from langchain.retrievers.ensemble")
except ImportError as e:
    print(f"Failed langchain.retrievers.ensemble: {e}")

try:
    from langchain_community.retrievers import EnsembleRetriever
    print("Imported from langchain_community.retrievers")
except ImportError as e:
    print(f"Failed langchain_community.retrievers: {e}")

# Search manually if above failed
# find_class(langchain, "EnsembleRetriever")
# find_class(langchain_community, "EnsembleRetriever")
