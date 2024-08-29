import os
import re
from openai import OpenAI
from pathlib import Path
import yaml
import json
import argparse
import pyperclip  # To copy to clipboard
import subprocess  # For downloading and running the Ollama model
import shutil  # To check if commands are available

# Constants
CONFIG_FILE = 'config.yaml'
DEFAULT_CONFIG = {
    'code_extensions': [
        '.py', '.js', '.java', '.cpp', '.cs', '.html', '.css',
        '.json', '.yaml', '.yml', '.xml', '.md', '.txt', '.go',
        '.rb', '.php', '.ts', '.tsx', '.vue', '.rs', '.swift',
        '.kt', '.sh', '.bat', '.pl', '.pm', '.r', '.sql',
        '.ini', '.toml'
    ],
    'output_dir': 'output_directory',
    'input_directory': 'path_to_input_directory',
    'model': 'gpt-4o-mini-2024-07-18',
    'max_tokens': 100000,
    'temperature': 0.7,
    'api_key_path': '.secret',
    'clipboard_mode': False,
    'local_llm': True,
    'results_file': 'results.txt',
    'ollama_model': 'mistral'  # Placeholder for the actual best model name
}


# Load configuration from a YAML file, create a default one if not present
def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as config_file:
            yaml.dump(DEFAULT_CONFIG, config_file)
        print(f"Configuration file created with default settings: {CONFIG_FILE}")

    with open(CONFIG_FILE, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config


# Load API key from a .secret file
def load_api_key(api_key_path):
    with open(api_key_path, 'r') as secret_file:
        secrets = json.load(secret_file)
        return secrets['openai_api_key']


# Function to parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Script to enhance code using OpenAI or local LLM.')
    parser.add_argument('--code_extensions', nargs='+', help='File extensions for code files to analyze')
    parser.add_argument('--output_dir', help='Output directory for enhanced files')
    parser.add_argument('--input_directory', help='Input directory containing code files')
    parser.add_argument('--model', help='OpenAI model to use')
    parser.add_argument('--max_tokens', type=int, help='Maximum number of tokens to use in the OpenAI request')
    parser.add_argument('--temperature', type=float, help='Temperature for text generation')
    parser.add_argument('--api_key_path', help='Path to the file containing the OpenAI API key')
    parser.add_argument('--clipboard_mode', action='store_true',
                        help='Enable no-money mode, copies content to clipboard')
    parser.add_argument('--local_llm', action='store_true', help='Use local LLM (Ollama model) for code enhancement')
    parser.add_argument('--results_file', help='File to save results for later use')
    parser.add_argument('--ollama_model', help='Specify the Ollama model to use for local LLM')
    return parser.parse_args()


# Merge file configuration with CLI arguments
def merge_config_and_args(config, args):
    if args.code_extensions:
        config['code_extensions'] = args.code_extensions
    if args.output_dir:
        config['output_dir'] = args.output_dir
    if args.input_directory:
        config['input_directory'] = args.input_directory
    if args.model:
        config['model'] = args.model
    if args.max_tokens is not None:
        config['max_tokens'] = args.max_tokens
    if args.temperature is not None:
        config['temperature'] = args.temperature
    if args.api_key_path:
        config['api_key_path'] = args.api_key_path
    if args.clipboard_mode:
        config['clipboard_mode'] = args.clipboard_mode
    if args.local_llm:
        config['local_llm'] = args.local_llm
    if args.results_file:
        config['results_file'] = args.results_file
    if args.ollama_model:
        config['ollama_model'] = args.ollama_model
    return config


def is_code_file(filename, code_extensions):
    return any(filename.endswith(ext) for ext in code_extensions)


def read_and_concatenate_code_files(directory, code_extensions):
    all_code_content = ""
    for root, _, files in os.walk(directory):
        for file in files:
            if is_code_file(file, code_extensions):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    all_code_content += f"\n# {file}\n" + file_content
    return all_code_content


def clean_code_content(content):
    # Remove multiple spaces and newlines
    content = re.sub(r'\s+', ' ', content)
    return content


def generate_prompt(cleaned_code_content):
    prompt = (
        "You are an expert software engineer and architect. Your task is to review and refactor the entire project code "
        "provided below to achieve the highest standards of code quality, maintainability, scalability, and performance. "
        "Please follow these guidelines:\n"
        "1. Use modern design patterns (such as MVC, microservices, or clean architecture) suitable for this project.\n"
        "2. Ensure the code is modular, well-structured, and adheres to best practices for each programming language used.\n"
        "3. Provide clear separation of concerns, with appropriate use of classes, methods, and modules.\n"
        "4. Include error handling, input validation, and security best practices (e.g., sanitizing inputs, using prepared statements).\n"
        "5. Make sure the code is optimized for performance, removing any redundant or inefficient operations.\n"
        "6. Ensure compatibility with the latest versions of the frameworks or libraries used.\n"
        "7. Include comprehensive comments and documentation for each class, method, and module to ensure readability and maintainability.\n"
        "8. Output only code blocks using the format #@{filename} at the top of each block to indicate the file name.\n"
        "9. Provide test cases or suggest how the code can be tested to ensure robustness and reliability.\n"
        "10. Use clear, descriptive names for all variables, functions, and classes.\n"
        "\nReview the code and provide your output below, using only code blocks with no explanations:\n\n"
        f"{cleaned_code_content}"
    )
    return prompt


def ask_openai_to_improve_code(client, prompt, model, max_tokens, temperature):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content


def use_local_llm(prompt, model):
    # This function assumes Ollama command-line tool is available
    try:
        # Check if Ollama is installed
        if shutil.which("ollama") is None:
            raise EnvironmentError("Ollama command-line tool is not installed. Please install it to proceed.")

        # Download the model if not cached
        subprocess.run(["ollama", "download", model], check=True)

        # Run the model with the provided prompt
        result = subprocess.run(["ollama", "run", model, prompt], check=True, text=True, capture_output=True)
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error running the Ollama model: {e}")
        return ""
    except EnvironmentError as e:
        print(e)
        return ""


def save_results(result_content, output_directory):
    """
    Save the results in separate files and directories as suggested by ChatGPT or the local LLM.
    It parses the content for file and folder structure based on #@{filename} markers.
    """
    lines = result_content.splitlines()
    current_file = None
    current_content = []
    for line in lines:
        if line.startswith("#@"):
            if current_file:
                # Save the current file
                file_path = os.path.join(output_directory, current_file)
                Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(current_content))
            # Start a new file
            current_file = line[2:].strip()  # Extract filename after #@
            current_content = []
        else:
            current_content.append(line)

    # Save the last file
    if current_file:
        file_path = os.path.join(output_directory, current_file)
        Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(current_content))


def save_to_file(content, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Results saved to {file_path}")


def main():
    config = load_config()
    args = parse_args()
    config = merge_config_and_args(config, args)

    input_directory = config["input_directory"]
    code_extensions = config["code_extensions"]
    all_code_content = read_and_concatenate_code_files(input_directory, code_extensions)

    cleaned_code_content = clean_code_content(all_code_content)
    prompt = generate_prompt(cleaned_code_content)

    # Save the prompt to a results file only once
    save_to_file(prompt, config['results_file'])

    if config["clipboard_mode"]:
        # Copy the content and prompt to the clipboard
        clipboard_content = f"{prompt}\n\n{cleaned_code_content}"
        pyperclip.copy(clipboard_content)
        print("The prompt and code have been copied to the clipboard for later use.")
    elif config["local_llm"]:
        # Use the local LLM model
        print("Using local LLM model...")
        improved_content = use_local_llm(prompt, config["ollama_model"])
        save_to_file(improved_content, config['results_file'])
        save_results(improved_content, config["output_dir"])
    else:
        # Normal mode, call OpenAI API
        api_key = load_api_key(config['api_key_path'])
        client = OpenAI(api_key=api_key)

        output_directory = config["output_dir"]
        improved_content = ask_openai_to_improve_code(client, prompt, config["model"], config["max_tokens"],
                                                      config["temperature"])

        # Save the improved content to the results file
        save_to_file(improved_content, config['results_file'])

        # Save the improved content to separate files
        save_results(improved_content, output_directory)


if __name__ == "__main__":
    main()
