import time

from app.main import rec_db_conn


class store_names_client:
    """
    store_names_client loads 1000 results from database, use self.offset to keep track of reading buffer,
    if self.current_count is less than required count, search database again
    """

    def __init__(self):
        """
        self.current_count: int
            total found store names count
        self.offset: int
            offset when reading store_names
        self.limit_count: int
            search additional count of results every time in the database, default 1000
        self.store_names: list
            total store names found in database
        self.skip_count: int
            skip the first skip_count of results in the database
        self.time_out: int
            time_count seconds when searching in the database， default 2 seconds
        """
        self.current_count = 0
        self.offset = 0
        self.limit_count = 1000
        self.store_names = []
        self.skip_count = 0
        self.search_db_store_names(self.limit_count, self.current_count)
        self.time_out = 2

    def init(self):
        """
        init offset when reading self.store_names
        """
        self.offset = 0

    def add_store_names(self, count):
        """
        Get number of 2*count store_names from self.store_names, in case there are not sufficient store names
        after filtering, if current_count is less than count, then search db to get limit_count(1000) number of
        new results.
        """
        start_count = self.offset
        end_count = start_count + 2 * count

        start_time = time.time()
        while self.current_count < end_count:
            if time.time() - start_time > self.time_out:
                break
            additional_store_names = self.search_db_store_names(
                self.limit_count, self.skip_count
            )
            if not additional_store_names:
                break

        self.offset = end_count
        return self.store_names[start_count:end_count]

    def search_db_store_names(self, count, skip_count):
        """
        Connecting directly to MongoDB to fetch popular store name words,
        Extracting the popular store name words from the store_names document

        count: limit the results returned from db
        skip_count: skip the first skip_count of results from db
        """
        db_store_names = list(
            rec_db_conn.get_database_instance()["fgmStoreNames"]
            .find({}, {"_id": 0, "words": 1})
            .sort("counts", -1)
            .limit(count)
            .skip(skip_count)
        )
        # Extracting the popular store name words from the document
        store_words = [str.title(record["words"]) for record in db_store_names]
        self.current_count += len(store_words)
        self.store_names.extend(store_words)
        return store_words


store_names_client = store_names_client()
