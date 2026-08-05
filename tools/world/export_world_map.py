import os, json

def generate_mermaid_markdown(graph_data, output_path):
    print("--- ÉTAPE 6 : EXPORT VISUEL (MERMAID GRAPH) ---")
    
    md = "# PMD Explorers of Sky World Graph\n\n"
    md += "> Représentation visuelle des connexions logiques canoniques de la NDS.\n\n"
    md += "```mermaid\n"
    md += "graph TD;\n"
    
    # Pour ne pas surcharger le diagramme, on n'affiche que les noeuds connectés
    active_nodes = set()
    for edge in graph_data['edges']:
        active_nodes.add(edge['source'])
        active_nodes.add(edge['target'])
        
    for node in graph_data['nodes']:
        if node['id'] in active_nodes:
            # Styling based on type
            shape_start, shape_end = "[", "]"
            if node['type'] == 'town': shape_start, shape_end = "((", "))"
            elif node['type'] == 'dungeon_entrance': shape_start, shape_end = "[(", ")]"
            
            md += f"    {node['id']}{shape_start}\"{node['label']} ({node['type']})\"{shape_end};\n"
            
    md += "\n"
    for edge in graph_data['edges']:
        md += f"    {edge['source']} -->|\"{edge['label']}\"| {edge['target']};\n"
        
    md += "```\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"✅ Graphe Markdown Mermaid généré : {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    with open(os.path.join(base_dir, 'database', 'world_graph.json'), 'r') as f:
        graph = json.load(f)
        
    out_dir = os.path.join(base_dir, 'output', 'World')
    os.makedirs(out_dir, exist_ok=True)
    generate_mermaid_markdown(graph, os.path.join(out_dir, 'WORLD_MAP_VISUAL.md'))
