class ScObject():
    def __init__(self, main_sc, data: bytes, data_type: int):
        self.main_sc = main_sc
        self.data = data
        self.data_type = data_type

    def export(self) -> bytes:
        return self.data