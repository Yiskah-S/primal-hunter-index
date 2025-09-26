# run command: ./setup_schemas.sh


#!/bin/bash
mkdir -p schemas

for file in \
	skills \
	classes \
	known_skills \
	character_timeline \
	titles \
	tiers \
	stat_scaling \
	chapters_to_posts \
	aliases \
	global_event_timeline; do
	touch schemas/${file}.schema.json
	echo "✅ Created schemas/${file}.schema.json"
done
