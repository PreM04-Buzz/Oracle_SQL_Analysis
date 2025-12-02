import oracledb

oracledb.init_oracle_client(
    lib_dir="/Users/premswaroop/Downloads/instantclient_23_3"
)

WALLET_PATH = "/Users/premswaroop/Downloads/Wallet_ATP"

DB_USER = "ramf25"
DB_PASSWORD = "GSUF25*1558563"
DB_SERVICE = "omnl2vbu9zzpc7aq_high.adb.us-chicago-1.oraclecloud.com"

def get_oracle_connection():
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_SERVICE,
            wallet_location=WALLET_PATH
        )
        return conn
    except Exception as e:
        print("ERROR:", e)
        return None

