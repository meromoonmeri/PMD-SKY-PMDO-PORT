import os, json, re

def parse_connections(pmd_sky_path, grounds_db):
    print("--- ÉTAPE 2 : EXTRACTION DES CONNEXIONS ---")
    script_dir = os.path.join(pmd_sky_path, 'files', 'language-specific', 'US', 'SCRIPT')
    
    transitions = []
    
    for ground_id, data in grounds_db.items():
        folder_path = os.path.join(pmd_sky_path, data['script_folder'])
        if not os.path.exists(folder_path): continue
        
        for file in os.listdir(folder_path):
            # Parse .lsd (Level Script Data) or .ssb/.ssa if decompiled
            if file.endswith('.ssa') or file.endswith('.lsd') or file.endswith('.ssb'):
                # In a real deep parser, we decode the SSB or read the SSA.
                # For this framework extractor, we simulate the extraction of warp markers 
                # (since .ssa files in pret/pmd-sky often contain JumpCommon or CallCommon with Map IDs)
                file_path = os.path.join(folder_path, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Looking for patterns like JUMP_MAP(MAP_BEACH) or ExecuteStation
                        # NDS scripting uses specific opcodes for map transitions. We extract hints.
                        matches = re.findall(r'(d\d{2}p\d{2}[a-z]|t\d{2}p\d{2}[a-z])', content.lower())
                        for match in matches:
                            if match != ground_id and match in grounds_db:
                                trans = {
                                    "from": {"ground": ground_id, "position": "trigger"},
                                    "to": {"ground": match, "position": "spawn_0"},
                                    "condition": file,
                                    "type": "warp"
                                }
                                if trans not in transitions:
                                    transitions.append(trans)
                                    grounds_db[ground_id]["connections"].append(match)
                except Exception as e:
                    pass
                    
    # Deduplicate connections in grounds_db
    for g in grounds_db.values():
        g['connections'] = list(set(g['connections']))
        
    return transitions, grounds_db

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'grounds.json')
    with open(db_path, 'r') as f:
        grounds = json.load(f)
        
    transitions, updated_grounds = parse_connections('/tmp/pmd-sky', grounds)
    
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(updated_grounds, f, indent=2)
        
    trans_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'transitions.json')
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(transitions, f, indent=2)
        
    print(f"✅ Généré : {trans_path} ({len(transitions)} transitions extraites)")
