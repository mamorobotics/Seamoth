import bluetooth

nearby_devices = bluetooth.discover_devices(lookup_names=True)
nearby = {}
for i in nearby_devices:
    nearby.setdefault(i[1], []).append(i[0])

print(nearby)