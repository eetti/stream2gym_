
import yaml
from yaml.loader import SafeLoader

def readYAMLConfig(configPath):
	data = []

	try:
		with open(configPath, 'r') as f:
			data = list(yaml.load_all(f, Loader=SafeLoader))
			print(data)
	except yaml.YAMLError:
		print("Error in configuration file")

	return data
