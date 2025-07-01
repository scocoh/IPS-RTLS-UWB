# Name: check_image_size.py
# Version: 0.1.1
# Created: 971201
# Modified: 250630
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: ParcoRTLS backend script to analyze image sizes and coordinate conversion
# Location: /home/parcoadmin/parco_fastapi/app/tests
# Role: Backend
# Status: Active
# Dependent: TRUE

import asyncio
import asyncpg
from PIL import Image
import io

async def check_image_size():
    try:
        # Connect to database
        conn = await asyncpg.connect(
            "postgresql://parcoadmin:parcoMCSE04106!@192.168.210.226:5432/ParcoRTLSMaint"
        )
        
        print("=== IMAGE SIZE ANALYSIS ===")
        
        # Check source campus map (Map 43)
        result43 = await conn.fetch("SELECT img_data, min_x, min_y, max_x, max_y FROM maps WHERE i_map = 43")
        if result43:
            img_data = result43[0]["img_data"]
            image = Image.open(io.BytesIO(img_data))
            bounds = result43[0]
            print(f"Map 43 'LongBeach' (source campus):")
            print(f"  Image size: {image.size[0]} x {image.size[1]} pixels")
            print(f"  Coordinate bounds: ({bounds['min_x']}, {bounds['min_y']}) to ({bounds['max_x']}, {bounds['max_y']})")
            print(f"  Coordinate range: {bounds['max_x'] - bounds['min_x']} x {bounds['max_y'] - bounds['min_y']}")
            
        # Check reference building map (Map 44) 
        result44 = await conn.fetch("SELECT img_data, min_x, min_y, max_x, max_y FROM maps WHERE i_map = 44")
        if result44:
            img_data44 = result44[0]["img_data"]
            image44 = Image.open(io.BytesIO(img_data44))
            bounds44 = result44[0]
            print(f"\nMap 44 'Long Beach to scale' (reference building):")
            print(f"  Image size: {image44.size[0]} x {image44.size[1]} pixels")
            print(f"  Coordinate bounds: ({bounds44['min_x']}, {bounds44['min_y']}) to ({bounds44['max_x']}, {bounds44['max_y']})")
            print(f"  Coordinate range: {bounds44['max_x'] - bounds44['min_x']} x {bounds44['max_y'] - bounds44['min_y']}")
            
        # Check our new cropped map (Map 50)
        result50 = await conn.fetch("SELECT img_data, min_x, min_y, max_x, max_y FROM maps WHERE i_map = 50")
        if result50:
            img_data50 = result50[0]["img_data"]
            image50 = Image.open(io.BytesIO(img_data50))
            bounds50 = result50[0]
            print(f"\nMap 50 'Long Beach Bld Out BO10' (new cropped):")
            print(f"  Image size: {image50.size[0]} x {image50.size[1]} pixels")
            print(f"  Coordinate bounds: ({bounds50['min_x']}, {bounds50['min_y']}) to ({bounds50['max_x']}, {bounds50['max_y']})")
            print(f"  Coordinate range: {bounds50['max_x'] - bounds50['min_x']} x {bounds50['max_y'] - bounds50['min_y']}")
            
            # Calculate what the image size SHOULD be based on coordinate scaling
            if result43 and result44:
                # Source image dimensions
                source_width, source_height = image.size[0], image.size[1]
                source_coord_range_x = bounds['max_x'] - bounds['min_x']  # 282
                source_coord_range_y = bounds['max_y'] - bounds['min_y']  # 201
                
                # Cropped coordinate range
                crop_coord_range_x = bounds50['max_x'] - bounds50['min_x']  # Same as Map 44
                crop_coord_range_y = bounds50['max_y'] - bounds50['min_y']  # Same as Map 44
                
                # Expected pixel dimensions
                expected_width = int((crop_coord_range_x / source_coord_range_x) * source_width)
                expected_height = int((crop_coord_range_y / source_coord_range_y) * source_height)
                
                print(f"\n=== COORDINATE CONVERSION ANALYSIS ===")
                print(f"Source coordinate system: {source_coord_range_x} x {source_coord_range_y}")
                print(f"Source image pixels: {source_width} x {source_height}")
                print(f"Crop coordinate range: {crop_coord_range_x:.6f} x {crop_coord_range_y:.6f}")
                print(f"Expected crop pixels: {expected_width} x {expected_height}")
                print(f"Actual crop pixels: {image50.size[0]} x {image50.size[1]}")
                print(f"Size ratio: {image50.size[0]/expected_width:.3f} x {image50.size[1]/expected_height:.3f}")
                
                if abs(image50.size[0] - expected_width) > 100 or abs(image50.size[1] - expected_height) > 100:
                    print(f"❌ MISMATCH: Cropped image is wrong size!")
                    print(f"   Difference: {image50.size[0] - expected_width} x {image50.size[1] - expected_height} pixels")
                else:
                    print(f"✅ SUCCESS: Cropped image size matches expected dimensions")
                    
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

# Run the check
if __name__ == "__main__":
    asyncio.run(check_image_size())