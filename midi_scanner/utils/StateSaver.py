import yaml
import logging

class StateSaver:
    def __init__(self, config_file):
        self.config_file = config_file
        self.state = {}
        self.logger = logging.getLogger("StateSaver")

    def load_state(self):
        try:
            with open(self.config_file, 'r') as f:
                self.state = yaml.safe_load(f)
            self.logger.info("State loaded successfully.")
        except FileNotFoundError:
            self.logger.info("Config file not found. Starting with empty state.")
            self.state = {}

    def save_state(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.state, f)
        self.logger.info("State saved successfully.")

    def update_state(self, key, value):
        self.state[key] = value

    def get_state(self, key):
        return self.state.get(key)
