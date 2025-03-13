# what does this actually need to do?
# 1 - get a days games --> how often does this update and how do we update the data in the database? new table?
# 2 - post a days games if needed --> how is this post specific tracked in the database? ^use a new table for this with a post id column
# 3 - post game headers
# 4 - post important plays
from datetime import datetime, timezone

def main(date: datetime):
    date = date.strftime("%Y%m%d")


if __name__ == "__main__":
    main(datetime.now(timezone.utc))
