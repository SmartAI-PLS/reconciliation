import difflib

def similar(a, b):
    return difflib.get_close_matches(a, b, 1, 0.70)

print(similar("iphone13 - 128 gb (red) ".replace(" ", "").replace("-",""), ['iphone13 128GB red color'.replace(" ", "").replace("-","")]))