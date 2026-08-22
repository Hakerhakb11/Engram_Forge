from engram_forge.get_user_config import get_name, get_prompt_for_chatting


def create_modelfile_for_gguf(GGUF_DIR):
    gguf_files = list(GGUF_DIR.glob("*.gguf"))
    if gguf_files:
        gguf_filename = gguf_files[0].name
        system_prompt = get_prompt_for_chatting().format(
            my_name=get_name(), contact_name="(имя неизвестно, спроси у собеседника если нужно)")

        modelfile_content = f"""# ==========================================
# HOW TO ADD THIS MODEL TO OLLAMA:
# 1. Open terminal in this folder (folder with Modelfile and .gguf file)
# 2. Run: ollama create <your_model_name> -f Modelfile
# 3. Run: ollama run <your_model_name>
# [!] It IS VERY IMPORTANT, TO SET --think=false BEFORE YOU ADD YOUR MODEL!
# ==========================================

FROM ./{gguf_filename}

PARAMETER temperature 0.5
PARAMETER top_p 0.8
PARAMETER top_k 40
PARAMETER repeat_penalty 1.14
PARAMETER num_predict 100

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
