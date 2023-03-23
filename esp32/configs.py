import json

class Configs():

  def __init__(self, config='config.json'):
    self.configFile = config
    with open(config) as conf:
      for k, v in json.load(conf).items():
        setattr(self, k, v)
  
  def update(self, newConfig):
    try:
      with open(self.configFile) as conf:
        data = json.load(conf)
        data.update(newConfig)
        for k, v in data.items():
          setattr(self, k, v)
      with open(self.configFile, "w") as conf:
        json.dump(data, conf)
    except Exception as ex:
      print("Config update error: ", ex)
      raise ex