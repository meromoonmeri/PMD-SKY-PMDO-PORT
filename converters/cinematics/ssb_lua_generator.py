import os, json

def generate_lua_from_ast(ast, mappings_db):
    """
    Traduit l'AST du SSB en script Lua RogueEssence.
    """
    scene_name = ast['scene_name']
    lua = f"--- PMD Sky to PMDO Automatic Translation\n"
    lua += f"--- Source Scene: {scene_name}\n\n"
    lua += f"local {scene_name} = {{}}\n\n"
    lua += f"function {scene_name}.Cutscene()\n"
    lua += "  GAME:CutsceneMode(true)\n\n"
    
    text_counter = 1
    
    for instruction in ast['instructions']:
        cmd = instruction['command']
        args = instruction.get('args', {})
        
        if cmd in mappings_db['mappings']:
            template = mappings_db['mappings'][cmd]['lua']
            
            # Special case for Dialogues (we strip original text for New Era)
            if cmd == "Message":
                args['new_era_key'] = f"SCENE_{scene_name.upper()}_DLG_{text_counter:03d}"
                text_counter += 1
            
            # Format the lua template with the arguments
            try:
                lua_line = template.format(**args)
                lua += f"  {lua_line}\n"
            except KeyError as e:
                lua += f"  -- [ERROR] Missing argument {e} for command {cmd}\n"
        else:
            lua += f"  -- [UNMAPPED] {cmd} {args}\n"
            
    lua += "\n  GAME:CutsceneMode(false)\n"
    lua += "end\n\n"
    lua += f"return {scene_name}\n"
    return lua

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'compatibility', 'ssb_to_pmdo.json')
    ast_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'intermediate', 'cinematics_ssb')
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'Scripts', 'scene')
    os.makedirs(out_dir, exist_ok=True)
    
    with open(db_path, 'r', encoding='utf-8') as f:
        mappings = json.load(f)
        
    print("--- 4. GÉNÉRATEUR LUA (SKY SSB -> PMDO) ---")
    for f in os.listdir(ast_dir):
        if not f.endswith('.json'): continue
        with open(os.path.join(ast_dir, f), 'r') as ast_f:
            ast = json.load(ast_f)
            
        lua = generate_lua_from_ast(ast, mappings)
        out_file = os.path.join(out_dir, f"{ast['scene_name']}.lua")
        with open(out_file, 'w', encoding='utf-8') as out_f:
            out_f.write(lua)
        print(f"✅ LUA Généré: {out_file}")
