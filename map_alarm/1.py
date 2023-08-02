import json
from urllib.request import urlopen

# Set the desired year range
start_year = 2013
end_year = 2023

# Initialize an empty list to store the results
results = []

# Loop through the years
for year in range(start_year, end_year + 1):
    # Update the URL with the current year
    url = f'https://apis.data.go.kr/B552061/frequentzoneChild/getRestFrequentzoneChild?ServiceKey=%2BTHWNzZCVM8HYbGFp8GV2CPZjPEqQ%2BSqehbMQoQDEmuW7lR9JNUYwJtx3tolZ39qkQVZg0JgKrf3GAsaluhhEg%3D%3D&searchYearCd={year}&siDo=11&guGun=710&type=json&numOfRows=100&pageNo=1'

    # Make the request and read the response
    with urlopen(url) as response:
        data = json.loads(response.read().decode())

    # Extracting "spot_nm" and "geom_json" for each year
    if "items" in data and "item" in data["items"]:
        items = data["items"]["item"]
        for item in items:
            spot_nm = item.get("spot_nm")
            geom_json = item.get("geom_json")

            # Parsing the "geom_json" string as JSON
            geom_data = json.loads(geom_json)

            # Extracting the polygon coordinates
            if geom_data["type"] == "Polygon":
                polygon_coordinates = geom_data["coordinates"]
                results.append({
                    "year": year,
                    "spot_nm": spot_nm,
                    "polygon_coordinates": polygon_coordinates
                })

# Print the results
for result in results:
    print("Year:", result["year"])
    print("Spot Name:", result["spot_nm"])
    print("Polygon Coordinates:", result["polygon_coordinates"])
    print()
