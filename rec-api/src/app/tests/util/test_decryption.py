import pytest
import operator

from app.main.util.decryption import PRIVATE_KEY_PATH, RsaUtil


class TestDecryption:
    rsaUtil = RsaUtil(PRIVATE_KEY_PATH)

    def test_decryption_without_enc(self):
        encrypted_message = "18e0599b8e4251fd23047c40e28c52ddfefdd74179315c79097d4c8d2c47e2ffe04043debead4f2a054b2a9d3f78cd6c8fcf24e1850f3993ae5645ade9045db4737afefb112f7940a2783f55fd290b00549e5ed898dbc72cf82ea84acfb75c68bac50743585e166035168089d025ade98d2ebaa4de221e9200561caafcee564b73bce6deda0dff428306b0aadbc0425bb9ddcc2d91d15078b8b7d9d0de7a3270fe9df7fc87721c0cbd33bb8958853c22fe90e77549b44190a1191360d20fb787733bcd7ec2a79bae71c280848b12b93da7ecb41ddcdfdcbec73370dc4d2fb7f65fb386eccaed053eb26d5abe53b4a229220e8fe477d209f3ccc9a284c594ac2d"
        decrypt_result = self.rsaUtil.decrypt_by_private_key(encrypted_message)
        assert operator.eq(decrypt_result, "Hello World")

    def test_decryption_with_enc(self):
        encrypted_message = "enc(18e0599b8e4251fd23047c40e28c52ddfefdd74179315c79097d4c8d2c47e2ffe04043debead4f2a054b2a9d3f78cd6c8fcf24e1850f3993ae5645ade9045db4737afefb112f7940a2783f55fd290b00549e5ed898dbc72cf82ea84acfb75c68bac50743585e166035168089d025ade98d2ebaa4de221e9200561caafcee564b73bce6deda0dff428306b0aadbc0425bb9ddcc2d91d15078b8b7d9d0de7a3270fe9df7fc87721c0cbd33bb8958853c22fe90e77549b44190a1191360d20fb787733bcd7ec2a79bae71c280848b12b93da7ecb41ddcdfdcbec73370dc4d2fb7f65fb386eccaed053eb26d5abe53b4a229220e8fe477d209f3ccc9a284c594ac2d)"
        decrypt_result = self.rsaUtil.decrypt_by_private_key(encrypted_message)
        assert operator.eq(decrypt_result, "Hello World")


if __name__ == "__main__":
    pytest.main()
