import os
import yaml
from typing import Dict, Any
from jinja2 import Template

class PromptLoader:
    _prompts: Dict[str, str] = {}

    @classmethod
    def load_prompts(cls, file_path: str = "app/prompts/prompts.yaml"):
        """Load prompts from a YAML file."""
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Prompts file not found at {abs_path}")
            
        with open(abs_path, "r") as f:
            cls._prompts = yaml.safe_load(f)

    @classmethod
    def get_prompt(cls, key: str, **kwargs: Any) -> str:
        """Get a prompt by key and render it with provided variables."""
        if not cls._prompts:
            cls.load_prompts()
            
        if key not in cls._prompts:
            raise KeyError(f"Prompt key '{key}' not found.")
            
        template = Template(cls._prompts[key])
        return template.render(**kwargs)
