import hashlib


def string_hash(name, arch=32):
    index = 0
    p = name[index]
    x = ord(p) << 7
    length = len(name) - 1
    while length >= 0:
        p = name[index]
        x = ((1000003 * x) ^ ord(p)) % 2 ** arch
        index += 1
        length -= 1

    x = (x ^ len(name)) % 2 ** arch
    if x == -1:
        x = -2
    return x

# filepath = "./logs/available_functions.txt"
filepath = "./logs/kallsyms.map"

shortnames = list()
functions = dict()
length_frequencies = dict()
max_length = 0
count = 0

print("hsiFlareAcc_init   [hsiFlare]=%s\n hsiFlareAcc_init [hsiFlare]=%s\n hsiFlareAcc_init=%s\n" % (string_hash("hsiFlareAcc_init   [hsiFlare]"),
            string_hash("hsiFlareAcc_init [hsiFlare]"),
            string_hash("hsiFlareAcc_init"),
            ))
with open(filepath) as f:
    lines = f.readlines()
    count = len(lines)
    for line in lines:
        try:
            values = line.strip().split(' ')
            if not values[0]:
                continue
            ip = values[0]
            ip = int(ip, 16)
            function_name = values[1] if len(values) <= 2 else values[2]
            function_name = function_name.rstrip().replace('\t', ' ')
            # function_name = line.strip()
            # if function_name in functions:
            #     continue
            max_length = len(function_name) if len(function_name) > max_length else max_length

            shortname = string_hash(function_name)
            # size = 40
            # shortname = function_name[:size]
            # if len(function_name) > size:
            #     shortname = function_name[-size:]

            # if len(function_name) < 16:
            #     shortname = function_name
            # elif len(function_name) > 16 and len(function_name) < 32:
            #     shortname = function_name[:16]+function_name[-(len(function_name)-16):]
            # else:
            #     shortname = function_name[:16] + '...' + function_name[-16:]

            # if shortname in shortnames and function_name != shortname:
            #     print("clash : %s - %s" % (function_name, shortname))

            functions[function_name] = ip
            shortnames.append(shortname)
            length_frequencies[len(function_name)] = length_frequencies.get(len(function_name), 0) + 1
            # print("%s => %s [size=%d]" % (function_name, function_name[:16], len(function_name)))
        except Exception as ex:
            print(ex)

duplicate = count - len(functions)

print("Max function length : %d" % max_length)
print("All functions : %d" % count)
print("Unique functions : %d" % len(functions))
print("Duplicate : %d" % duplicate)
unique_names = set(shortnames)

# for name, ip in functions.items():
#     count = shortnames.count(name)
#     if count > 1:
#         print("[%s] %s %d" % (ip, name, count))

print("Clash functions : %d" % (len(shortnames) - len(unique_names) - duplicate))
