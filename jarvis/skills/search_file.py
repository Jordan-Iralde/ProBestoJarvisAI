# actions/skills/search_file.py
import os
import fnmatch


class SearchFileSkill:
    """Busca archivos en el sistema"""
    
    patterns = [
        r"\b(busca|buscar|search|encuentra|find)\b",
        r"\b(donde esta|dónde está|where is)\b"
    ]
    
    entity_hints = {
        "search_query": {"pattern": r"busca\s+(.+)"}
    }
    
    def run(self, entities, system_state):
        # Extraer parámetros
        filename = entities.get("file")
        if not filename:
            filename = entities.get("search_query", "*")
        if isinstance(filename, list):
            filename = filename[0] if len(filename) > 0 else entities.get("search_query", "*")
        
        search_path = entities.get("path", os.path.expanduser("~"))
        if isinstance(search_path, list):
            search_path = search_path[0] if len(search_path) > 0 else os.path.expanduser("~")
        max_results = 10
        
        print(f"🔍 Buscando: {filename}")
        print(f"📂 En: {search_path}")
        
        results = []
        try:
            for root, dirs, files in os.walk(search_path):
                # Limitar profundidad para no tardar mucho
                if root.count(os.sep) - search_path.count(os.sep) > 3:
                    continue
                
                for file in files:
                    if fnmatch.fnmatch(file.lower(), f"*{filename.lower()}*"):
                        results.append(os.path.join(root, file))
                        if len(results) >= max_results:
                            break
                
                if len(results) >= max_results:
                    break
            
            if results:
                print(f"✓ Encontrados {len(results)} archivos:")
                for r in results[:5]:
                    print(f"  📄 {r}")
                if len(results) > 5:
                    print(f"  ... y {len(results) - 5} más")
            else:
                print("❌ No se encontraron archivos")
            
            return {
                "success": True,
                "results": results,
                "count": len(results),
                "query": filename
            }
            
        except Exception as e:
            print(f"❌ Error buscando: {e}")
            return {"success": False, "error": str(e)}