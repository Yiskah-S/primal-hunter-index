import os
import re
from pathlib import Path

INPUT_DIR = Path("chapters")
OUTPUT_DIR = Path("raw_scene_chunks")
OUTPUT_DIR.mkdir(exist_ok=True)

def chunk_scenes_from_markdown(file_path, chapter_number):
	with open(file_path, "r", encoding="utf-8") as f:
		lines = f.readlines()

	scene_chunks = []
	current_scene = []

	for line in lines:
		# Define a potential scene break
		if line.strip() in ["", "---", "===", "==="] and current_scene:
			scene_chunks.append(current_scene)
			current_scene = []
		else:
			current_scene.append(line)

	if current_scene:
		scene_chunks.append(current_scene)

	return scene_chunks

def save_scene(scene_lines, scene_id):
	out_path = OUTPUT_DIR / f"{scene_id}.md"
	with open(out_path, "w", encoding="utf-8") as f:
		f.writelines(scene_lines)
	print(f"✅ Saved scene: {scene_id}")

def process_all_chapters():
	files = sorted(INPUT_DIR.glob("*.md"))
	print(f"📂 Found {len(files)} files in '{INPUT_DIR}'")
	
	for fname in files:
		match = re.search(r"Chapter_(\d+)", fname.name)
		if not match:
			print("⚠️ No chapter number found in", fname.name)
			continue

		chapter_number = int(match.group(1))
		scene_chunks = chunk_scenes_from_markdown(fname, chapter_number)

		for idx, scene in enumerate(scene_chunks, 1):
			scene_id = f"{chapter_number}-{idx}"
			save_scene(scene, scene_id)

if __name__ == "__main__":
	process_all_chapters()
