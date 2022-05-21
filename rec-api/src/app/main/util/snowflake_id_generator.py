"""
Provide snowflake ID generator algorithm
"""
import time


class SnowflakeIDGenerator:
    """
    This class applied twitter snowflake ID generation algorithm to generate IDs
    Reference: https://github.com/cablehead/python-snowflake
    """

    def __init__(self, worker_id, data_center_id):
        """
        :param worker_id: int. The work ID. From 0 - 31
        :param data_center_id: int. The data identifier ID. From 0 - 31
        """
        # The start date of cutoff. Tue, 21 Mar 2006 20:50:14.000 GMT
        self.twepoch = 1142974214000

        # Number of digits occupied by machine id
        self.worker_id_bits = 5

        # Number of digits occupied by data identifier id
        self.data_center_id_bits = 5

        # Supported maximum machine id, the result is 31
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)

        # Supported maximum data identifier id, resulting in 31
        self.max_data_center_id = -1 ^ (-1 << self.data_center_id_bits)

        # Number of digits in id of sequence
        self.sequence_bits = 12

        # Machine ID moved 12 bits to the left
        self.worker_id_shift = self.sequence_bits

        # Data id moved 17 bits to the left (12 + 5)
        self.data_center_id_shift = self.sequence_bits + self.worker_id_bits

        # Time truncation moves 22 bits to the left (5 + 5 + 12)
        self.timestamp_left_shift = (
            self.sequence_bits + self.worker_id_bits + self.data_center_id_bits
        )

        # The mask of the generated sequence is 4095 (0b111111111111111111111 = 0xfff = 4095)
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        # Time cut of last ID generation
        self.last_timestamp = -1

        # Sequence in millisecond
        self.sequence = 0

        # Work Machine ID (0-31)
        self.worker_id = worker_id

        # Data Center ID (0-31)
        self.data_center_id = data_center_id

        self._type_check()

    def snowflake_to_timestamp(self, _id):
        """
        :param _id: int. The snowflake ID
        :return: int. The seconds when this ID was generated
        """
        _id = _id >> 22  # strip the lower 22 bits
        _id += self.twepoch  # adjust for twitter epoch
        _id = _id / 1000  # convert from milliseconds to seconds
        return _id

    def snowflake_generator(self, sleep=lambda x: time.sleep(x / 1000.0)):
        """
        :param sleep: lambda function. function to wait
        :return:
        """

        while True:
            timestamp = round(time.time() * 1000)

            # If the current timestamp is less than last timestamp used to generate ID,
            # sleep and wait.(last_timestamp - timestamp)
            if self.last_timestamp > timestamp:
                sleep(self.last_timestamp - timestamp)
                continue

            # If it is generated at the same time, use the sequence in millisecond to
            # sleep
            if self.last_timestamp == timestamp:
                self.sequence = (self.sequence + 1) & self.sequence_mask
                if self.sequence == 0:
                    self.sequence = -1 & self.sequence_mask
                    sleep(1)
                    continue
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            yield (
                ((timestamp - self.twepoch) << self.timestamp_left_shift)
                | (self.data_center_id << self.data_center_id_shift)
                | (self.worker_id << self.worker_id_shift)
                | self.sequence
            )

    def _type_check(self):
        """
        Check class's variables type
        """
        assert 0 <= self.worker_id <= self.max_worker_id
        assert 0 <= self.data_center_id <= self.max_data_center_id
