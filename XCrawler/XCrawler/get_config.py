import yaml

def postgreconfig():
    with open('XCrawler/config.yaml', 'r') as f:
        data = yaml.safe_load(f)
    return data['postgreconfig']

def mogodbconfig():
    with open('XCrawler/config.yaml', 'r') as f:
        data = yaml.safe_load(f)
    return data['mogodbconfig']

def redisconfig():
    with open('XCrawler/config.yaml', 'r') as f:
        data = yaml.safe_load(f)
    return data['redisconfig']