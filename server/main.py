from config_loader import load_config

configs = load_config("../config/instruments.json")
for instrument_id, config in configs.items():
    print(config)