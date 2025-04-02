import json
import os


class LocalStorage:
    def __init__(self, base_path="data"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def save_json(self, data, filename):
        path = os.path.join(self.base_path, f"{filename}")
        # print(f"Save file -> {path}")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load_json(self, filename):
        path = os.path.join(self.base_path, f"{filename}")
        if not os.path.exists(path):
            print(f"ERROR: {path} is not Exists!!!!!!!!!!!")
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_novel_info(self, data):
        self.save_json(data, "info.json")

    def load_novel_info(self):
        return self.load_json("info.json")

    def save_chapter(self, data, index: str):
        self.save_json(data, f"Chapter-{index}.json")

    def load_chapter(self, index: str):
        return self.load_json(f"Chapter-{index}.json")
