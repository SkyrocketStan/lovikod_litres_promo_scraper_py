import datetime
import logging

from codes import Codes

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

current_date_in_iso = datetime.datetime.now().date().isoformat()
log.debug(current_date_in_iso)


def main():
    log.info("main() started")
    codes = Codes.get_fresh_raw_codes()
    log.info('Num of codes: %s', len(codes))
    # sql = DBSqlite("codes")
    # log.info("SQL Connected")
    # sql.disconnect()


if __name__ == '__main__':
    main()
