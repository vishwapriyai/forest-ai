from pystac_client import Client
import planetary_computer
import rasterio
import os

OUTPUT_DIR = "data/raw/satellite/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

bbox = [76.5, 11.3, 76.9, 11.7]

# 🎯 Only few dates (POC friendly)
dates = [
    "2022-01-01/2022-02-01",
    "2022-06-01/2022-07-01",
    "2023-01-01/2023-02-01"
]

def fetch_data():
    catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

    for i, date in enumerate(dates):
        print(f"\n📅 Fetching data for: {date}")

        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=date,
            query={"eo:cloud_cover": {"lt": 20}},
            limit=3
        )

        items = list(search.items())

        if len(items) == 0:
            print("❌ No data found for this date")
            continue

        success = False

        for item in items:
            try:
                signed_item = planetary_computer.sign(item)

                red_url = signed_item.assets["B04"].href
                nir_url = signed_item.assets["B08"].href

                download_band(red_url, f"{i}_red.tif")
                download_band(nir_url, f"{i}_nir.tif")

                success = True
                break

            except Exception as e:
                print("⚠️ Skipping item:", e)

        if not success:
            print("❌ Failed to download for this date")

def download_band(url, filename):
    path = os.path.join(OUTPUT_DIR, filename)

    with rasterio.open(url) as src:
        try:
            window = rasterio.windows.from_bounds(
                76.5, 11.3, 76.9, 11.7,
                transform=src.transform
            )

            data = src.read(1, window=window)

            # ⚠️ If empty → fallback
            if data.size == 0:
                print("⚠️ Empty crop, using full image instead...")
                data = src.read(1)
                transform = src.transform
            else:
                transform = rasterio.windows.transform(window, src.transform)

        except Exception as e:
            print("⚠️ Window failed, using full image:", e)
            data = src.read(1)
            transform = src.transform

        profile = src.profile
        profile.update({
            "height": data.shape[0],
            "width": data.shape[1],
            "transform": transform,
            "dtype": rasterio.float32
        })

        with rasterio.open(path, "w", **profile) as dst:
            dst.write(data, 1)

    print(f"✅ Saved: {filename}")

if __name__ == "__main__":
    fetch_data()