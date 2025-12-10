import pytest
import os
import yaml
from app.core.prompt_loader import PromptLoader

TEST_PROMPTS_FILE = "tests/test_prompts.yaml"

@pytest.fixture
def setup_prompts_file():
    """Create a temporary prompts file for testing."""
    prompts = {
        "test_key": "Hello {{ name }}!",
        "simple_key": "Just a string."
    }
    with open(TEST_PROMPTS_FILE, "w") as f:
        yaml.dump(prompts, f)
    
    # Reset PromptLoader state before test
    PromptLoader._prompts = {}
    
    yield TEST_PROMPTS_FILE
    
    # Cleanup
    if os.path.exists(TEST_PROMPTS_FILE):
        os.remove(TEST_PROMPTS_FILE)
    
    # Reset PromptLoader state after test
    PromptLoader._prompts = {}

def test_load_prompts(setup_prompts_file):
    """Test loading prompts from a file."""
    PromptLoader.load_prompts(setup_prompts_file)
    assert PromptLoader._prompts["test_key"] == "Hello {{ name }}!"

def test_get_prompt_rendering(setup_prompts_file):
    """Test rendering a prompt with variables."""
    PromptLoader.load_prompts(setup_prompts_file)
    result = PromptLoader.get_prompt("test_key", name="World")
    assert result == "Hello World!"

def test_get_prompt_missing_key(setup_prompts_file):
    """Test error when key is missing."""
    PromptLoader.load_prompts(setup_prompts_file)
    with pytest.raises(KeyError):
        PromptLoader.get_prompt("non_existent_key")

def test_load_prompts_file_not_found():
    """Test error when file does not exist."""
    with pytest.raises(FileNotFoundError):
        PromptLoader.load_prompts("non_existent_file.yaml")
