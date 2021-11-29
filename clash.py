import io
import re

import requests
from ruamel.yaml import YAML
#import yaml

urls = [
    "https://cdn.jsdelivr.net/gh/AzadNetCH/Clash@main/AzadNet.yml",
    "https://raw.githubusercontent.com/chfchf0306/clash/main/clash",
    "https://raw.githubusercontent.com/jw853355718/clash_233/master/speed.yaml",
    "https://raw.githubusercontent.com/jw853355718/clash_233/master/speed_ignore_ssl.yaml",
    "https://raw.githubusercontent.com/jw853355718/clash_233/master/speed_short.yaml",
    "https://raw.githubusercontent.com/gooooooooooooogle/Clash-Config/main/Clash.yaml",
    "https://raw.githubusercontent.com/vpei/Free-Node-Merge/main/out/clash.yaml",
    "https://raw.githubusercontent.com/oslook/clash-freenode/main/clash.yaml",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/clash.yml",
    "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
    "https://raw.githubusercontent.com/alanbobs999/TopFreeProxies/master/sub/sub_merge_yaml.yml",
    "https://raw.githubusercontent.com/clashconfig/online/main/wevpn.yml",
    "https://raw.githubusercontent.com/baby610/Clash/main/ClashSC",
    "https://raw.githubusercontent.com/mohsenhafezquran/ClashVPN/main/Clash",
]


def get_yaml_content(url):
    print(url)
    try:
        result = requests.get(url)
    except Exception as e:
        print(e)
        return ""

    if result.status_code != 200:
        return ""

    content = result.content.decode('utf-8')
    pattern = re.compile(r'(name|password): ([^,\{\}\n"]+)([,\}])')
    #print(re.findall(pattern, content))
    content = re.sub(pattern, r'\1: "\2"\3', content)
    #print(content)
    return content


def get_proxies(content):
    yaml = YAML(typ='safe')
    with io.BytesIO() as buf:
        buf.write(content.encode('utf-8'))
        buf.flush()
        data = yaml.load(buf.getvalue())

    return data["proxies"]


def get_all_proxies():
    all_proxies = []
    for url in urls:
        content = get_yaml_content(url)
        #print(content)
        if content == "":
            print("content is empty")
            continue
        proxies = get_proxies(content)
        all_proxies.extend(proxies)
    return all_proxies


def filter_proxies(all_proxies):
    ret_proxies = []
    proxies_server = set()
    for proxy in all_proxies:
        if "cipher" in proxy.keys() and proxy["cipher"] == "none":
            continue
        if proxy["server"] not in proxies_server:
            proxies_server.add(proxy["server"])
            ret_proxies.append(proxy)
    return ret_proxies


def rename_proxies(all_proxies):
    ret_proxies = []
    names = []
    count = 1
    for proxy in all_proxies:
        proxy["name"] = str(count).zfill(5)
        count = count + 1
        ret_proxies.append(proxy)
        names.append(proxy["name"])
    return ret_proxies, names


def write_yaml(all_proxies, names):
    yaml = YAML(typ='safe')
    with open("template.yaml", encoding='utf-8') as template:
        data = yaml.load(template)
    #print(data)
    data["proxies"] = all_proxies
    for index in range(len(data["proxy-groups"])):
        if data["proxy-groups"][index]["proxies"] is None:
            data["proxy-groups"][index]["proxies"] = names

    with open("output.yaml", mode="w", encoding='utf-8') as output:
        yaml.dump(data, output)


def main():
    all_proxies = get_all_proxies()
    #print(all_proxies)
    all_proxies = filter_proxies(all_proxies)
    all_proxies, names = rename_proxies(all_proxies)
    write_yaml(all_proxies, names)


if __name__ == '__main__':
    main()
