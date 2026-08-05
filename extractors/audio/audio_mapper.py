import os, json

def map_audio():
    # Sky uses internal track IDs. We map them to standard PMDO Track Names.
    # We do not convert the .smd/.swd, as PMDO handles ogg/wav natively. We just provide the mapping database.
    track_mapping = {
        "MUS_BEACH": "On the Beach at Dusk",
        "MUS_TREASURE_TOWN": "Treasure Town",
        "MUS_WIGGLYTUFF_GUILD": "Wigglytuff Guild",
        "MUS_TEMPORAL_TOWER": "Temporal Tower",
        "MUS_DIALGA_BATTLE": "Dialgas Fight to the Finish",
        "MUS_DONT_EVER_FORGET": "Dont Ever Forget"
    }
    return track_mapping

if __name__ == "__main__":
    print("--- MAPPING DE LA MUSIQUE (NDS -> PMDO BGM) ---")
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'Audio')
    mapping = map_audio()
    
    out_file = os.path.join(out_dir, "sky_audio_mapping.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
        
    print(f"✅ Mapping Audio généré : {len(mapping)} correspondances BGM.")
