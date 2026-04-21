import logging
import os
import asyncio
import ray
from agentsociety import AgentSimulation
from agentsociety.configs import SimConfig
from mosstool.map.osm import RoadNet, Building
from mosstool.map.builder import Builder
from mosstool.type import Map as MossMap
from mosstool.util.format_converter import dict2pb

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tiny_test")

async def main():
    logger.info("Starting Minimal HBEE Pulse Check (Async)...")

    # Use an absolute path so the Go server never loses it
    map_path = os.path.abspath("mock_map.pb")
    
    logger.info("Fetching a dense map block via mosstool (Manhattan)...")
    min_lat, max_lat = 40.755, 40.759
    min_lon, max_lon = -73.988, -73.984
    projstr = f"+proj=tmerc +lat_0={(min_lat + max_lat) / 2} +lon_0={(min_lon + max_lon) / 2}"
    
    try:
        rn = RoadNet(max_latitude=max_lat, min_latitude=min_lat, max_longitude=max_lon, min_longitude=min_lon)
        roadnet = rn.create_road_net()
        
        bd = Building(proj_str=projstr, max_latitude=max_lat, min_latitude=min_lat, max_longitude=max_lon, min_longitude=min_lon)
        aois = bd.create_building()
        
        logger.info("Compiling binary map...")
        builder = Builder(net=roadnet, aois=aois, proj_str=projstr)
        m = builder.build("mock_map")
        pb = dict2pb(m, MossMap())
        
        with open(map_path, "wb") as f:
            f.write(pb.SerializeToString())
            
        logger.info(f"✅ Valid Protobuf mock map created at {map_path}")
    except Exception as e:
        logger.error(f"Failed to build map from OSM: {e}")
        return

    config = SimConfig()
    config.SetLLMRequest(
        request_type="openai", 
        api_key="EMPTY", 
        model="/home/ubuntu/glm4_flash_int4"
    )
    config.SetSimulatorRequest(
        task_name="hbee_tiny_test",
        max_day=1,
        start_step=28800,
        total_step=86400,
        log_dir="./logs_test",
        steps_per_simulation_step=1200,
        steps_per_simulation_day=86400,
        primary_node_ip="localhost"
    )
    config.SetMapRequest(file_path=map_path)
    config.SetMQTT(server="localhost", port=1883)

    tiny_roster = {
        "agent_1": {
            "name": "Dave", 
            "role": "Disgruntled IT", 
            "stress_baseline": 0.9, 
            "traits": ["paranoid"]
        },
        "agent_2": {
            "name": "Klaus", 
            "role": "Happy HR", 
            "stress_baseline": 0.1, 
            "traits": ["calm"]
        }
    }
    logger.info(f"Loaded {len(tiny_roster)} agents into memory.")

    try:
        simulation = AgentSimulation(
            config=config,
            agent_class_configs=tiny_roster,
            exp_name="tiny_pulse_check",
            logging_level=logging.INFO
        )
        logger.info("✅ Framework initialized safely. Waiting 10 seconds for the Go physics engine to boot...")
        
        # THE FIX: Give the Go server 10 seconds to open its gRPC port before stepping
        await asyncio.sleep(10)
        
        logger.info("🔥 Firing ONE tick...")
        await simulation.step()
        
        logger.info("✅ SUCCESS! Dave and Klaus ACTUALLY thought about their lives.")
    except Exception as e:
        logger.error(f"❌ Test failed. Error trace: {e}")
    finally:
        if os.path.exists(map_path):
            os.remove(map_path)
        if ray.is_initialized():
            ray.shutdown()

if __name__ == "__main__":
    asyncio.run(main())