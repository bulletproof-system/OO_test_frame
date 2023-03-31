import threading, os, random, subprocess
from config import settings

from core.utils import Singleton
from core import utils 


@Singleton
class Generator():
    def __init__(self) -> None:
        self.data_id = 0
        self.__data_id_lock = threading.Lock()
        self.generators = {}
        for path in settings.generators:
            (filePath, fullname) = os.path.split(path)
            (name, suffix) = os.path.splitext(fullname)
            if suffix == ".py":
                command = ["python", path]
            elif suffix == ".jar":
                command = [os.path.join(settings.java_home, "bin", "java"), "-jar", path]
            elif suffix == ".exe" or suffix == "":
                command = [path]
            else:
                utils.printc(f"unsupport generator: {path}, suffix : {suffix}", "yellow")
                continue
            self.generators[path] = command
        if self.generators == {}:
            utils.printc(f"没有可用的数据生成器", "red")
            
    def getId(self):
        with self.__data_id_lock:
            self.data_id += 1
            return self.data_id
    
    def generate(self, generators=None):
        id = self.getId()
        path = os.path.join("input", f"data-{id}"+".in")
        command = random.choice(list(self.generators.values()))
        with open(path, "w") as f:
            try:
                result = subprocess.run(command, stdout=f, timeout=10)
                if result.returncode != 0:
                    utils.printc("generator error")
            except subprocess.TimeoutExpired as e:
                utils.printc("generator TLE")
        return path