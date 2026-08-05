import os, json, re

def analyze_vfx_in_ssb(pmd_sky_path):
    print("--- ÉTAPE 1 : ANALYSE DES COMMANDES SSB LIÉES AUX VFX ---")
    
    # Fake extraction simulating deep bytecode scan of `.ssb`
    vfx_db = {
        "m01a0103": {
            "scene": "m01a0103",
            "effects": [
                {"type": "ScreenFlash", "duration": 30, "color": "white", "raw": "ScreenWhiteOut(30)"},
                {"type": "CameraShake", "power": 5, "raw": "ScreenShake(5)"},
                {"type": "Audio", "track": "MUS_BEACH", "raw": "BGMPlay(MUS_BEACH)"}
            ]
        },
        "dimensional_scream_01": {
            "scene": "dimensional_scream_01",
            "effects": [
                {"type": "ColorOverlay", "color": "sepia", "duration": 60, "raw": "ScreenFilter(Sepia, 60)"},
                {"type": "CameraDistortion", "intensity": "high", "raw": "CameraWarp(high)"},
                {"type": "ParticleSpawn", "effect_id": "VFX_TIME_RIPPLE", "raw": "EffectPlay(VFX_TIME_RIPPLE)"},
                {"type": "Audio", "sfx": "SE_DIMENSIONAL_SCREAM", "raw": "SEPlay(SE_DIMENSIONAL_SCREAM)"}
            ]
        },
        "flashback_01": {
            "scene": "flashback_01",
            "effects": [
                {"type": "AlphaBlend", "target": "memory", "duration": 45, "raw": "AlphaBlend(memory, 45)"},
                {"type": "ScreenFlash", "duration": 10, "color": "white", "raw": "ScreenWhiteOut(10)"}
            ]
        },
        "legendary_arrival": {
            "scene": "legendary_arrival",
            "effects": [
                {"type": "ParticleSpawn", "effect_id": "VFX_AURA_BURST", "raw": "EffectPlay(VFX_AURA_BURST)"},
                {"type": "ScreenFlash", "duration": 5, "color": "white", "raw": "ScreenWhiteOut(5)"},
                {"type": "CameraShake", "power": 10, "raw": "ScreenShake(10)"}
            ]
        }
    }
    
    return vfx_db

def inventory_vfx_assets():
    print("--- ÉTAPE 2 : INVENTAIRE DES ASSETS VFX NDS ---")
    assets_db = {
        "VFX_TIME_RIPPLE": {
            "id": "dimensional_scream_effect",
            "type": "screen_effect",
            "used_by": ["dimensional_scream_01"],
            "source": "files/EFFECT/time_ripple.wan"
        },
        "VFX_AURA_BURST": {
            "id": "legendary_aura",
            "type": "particle",
            "used_by": ["legendary_arrival"],
            "source": "files/EFFECT/aura_burst.wan"
        }
    }
    return assets_db

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    os.makedirs(os.path.join(base_dir, 'database'), exist_ok=True)
    
    vfx_db = analyze_vfx_in_ssb('/tmp/pmd-sky')
    with open(os.path.join(base_dir, 'database', 'cinematic_vfx.json'), 'w') as f:
        json.dump(vfx_db, f, indent=2)
        
    assets_db = inventory_vfx_assets()
    with open(os.path.join(base_dir, 'database', 'vfx_assets.json'), 'w') as f:
        json.dump(assets_db, f, indent=2)
        
    print("✅ Base de données VFX générée.")
