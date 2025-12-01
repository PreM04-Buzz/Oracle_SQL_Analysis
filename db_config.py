import oracledb
import os

# Initialize Oracle Client (macOS path)

oracledb.init_oracle_client()

# Wallet directory path
WALLET_PATH = os.path.abspath("wallet")


# Oracle Credentials
DB_USER = "ramf25"
DB_PASSWORD = "GSUf25*1558563"

# From SQL Developer screen:
#   omnl2vbu9zzpc7aq_high
DB_SERVICE = "omnl2vbu9zzpc7aq_high"

def get_oracle_connection():
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_SERVICE,
            config_dir=WALLET_PATH,
            wallet_location=WALLET_PATH,
            wallet_password=None
        )
        return conn
    except Exception as e:
        print("\n[ERROR: could not connect to Oracle]")
        print("Details:", e)
        return None

