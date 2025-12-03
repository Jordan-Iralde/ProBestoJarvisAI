# actions/skills/create_note.py
from actions.base.skill import Skill
from actions.system.file_ops import save_note

class CreateNoteSkill(Skill):
    def run(self, entities, system_state):
        text = entities.get("text")
        if not text:
            return {"error": "missing_text"}

        note_path = save_note(text)
        return {"status": "created", "path": note_path}
