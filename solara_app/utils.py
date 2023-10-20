from typing import Callable
from solara.components.file_drop import FileInfo

def persist_uploaded_file(filename: str, key: str = "data") -> Callable[[FileInfo], None]:
    def func(data: FileInfo) -> None:
        with open(filename, "wb") as f:
            f.write(data[key])
    
    return func
