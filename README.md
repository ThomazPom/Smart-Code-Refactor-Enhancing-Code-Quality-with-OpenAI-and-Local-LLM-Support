# Code Enhancer with OpenAI and Local LLM Support

This script written by ChatGpt is designed to enhance the quality, maintainability, scalability, and performance of a codebase using either OpenAI's API or a local LLM (Ollama model). The script can automatically download, cache, and use a Ollama model if specified. It supports different modes of operation, including API-based, clipboard mode, and local LLM mode.

## Features

- **OpenAI API Support**: Enhance code using OpenAI's GPT models.
- **Local LLM Support**: Use local models from Ollama for code enhancement.
- **clipboard mode**: Copy the generated prompt and code to the clipboard for manual use.
- **Automatic Model Management**: Automatically download and cache the specified Ollama model.
- **Flexible Configuration**: Easily configurable through CLI arguments and a YAML configuration file.
- **Result Storage**: Save enhanced code to specified directories and files.

## Prerequisites

- Python 3.6+
- [Ollama Command-Line Tool](https://ollama.com/cli) (for local LLM mode)
- [Pyperclip](https://pyperclip.readthedocs.io/en/latest/) (for clipboard operations)

## Installation

1. **Install Python Dependencies**:
    ```bash
    pip install openai pyperclip pyyaml
    ```

2. **Install Ollama Command-Line Tool** (if using local LLM mode):
    Follow the installation instructions from the [Ollama website](https://ollama.com/cli).

3. **Create Configuration File** (optional):
    If a `config.yaml` file is not present, the script will create one with default settings.

## Usage

### 1. OpenAI API Mode

Use OpenAI's API to enhance the code:

```bash
python script.py --input_directory path/to/code --output_dir path/to/save --results_file results.txt --openai_model gpt-4o-mini-2024-07-18
```
###  2. clipboard mode

Copy the prompt and code to the clipboard for manual use:

```bash

python script.py --input_directory path/to/code --clipboard_mode --results_file results.txt
```
###  3. Local LLM Mode

Use a local Ollama model for code enhancement:

```bash
python script.py --input_directory path/to/code --local_llm --ollama_model mistral --results_file results.txt

```
## CLI Options

    --code_extensions: File extensions to consider as code files (e.g., .py .js .java).
    --output_dir: Directory to save enhanced files.
    --input_directory: Directory containing the code files to enhance.
    --openai_model: OpenAI model to use (e.g., gpt-4o-mini-2024-07-18).
    --ollama_model: Ollama model to use for local LLM (e.g., mistral).
    --max_tokens: Maximum number of tokens for the OpenAI request.
    --temperature: Temperature for text generation.
    --api_key_path: Path to the file containing the OpenAI API key.
    --clipboard_mode: Enable clipboard mode (copies content to clipboard).
    --local_llm: Use the local LLM (Ollama model) for code enhancement.
    --results_file: File to save results for later use.

##  Configuration

The script can be configured via a config.yaml file. A default configuration file will be created if it does not exist. Example configuration:

```yaml

code_extensions:
  - .py
  - .js
output_dir: output_directory
input_directory: path_to_input_directory
openai_model: gpt-4o-mini-2024-07-18
ollama_model: mistral
max_tokens: 100000
temperature: 0.7
api_key_path: .secret
clipboard_mode: False
local_llm: False
results_file: results.txt
```
##  API Key

The OpenAI API key should be stored in a .secret file in JSON format:

```json

{
  "openai_api_key": "your_openai_api_key_here"
}
```
## Local LLM Usage

To use the local LLM mode, ensure that the Ollama CLI is installed and accessible from your system's PATH. The script will automatically download and cache the specified Ollama model if it's not already cached.
Error Handling

    If the Ollama CLI is not installed or accessible, an error message will be displayed.
    If the specified model is not available or fails to run, the script will print an error message and exit.
