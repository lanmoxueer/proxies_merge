import io
import re
import json
import requests
from ruamel.yaml import YAML, ruamel

#import yaml

urls = [
    "https://cdn.jsdelivr.net/gh/AzadNetCH/Clash@main/AzadNet.yml",
    "https://raw.githubusercontent.com/chfchf0306/clash/main/clash",
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

proxies = {
    'http': '127.0.0.1:10908',
    'https': '127.0.0.1:10908'
}

proxies_server = set()

def test_use_proxies():
    try:
        result = requests.get("https://www.google.com", proxies=proxies)
        return True
    except Exception as e:
        return False


def get_yaml_content(url):
    print(url)
    try:
        should_use_proxies = test_use_proxies()
        if should_use_proxies:
            result = requests.get(url, proxies=proxies)
        else:
            result = requests.get(url)
    except Exception as e:
        print(e)
        return ""

    if result.status_code != 200:
        return ""

    content = result.content.decode('utf-8')
    pattern = re.compile(r'(name|password|ws-path|type|protocol-param|obfs-param|server|servername|cipher|protocol|obfs'
                         r'|network|Host|uuid): [ \'"]*([^,\{\}\n\'"]+)[ \'"]*([,\}\n])')
    #print(re.findall(pattern, content))
    content = re.sub(pattern, r'\1: "\2"\3', content)
    #print(content)
    pattern = re.compile(r'(tls|port|skip-cert-verify): [\'"]([^,\{\}\n"]+)[\'"]([,\}\n])')
    #print(re.findall(pattern, content))
    content = re.sub(pattern, r'\1: \2\3', content)

    pattern = re.compile(r'(http-opts|h2-opts): [\'"]+([,\}\n])')
    #print(re.findall(pattern, content))
    content = re.sub(pattern, r'\1: {}\2', content)
    return content


def get_proxies(content):
    yaml = YAML(typ='safe')
    try:
        with io.BytesIO() as buf:
            buf.write(content.encode('utf-8'))
            buf.flush()
            data = yaml.load(buf.getvalue())
    except Exception as e:
        print(e)
        return []

    return data["proxies"]


def get_all_proxies():
    all_proxies = []
    all_proxies_names = []
    for pos in range(len(urls)):
        content = get_yaml_content(urls[pos])
        #print(content)
        if content == "":
            print("content is empty")
            continue
        proxies = get_proxies(content)
        filtered_proxies = filter_proxies(proxies)
        renamed_proxies, names = rename_proxies(filtered_proxies, pos, len(all_proxies))

        all_proxies.extend(renamed_proxies)
        all_proxies_names.extend(names)
    #print(all_proxies)
    return all_proxies, all_proxies_names


def filter_proxies(proxies):
    ret_proxies = []
    for proxy in proxies:
        #not_support_cipher = ("none", "null", "rc4", "aes-256-gcm", "chacha20-ietf-poly1305")
        not_support_cipher = ("none", "null")
        if "cipher" in proxy.keys() and proxy["cipher"] in not_support_cipher:
            continue
        if "tls" in proxy.keys() and proxy["tls"] == "":
            continue
        if "port" in proxy.keys() and not isinstance(proxy["port"], int):
            continue
        not_support_type = ("none", "null", "ssr")
        if "type" not in proxy.keys() or proxy["type"] in not_support_type:
            continue
        if "server" not in proxy.keys():
            continue
            
        proxy_mark = proxy["server"] + ':' + str(proxy["port"])
        if proxy_mark not in proxies_server:
            proxies_server.add(proxy_mark)
            ret_proxies.append(proxy)
    return ret_proxies


def rename_proxies(proxies, url_pos, proxies_pos):
    ret_proxies = []
    names = []
    count = url_pos * 10000 + proxies_pos + 1
    for proxy in proxies:
        proxy["name"] = str(count).zfill(6)
        count = count + 1
        ret_proxies.append(proxy)
        names.append(proxy["name"])
    return ret_proxies, names


def write_yaml(all_proxies, names):
    #yaml = YAML(typ='safe')
    with open("template.yaml", encoding='utf-8') as template:
        #data = yaml.load(template)
        data = ruamel.yaml.round_trip_load(template)
    #print(data)
    data["proxies"] = all_proxies
    for index in range(len(data["proxy-groups"])):
        if data["proxy-groups"][index]["proxies"] is None:
            data["proxy-groups"][index]["proxies"] = names

    with open("output.yaml", mode="w", encoding='utf-8') as output:
        #yaml.preserve_quotes = True
        #yaml.dump(data, output)
        ruamel.yaml.round_trip_dump(data, output, default_style='"')
    #with open("output.json", mode="w", encoding='utf-8') as output2:
    #    json.dump(data, output2, ensure_ascii=False)


def main():
    all_proxies, all_proxies_names = get_all_proxies()
    #print(all_proxies)
    write_yaml(all_proxies, all_proxies_names)


if __name__ == '__main__':
    main()
