# actions/skills/search_file.py
from actions.base.skill import Skill
from actions.system.file_ops import search_file


class SearchFileSkill(Skill):
    def run(self, entities, system_state):
        query = entities.get("filename")
        if not query:
            return {"error": "missing_filename"}

        results = search_file(query, root=".")
        return {"results": results}
