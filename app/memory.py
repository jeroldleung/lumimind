from typing import Dict, List


class Memory:
    def __init__(self):
        with open("assets/chat_prompt.txt") as f:
            sys_prompt = f.read()
        self.mem = [{"role": "system", "content": sys_prompt}]

    def add_user_msg(self, content: str):
        self.mem.append({"role": "user", "content": content})

    def add_assistant_msg(self, content: str):
        self.mem.append({"role": "user", "content": content})

    def get(self) -> List[Dict]:
        return self.mem
