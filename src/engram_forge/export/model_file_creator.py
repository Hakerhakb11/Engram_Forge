from pathlib import Path

from engram_forge.utils.get_json_config import load_config
from engram_forge.utils.get_user_config import get_name, get_prompt_for_chatting

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent

CONFIG_FILE: Path = PROJECT_DIR / "config/model_run_config.json"
DEFAULT_CONFIG = {
    "temperature": 0.5,
    "repeat_penalty": 1.14,
    "max_tokens": 400
}


def create_modelfile_for_gguf(GGUF_DIR):
    gguf_files = list(GGUF_DIR.glob("*.gguf"))
    if gguf_files:
        gguf_filename = gguf_files[0].name
        system_prompt = get_prompt_for_chatting().format(
            my_name=get_name(), contact_name="(имя неизвестно, спроси у собеседника если нужно)")

        config = load_config(CONFIG_FILE, DEFAULT_CONFIG)
        temperature: float = config.get("temperature")
        repeat_penalty: float = config.get("repeat_penalty")
        max_tokens: int = config.get("max_tokens")
        
        modelfile_content = f"""# ==========================================
# HOW TO ADD THIS MODEL TO OLLAMA:
# 1. Open terminal in this folder (folder with Modelfile and .gguf file)
# 2. Run: ollama create <your_model_name> -f Modelfile
# 3. Run: ollama run <your_model_name>
# [!] It IS VERY IMPORTANT, TO SET --think=false BEFORE YOU ADD YOUR MODEL!
# ==========================================

FROM ./{gguf_filename}

PARAMETER temperature {temperature}
PARAMETER repeat_penalty {repeat_penalty}
PARAMETER num_predict {max_tokens}
PARAMETER top_p 0.8
PARAMETER top_k 40

PARAMETER stop "<|im_end|>"
PARAMETER stop "<|im_start|>"

TEMPLATE \"\"\"{{{{ if .System }}}}<|im_start|>system
{{{{ .System }}}}<|im_end|>
{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
{{{{ end }}}}<|im_start|>assistant
<think>
</think>
\"\"\"

SYSTEM \"\"\"{system_prompt.strip()}\"\"\"
"""

        modelfile_path = GGUF_DIR / "Modelfile"
        modelfile_path.write_text(modelfile_content, encoding="utf-8")
        print(f"Modelfile save in model directory: {modelfile_path}")
