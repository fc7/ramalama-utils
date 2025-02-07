#!/usr/bin/env python3
"""
Script that detects all local Ollama models and makes them 
available to ramalama via symlinks.

This script will first detect all symlinks from a previous iteration
that point to the local Ollama models, and removes them before creating them anew. 
So it can be run safely everytime the Ollama models have been changed.

If executed with the parameter --reset, the script will remove all previous symlinks and then exit.

TODO
add parameters:
--help
--verbose

Author: François Charette (fc7)
"""
import os
from pathlib import Path
import json
import argparse

home = Path(os.environ['HOME'])
OLLAMA_MODELS_DIR = home / Path(".ollama/models") 
OLLAMA_MANIFESTS_DIR = OLLAMA_MODELS_DIR / Path("manifests/registry.ollama.ai")
OLLAMA_BLOBS_DIR = OLLAMA_MODELS_DIR / Path("blobs")
RAMALAMA_DIR = home / Path(".local/share/ramalama/models/ollama")

def get_filenames(folder):
    filenames = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            filename = os.path.join(root, file)
            filenames.append(filename)

    return filenames

def get_model_name(filename):
    parts = filename.split('/')

    return parts[-2] + ":" + parts[-1]

def get_model_blob(model_path):
    """
    Reads a JSON file and extracts the matching layer with mediaType 
    "application/vnd.ollama.image.model".
    
    Args:
        model_path (str): Path to the JSON file.
        
    Returns:
        dict or None: The first matching layer if found, otherwise None.
    """
    try:
        # Read and parse the JSON file
        with open(model_path, 'r') as f:
            data = json.load(f)
            
        layers = data.get('layers', [])
        
        # Iterate through layers to find the first one with matching mediaType
        for layer in layers:
            if layer.get('mediaType') == 'application/vnd.ollama.image.model':
                return layer.get('digest', '').replace('sha256:', 'sha256-')
                
        print("No matching layer found.")
            
    except FileNotFoundError:
        print(f"File not found at path: {model_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error in file: {e}")
        return None
        
    return None

def create_symlink(src, target):
    """
    Creates a symbolic link from src to target.

    Args:
        src (str): The path of the file or directory to which symlinking.
        target (str): The name under which the source will be linked.

    Returns:
        bool: True if the symlink was successfully created, False otherwise.

    Raises:
        FileNotFoundError: If the source does not exist.
        OSError: If the target cannot be created due to permission issues or other errors.
    """
    try:
        # Check if the source exists
        if not os.path.exists(src):
            raise FileNotFoundError(f"Source file '{src}' does not exist.")

        # Create the symbolic link
        os.symlink(src, target)

        return True

    except FileNotFoundError as e:
        raise 
    except OSError as e:
        raise

def reset_symlinks(directory, blobs_dir):
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            if os.path.islink(path):
                source = os.readlink(path)
                if source.startswith(str(blobs_dir)):
                    print(f"Delete symlink {path} to Ollama model {source}")
                    os.unlink(path)     

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reset: remove all symlinks to Ollama')
    parser.add_argument('--reset', action='store_true', help='Remove all symlinks to Ollama')
    args = parser.parse_args()
    reset_symlinks(RAMALAMA_DIR, OLLAMA_BLOBS_DIR)
    if not args.reset:
        files = get_filenames(OLLAMA_MANIFESTS_DIR)
        for file in files:
            # print(get_model_name(file))
            # print(get_model_blob(file))
            target = RAMALAMA_DIR / Path(get_model_name(file))
            src = OLLAMA_BLOBS_DIR / Path(get_model_blob(file))
            if create_symlink(src, target):
                print(f"Model {target} symlinked to existing blob {src}")
