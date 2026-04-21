import os
import logging

try:
    import pycityproto.city.map.v2.map_pb2 as map_pb2
except ImportError:
    print("❌ ERROR: Cannot find pycityproto. Ensure you are in the hbee_env!")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vixero_production_forge")

def forge_production_map(base_map_path="mock_map.pb", output_path="vixero_office.pb"):
    if not os.path.exists(base_map_path):
        logger.error(f"Base map '{base_map_path}' not found!")
        return

    city_map = map_pb2.Map()
    
    # 1. Load the Verified Topology
    with open(base_map_path, "rb") as f:
        city_map.ParseFromString(f.read())
        
    logger.info(f"✅ Loaded base map topology: {len(city_map.aois)} buildings found.")

    if len(city_map.aois) < 5:
        logger.error("❌ The base map has fewer than 5 buildings. Cannot hijack enough rooms.")
        return

    # 2. The Vixero HQ Mapping
    vixero_rooms = [
        {"id": 500000000, "name": "The Bullpen (IT/Dev)"},
        {"id": 500000001, "name": "The Vault (Server Room)"},
        {"id": 500000002, "name": "The Breakroom"},
        {"id": 500000003, "name": "Boardroom (NVIDIA Prep)"},
        {"id": 500000004, "name": "CEO Office (Vix)"}
    ]

    # 3. Commandeer the First 5 Buildings
    # We leave their shapes, area, and X/Y gates untouched to guarantee routing safety.
    for i in range(5):
        old_id = city_map.aois[i].id
        city_map.aois[i].id = vixero_rooms[i]["id"]
        logger.info(f"🏗️ Commandeered Building {old_id} -> Rebranded as {vixero_rooms[i]['name']} (ID: {vixero_rooms[i]['id']})")

    # 4. Bulldoze the Rest of the City
    # This isolates the map strictly to the Vixero HQ.
    del city_map.aois[5:]
    logger.info("🧹 Bulldozed the rest of the city map. Environment isolated to Vixero HQ.")

    # 5. Export Production Map
    with open(output_path, "wb") as f:
        f.write(city_map.SerializeToString())
        
    logger.info(f"✅ Production Map perfectly forged: {output_path}")

if __name__ == "__main__":
    forge_production_map()