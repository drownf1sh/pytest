import os

import hvac
import Crypto
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_v1_5_cipher
from Crypto.PublicKey import RSA

from app.main.util.environment_variables import (
    VAULT_ADDR,
    VAULT_TOKEN,
    VAULT_ENGINE,
    APP_ENV,
)

if not APP_ENV:
    PRIVATE_KEY_PATH = os.getenv("MIKSECPUBLIC")
else:
    client = hvac.Client(
        url="https://" + VAULT_ADDR + ":8200", token=VAULT_TOKEN, verify=False
    )
    # Read secrets from vault
    read_secret_result = client.secrets.kv.v1.read_secret(
        path="general",
        mount_point=VAULT_ENGINE,
    )
    try:
        PRIVATE_KEY_PATH = read_secret_result["data"]["miksecpublic"]
    except KeyError:
        PRIVATE_KEY_PATH = ""


class RsaUtil(object):
    # initialize key
    def __init__(self, pri_key_file):
        pem_prefix = "-----BEGIN PRIVATE KEY-----\n"
        pem_suffix = "\n-----END PRIVATE KEY-----"
        if pri_key_file:
            pri_key_pem = "{}{}{}".format(
                pem_prefix, open(pri_key_file).read(), pem_suffix
            )
            self.private_key = RSA.importKey(pri_key_pem)

    def get_max_length(self, rsa_key, encrypt=True):
        """if the encrypted data is too long, we need to encrypt by segments
        :param rsa_key: key.
        :param encrypt: encrypted or not.
        """
        blocksize = Crypto.Util.number.size(rsa_key.n) / 8
        reserve_size = 11  # reserved size is 11
        if not encrypt:  # we do not need to reserve size if it is not encrypted
            reserve_size = 0
        maxlength = blocksize - reserve_size
        return int(maxlength)

    def decrypt_by_private_key(self, decrypt_message):
        """if the encrypted data is too long, we need to encrypt by segments
        :param rsa_key: key.
        :param encrypt: encrypted or not.
        """
        decrypt_result = b""
        max_length = self.get_max_length(self.private_key, False)
        decrypt_message = (
            decrypt_message[4:-1]
            if decrypt_message.startswith("enc(") and decrypt_message.endswith(")")
            else decrypt_message
        )
        decrypt_message = bytes.fromhex(decrypt_message)
        cipher = PKCS1_v1_5_cipher.new(self.private_key)
        while decrypt_message:
            input_data = decrypt_message[:max_length]
            decrypt_message = decrypt_message[max_length:]
            out_data = cipher.decrypt(input_data, "")
            decrypt_result += out_data
        return str(decrypt_result, encoding="utf-8")
