import os, json

def validate_full_zone(profile_name):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    profile_path = os.path.join(base_dir, 'profiles', f"{profile_name}.json")
    
    with open(profile_path, 'r', encoding='utf-8') as f:
        prof = json.load(f)
        
    print(f"================================")
    print(f"PMD SKY PORT VALIDATION")
    print(f"================================")
    print(f"Zone : {prof['name']}")
    
    # 1. Validation Ground
    rsground_path = os.path.join(base_dir, 'output', 'Grounds', f"{prof['output_base']}.rsground")
    g_status = "SUCCESS" if os.path.exists(rsground_path) else "FAILED (Missing .rsground)"
    
    # 2. Validation Tile
    tile_path = os.path.join(base_dir, 'output', 'Tiles', f"{prof['output_base']}_tileset.tile")
    t_status = "SUCCESS" if os.path.exists(tile_path) else "FAILED (Missing .tile)"
    
    # 3. Validation SSB
    lua_path = os.path.join(base_dir, 'output', 'Scripts', 'scene', f"{prof['cinematic'].replace('.ssb', '.lua')}")
    s_status = "SUCCESS" if os.path.exists(lua_path) else "FAILED (Missing .lua)"
    
    # 4. Validation des Liens (Cohérence Cohésive)
    l_status = "SUCCESS"
    if g_status == "SUCCESS":
        with open(rsground_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            # Check collisions
            if not data.get('Object', {}).get('obstacles'):
                l_status = "FAILED (Missing obstacles)"
            
            # Check spawns in walkable areas (simulation)
            spawners = data.get('Object', {}).get('Entities', [{}])[0].get('Spawners', [])
            if not spawners:
                l_status = "FAILED (Missing NPC spawns)"
                
    if s_status == "SUCCESS":
        with open(lua_path, 'r', encoding='utf-8') as f:
            lua = f.read()
            if "UI:WaitShowDialogue" not in lua:
                l_status = "FAILED (Lua text generation error)"
                
    print(f"GROUND : {g_status}")
    print(f"TILESET: {t_status}")
    print(f"SSB    : {s_status}")
    print(f"LINKS  : {l_status}")
    
    if all(s == "SUCCESS" for s in [g_status, t_status, s_status, l_status]):
        print(f"\nFINAL STATUS: READY FOR PMDO")
    else:
        print(f"\nFINAL STATUS: AUDIT FAILED")
    print(f"================================\n")

if __name__ == "__main__":
    validate_full_zone("beach_intro")
