import hashlib


filepath = "./logs/symbols.sym"

shortnames = list()
functions = dict()
with open(filepath) as f:
    lines = f.readlines()
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
            # shortname = int(hashlib.sha256(function_name.encode('utf-8')).hexdigest(), 16) % 2**64
            shortname = function_name[:32]

            # if len(function_name) < 8:
            #     shortname = function_name
            # elif len(function_name) > 8 and len(function_name) < 16:
            #     shortname = function_name[:8]+function_name[-(len(function_name)-8):]
            # else:
            #     shortname = function_name[:8] + '...' + function_name[-8:]

            # if shortname in shortnames and function_name != shortname:
            #     print("clash : %s - %s" % (function_name, shortname))

            shortnames.append(shortname)
            # print("%s => %s [size=%d]" % (function_name, function_name[:16], len(function_name)))
        except Exception as ex:
            print(ex)


unique_names = set(shortnames)

print("%d vs %s = %d" % (len(unique_names), len(shortnames), len(shortnames)-len(unique_names)))