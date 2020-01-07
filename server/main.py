from collections import defaultdict
from emailManager import send_daily_updates
import db


if __name__ == '__main__':
    db.start()
    send_daily_updates()
    db.close(None)
