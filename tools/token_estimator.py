from pathlib import Path
import tiktoken

chapter_files = list(Path("chapters").glob("*.md"))
print(f"📄 Total chapter files: {len(chapter_files)}")

encoding = tiktoken.encoding_for_model("gpt-4")
total_tokens = sum(len(encoding.encode(Path(f).read_text())) for f in Path("chapters").glob("*.md"))
print(f"🔢 Approximate total tokens: {total_tokens}")
