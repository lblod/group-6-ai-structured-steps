class ModelConfig:
    def __init__(self, model: str, system_message: str, user_message: str, temperature: float, seed: int) -> None:
        self.model = model
        self.system_message = system_message
        self.user_message = user_message
        self.temperature = temperature
        self.seed = seed