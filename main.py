import json, os, sys

def load_compatibility_db():
    db_path = os.path.join(os.path.dirname(__file__), 'compatibility', 'systems.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_orchestrator():
    print("=========================================================")
    print(" FRAMEWORK REMAKE PMD SKY (NDS) -> PMDO (ROGUEESSENCE)")
    print("=========================================================")
    
    db = load_compatibility_db()
    
    print("\n--- ANALYSE DE LA POLITIQUE DE CONVERSION (NDS) ---")
    for sys_name, data in db['modules'].items():
        print(f"[{sys_name.upper()}] Action: {data['action']}")
        print(f"    -> Règle : {data['rule']}")
        
    print("\nLe pipeline d'extraction .SSB (Scripts) et Sir0 (Fonds) doit être implémenté.")
    print("RogueEssence reste le moteur maître. Fin de l'initialisation de l'architecture.")

if __name__ == "__main__":
    run_orchestrator()
