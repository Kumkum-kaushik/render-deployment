import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from livekit import api

# Load environment variables
def load_environment() -> None:
    root_dir = Path(__file__).resolve().parent
    for env_path in (root_dir / "backend" / ".env.local", root_dir / ".env.local", root_dir / ".env"):
        if env_path.exists():
            load_dotenv(env_path, override=True)


load_environment()

async def main():
    # Initialize LiveKit API
    # Credentials (LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET) are auto-loaded from env files.
    lkapi = api.LiveKitAPI()
    sip = lkapi.sip
    
    trunk_id = os.getenv("OUTBOUND_TRUNK_ID")
    address = os.getenv("VOBIZ_SIP_DOMAIN", "").replace("sip:", "").strip()
    username = os.getenv("VOBIZ_AUTH_ID") or os.getenv("VOBIZ_USERNAME")
    password = os.getenv("VOBIZ_AUTH_TOKEN") or os.getenv("VOBIZ_PASSWORD")
    number = os.getenv("VOBIZ_CALLER_ID") or os.getenv("VOBIZ_OUTBOUND_NUMBER")
    
    if not trunk_id:
        print("Error: OUTBOUND_TRUNK_ID not found in .env/.env.local")
        return
    
    required = {
        "VOBIZ_SIP_DOMAIN": address,
        "VOBIZ_AUTH_ID/VOBIZ_USERNAME": username,
        "VOBIZ_AUTH_TOKEN/VOBIZ_PASSWORD": password,
        "VOBIZ_CALLER_ID/VOBIZ_OUTBOUND_NUMBER": number,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"Error: Missing required values: {', '.join(missing)}")
        print("Please update your env file and run setup_trunk.py again.")
        return

    print(f"Updating SIP Trunk: {trunk_id}")
    print(f"  Address: {address}")
    print(f"  Username: {username}")
    print(f"  Numbers: [{number}]")

    try:
        # Update the trunk with the correct credentials and settings
        await sip.update_outbound_trunk_fields(
            trunk_id,
            address=address,
            auth_username=username,
            auth_password=password,
            numbers=[number] if number else [],
        )
        print("\n✅ SIP Trunk updated successfully!")
        print("The 'max auth retry attempts' error should be resolved now.")
        
    except Exception as e:
        print(f"\n❌ Failed to update trunk: {e}")
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(main())
