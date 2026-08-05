import os, json

def generate_lua_vfx_block(scene_id, vfx_db, mappings_db):
    print(f"--- ÉTAPE 4 : CONVERSION VERS PMDO ({scene_id}) ---")
    
    scene_data = vfx_db.get(scene_id)
    if not scene_data:
        return ""
        
    lua_code = ""
    for fx in scene_data['effects']:
        fx_type = fx['type']
        
        if fx_type == "ScreenFlash":
            color = fx.get('color', 'white')
            template = mappings_db['mappings']['ScreenFlash'].get(color, "GAME:FadeOut(true, {duration})")
            lua_code += f"  {template.format(duration=fx['duration'])}\n"
            
        elif fx_type == "CameraShake":
            template = mappings_db['mappings']['CameraShake']
            lua_code += f"  {template.format(power=fx['power'])}\n"
            
        elif fx_type == "ParticleSpawn":
            template = mappings_db['mappings']['ParticleSpawn']
            lua_code += f"  {template.format(effect_id=fx['effect_id'])}\n"
            
        elif fx_type == "ColorOverlay":
            template = mappings_db['mappings']['ColorOverlay']
            lua_code += f"  {template.format(duration=fx['duration'])}\n"
            
        elif fx_type == "Audio":
            if 'track' in fx:
                template = mappings_db['mappings']['Audio_Track']
                lua_code += f"  {template.format(track=fx['track'])}\n"
            elif 'sfx' in fx:
                template = mappings_db['mappings']['Audio_SFX']
                lua_code += f"  {template.format(sfx=fx['sfx'])}\n"
                
    return lua_code

def inject_into_cutscene(scene_id, vfx_lua):
    """
    Simule l'étape 5 (Lien avec les cinématiques Lua).
    Crée un script complet incluant Dialogues, Déplacements ET VFX.
    """
    lua = f"--- Framework Remake: {scene_id} (Full VFX Injection)\n"
    lua += f"local {scene_id} = {{}}\n\n"
    lua += f"function {scene_id}.Cutscene()\n"
    lua += "  GAME:CutsceneMode(true)\n\n"
    
    lua += "  -- Début Chorégraphie Spatiale (Exemple)\n"
    lua += "  GROUND:MoveToPosition(partner, 10, 15, false, 2)\n"
    lua += "  GROUND:EntTurn(partner, Direction.Left)\n\n"
    
    lua += "  -- Début Injection VFX Extraite\n"
    lua += vfx_lua
    lua += "  -- Fin Injection VFX\n\n"
    
    lua += "  -- Remplacement Narratif New Era\n"
    lua += f"  UI:WaitShowDialogue(STRINGS:FormatKey(\"SCENE_{scene_id.upper()}_001\"))\n\n"
    
    lua += "  GAME:CutsceneMode(false)\n"
    lua += "end\n\n"
    lua += f"return {scene_id}\n"
    
    return lua

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    with open(os.path.join(base_dir, 'database', 'cinematic_vfx.json'), 'r') as f:
        vfx_db = json.load(f)
        
    with open(os.path.join(base_dir, 'compatibility', 'vfx_to_pmdo.json'), 'r') as f:
        mappings_db = json.load(f)
        
    out_dir = os.path.join(base_dir, 'output', 'Scripts', 'scene')
    os.makedirs(out_dir, exist_ok=True)
    
    # Test avec le cas spécial "Dimensional Scream"
    scene_target = "dimensional_scream_01"
    vfx_lua = generate_lua_vfx_block(scene_target, vfx_db, mappings_db)
    final_lua = inject_into_cutscene(scene_target, vfx_lua)
    
    out_path = os.path.join(out_dir, f"{scene_target}.lua")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(final_lua)
        
    print(f"✅ Injection VFX réussie : {out_path}")
