from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.event import XidEvent
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
)
from pprint import pprint

MYSQL_SETTINGS = {"host": "pxc-web01", "port": 3306, "user": "root", "passwd": "root"}

def main():
    stream = BinLogStreamReader(
        connection_settings=MYSQL_SETTINGS,
        server_id=3,
        only_events=[XidEvent],
    )

    for binlogevent in stream:
        binlogevent.dump()
        # pprint(vars(binlogevent))
        # for row in binlogevent.rows:
        #     print(row)


if __name__ == "__main__":
    main()
