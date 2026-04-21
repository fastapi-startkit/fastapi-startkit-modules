class AppProvider:
    def register(self):
        from config.app import CONFIG

        self.merge_config_from(CONFIG, 'app')
