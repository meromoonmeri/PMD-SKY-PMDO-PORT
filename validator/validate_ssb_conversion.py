import os, json

def validate_lua_conversion(lua_path, ast_path):
    report = {
        "status": "SUCCESS",
        "errors": [],
        "warnings": []
    }
    
    with open(lua_path, 'r', encoding='utf-8') as f:
        lua_content = f.read()
        
    with open(ast_path, 'r', encoding='utf-8') as f:
        ast = json.load(f)
        
    # Validation Rules
    if "-- [UNMAPPED]" in lua_content:
        report["status"] = "PARTIAL"
        report["warnings"].append("Certaines commandes SSB n'ont pas d'équivalent dans la table de conversion.")
        
    if "-- [ERROR]" in lua_content:
        report["status"] = "FAILED"
        report["errors"].append("Erreur de formatage lors de l'injection des paramètres.")
        
    if "UI:WaitShowDialogue" not in lua_content and any(i['command'] == "Message" for i in ast['instructions']):
         report["status"] = "FAILED"
         report["errors"].append("Les dialogues n'ont pas été remplacés par la fonction UI:WaitShowDialogue().")
         
    return report

if __name__ == "__main__":
    lua_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'Scripts', 'scene', 'm01a0103.lua')
    ast_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'intermediate', 'cinematics_ssb', 'm01a0103.json')
    
    report = validate_lua_conversion(lua_file, ast_file)
    print("--- 5. VALIDATEUR DE CONVERSION LUA ---")
    print(f"Status: {report['status']}")
    if report["errors"]: print(f"Errors: {report['errors']}")
    if report["warnings"]: print(f"Warnings: {report['warnings']}")
    
    out_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'conversion_report.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
