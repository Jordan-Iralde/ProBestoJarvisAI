# actions/system/file_ops.py
import os
import uuid

NOTES_DIR = "storage/notes"
os.makedirs(NOTES_DIR, exist_ok=True)


def save_note(text):
    note_id = str(uuid.uuid4())
    path = os.path.join(NOTES_DIR, f"{note_id}.txt")
    with open(path, "w", encoding="utf8") as f:
        f.write(text)
    return path


def search_file(query, root=".", limit=20):
    """
    Búsqueda simple por nombre de archivo (substring match).
    root: carpeta a escanear
    limit: para evitar barrer todo el disco
    """
    query = query.lower()
    hits = []

    for base, dirs, files in os.walk(root):
        for name in files:
            if query in name.lower():
                hits.append(os.path.join(base, name))
                if len(hits) >= limit:
                    return hits

    return hits
