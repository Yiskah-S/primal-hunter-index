def detect_characters_in_scene(scene_text, alias_map):
	found = set()
	for canonical, data in alias_map.items():
		for alias in data["aliases"]:
			if re.search(rf"\b{re.escape(alias)}\b", scene_text, re.IGNORECASE):
				found.add(canonical)
	return list(found)
