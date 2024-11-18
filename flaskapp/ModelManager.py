# model_manager.py
class ModelManager:
    _instance = None

    def __init__(self):
        self.model = None
        self.training_frame = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ModelManager()
        return cls._instance

    def set_model(self, model):
        self.model = model

    def get_model(self):
        return self.model

    def set_training_frame(self, training_frame):
        self.training_frame = training_frame

    def get_training_frame(self):
        return self.training_frame
