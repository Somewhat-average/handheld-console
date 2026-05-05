import os
import math
import uuid
import json
import base64
import hashlib
from pathlib import Path


CHUNK_SIZE = 4096
RECEIVED_DIR = os.path.join(Path(__file__).parent, "data", "received_files")

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def make_transfer_id():
    return uuid.uuid4().hex[:12]


def build_file_start_packet(filepath, transfer_id=None, chunk_size=CHUNK_SIZE):
    if transfer_id is None:
        transfer_id = make_transfer_id()

    size = os.path.getsize(filepath)
    chunks = math.ceil(size / chunk_size)
    digest = sha256_file(filepath)

    return {
        "type": "file_start",
        "transfer_id": transfer_id,
        "name": os.path.basename(filepath),
        "size": size,
        "chunks": chunks,
        "sha256": digest,
    }


def iter_file_chunks(filepath, chunk_size=CHUNK_SIZE):
    with open(filepath, "rb") as f:
        index = 0
        while True:
            raw = f.read(chunk_size)
            if not raw:
                break

            yield {
                "type": "file_chunk",
                "index": index,
                "data": base64.b64encode(raw).decode("utf-8")
            }
            index += 1


def decode_chunk_data(data_b64):
    return base64.b64decode(data_b64.encode("utf-8"))


class IncomingFileTransfer:
    def __init__(self, transfer_id, name, size, chunks, sha256_hex):
        self.transfer_id = transfer_id
        self.name = name
        self.size = size
        self.chunks = chunks
        self.sha256 = sha256_hex
        self.parts = {}
        self.received_count = 0

    def add_chunk(self, index, raw_bytes):
        if index not in self.parts:
            self.parts[index] = raw_bytes
            self.received_count += 1

    def is_complete(self):
        return self.received_count == self.chunks

    def assemble_bytes(self):
        ordered = []
        for i in range(self.chunks):
            if i not in self.parts:
                raise ValueError(f"Missing chunk {i}")
            ordered.append(self.parts[i])
        return b"".join(ordered)

    def verify(self):
        raw = self.assemble_bytes()
        if len(raw) != self.size:
            return False, "size mismatch"

        digest = hashlib.sha256(raw).hexdigest()
        if digest != self.sha256:
            return False, "checksum mismatch"

        return True, raw

    def save(self, save_dir=RECEIVED_DIR):
        os.makedirs(save_dir, exist_ok=True)
        ok, result = self.verify()
        if not ok:
            return False, result

        filepath = os.path.join(save_dir, self.name)
        with open(filepath, "wb") as f:
            f.write(result)
        return True, filepath


def encode_packet(packet_dict):
    return (json.dumps(packet_dict) + "\n").encode("utf-8")


def try_parse_packet(line):
    return json.loads(line)