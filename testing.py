from src.pycfi import decode, CFICode

code = decode("RWSNCA")

print(code.category)
print(code.group)
print(code.get_attribute("underlying_assets").value)