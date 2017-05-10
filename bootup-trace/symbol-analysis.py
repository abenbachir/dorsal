import hashlib


# filepath = "./logs/available_functions.txt"
filepath = "./logs/symbols.txt"

shortnames = list()
functions = dict()
max_length = 0
count = 0
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
            function_name = function_name.rstrip()
            functions[function_name] = ip
            # function_name = line.strip()
            # if function_name in functions:
            #     continue
            max_length = len(function_name) if len(function_name) > max_length else max_length

            shortname = function_name
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
            # print("%s => %s [size=%d]" % (function_name, function_name[:16], len(function_name)))
        except Exception as ex:
            print(ex)


print("max function length = %d" % max_length)
print("all functions = %d" % count)
print("unique functions = %d" % len(functions))
unique_names = set(shortnames)
for name, ip in functions.items():
    count = shortnames.count(name)
    if count > 1:
        print("[%s] %s %d" % (ip, name, count))
print("%d vs %s = %d" % (len(unique_names), len(shortnames), len(shortnames)-len(unique_names)))