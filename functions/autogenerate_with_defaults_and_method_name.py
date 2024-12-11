import inspect
from typing import Any, Dict, Optional, Type, get_origin, get_args
from types import ModuleType, MappingProxyType
from docstring_parser import parse
from langchain_core.pydantic_v1 import BaseModel, Field, create_model
import pickle

def generate_pydantic_classes(module: ModuleType) -> list[Type[BaseModel]]:
    """
    Generate Pydantic classes for each callable (function/method) in a given module.
    
    Extracts parameters from docstrings and function signatures. Each generated class
    has fields corresponding to the parameters of the function. Parameter descriptions
    are taken from the docstring, while default values and types come from the function signature.
    
    Parameters
    ----------
    module : ModuleType
        The Python module from which to extract functions and generate models.
        
    Returns
    -------
    list[Type[BaseModel]]
        A list of Pydantic model classes corresponding to each function.
    """
    base_attributes = set(dir(BaseModel))
    classes_list = []

    for name, func in inspect.getmembers(module, inspect.isfunction):
        # skip if method starts with _
        if name.startswith("_"):
            continue

        doc = inspect.getdoc(func) or ""
        parsed_doc = parse(doc)
        doc_params = {p.arg_name: p.description or "No description available." for p in parsed_doc.params}

        sig = inspect.signature(func)
        fields = {}
        alias_map = {}

        for param_name, param in sig.parameters.items():
            # Skip *args and **kwargs if needed, or handle them differently
            if param_name == "args" or param_name == "kwargs":
                continue

            description = doc_params.get(param_name, "No description available.")

            # Determine default value
            if param.default is not inspect.Parameter.empty:
                default_value = param.default
                # If default_value is a mappingproxy, convert it to a dict
                if isinstance(default_value, MappingProxyType):
                    default_value = dict(default_value)
            else:
                default_value = None

            # Determine type hint
            if param.annotation is not inspect.Parameter.empty:
                annotation =  Any #param.annotation
            else:
                # If no annotation, fallback to Optional[str] or just str
                annotation = Any #Optional[str]

            # If we detect a required parameter with no default, use `...` to make it required
            # If default exists, we use that
            if default_value is not None:
                # If default is None, we can mark as Optional if not already optional
                # If annotation doesn't allow None but default is None, you can adjust accordingly.
                # For simplicity, if default is None and annotation not optional, make it optional
                if default_value is None and annotation is not Any and not _is_optional_type(annotation):
                    annotation = Any #Optional[annotation]
            else:
                # Required parameter, no default
                pass

            field_kwargs = {"description": description, "default": default_value}
            field_name = param_name

            # Alias if conflicts with BaseModel attributes
            if param_name in base_attributes:
                aliased_name = param_name + "_param"
                field_kwargs["alias"] = param_name
                alias_map[aliased_name] = param_name
                field_name = aliased_name

            fields[field_name] = (annotation, Field(**field_kwargs))
        TLParametersModel = create_model(name, **fields)
        classes_list.append(TLParametersModel)

    return classes_list


def _is_optional_type(t):
    """Check if a given type annotation is Optional[...]"""
    if t is Any:
        return True
    origin = get_origin(t)
    if origin is getattr(__import__('typing'), 'Union', None):
        args = get_args(t)
        return type(None) in args
    return False

# Example usage:
#import scanpy as sc
#generated_classes = generate_pydantic_classes(sc.tl)
#for func in generated_classes:  
#    print(func.schema())
