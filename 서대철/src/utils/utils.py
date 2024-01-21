import json

def load_config(file_path):
    """config.json 파일 로드"""
    with open(file_path, 'r') as config_file:
        return json.load(config_file)

