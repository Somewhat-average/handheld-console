import socket
import threading
import json
import os

from communication.message_store import add_message
from communication.file_transfer import (
    build_file_start_packet,
    iter_file_chunks,
    decode_chunk_data,
    IncomingFileTransfer,
    encode_packet,
    try_parse_packet,
)

class CommService:
    def __init__(self, manager, mode):
        self.manager = manager
        self.mode = mode  # "tcp" or "bluetooth"

        self.server_socket = None
        self.client_socket = None

        self.accept_thread = None
        self.recv_thread = None
        self.file_send_thread = None

        self.is_hosting = False
        self.is_connected = False
        self.connecting = False

        self.host_addr = None
        self.peer_addr = None
        self.status_msg = ""

        self.lock = threading.Lock()

        self.recv_buffer = ""
        self.pending_acks = {}
        self.pending_acks_lock = threading.Lock()

        self.incoming_transfers = {}
        self.outgoing_transfer = None
        self.incoming_transfer_status = None

        self.request_open_transfer_popup = False

    # helpers
    def get_local_nickname(self):
        return self.manager.tag_links['DevName'].text

    def create_server_socket(self, host, port_or_channel):
        if self.mode == "tcp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port_or_channel))
            return sock

        elif self.mode == "bluetooth":
            sock = socket.socket(
                socket.AF_BLUETOOTH,
                socket.SOCK_STREAM,
                socket.BTPROTO_RFCOMM
            )
            sock.bind((host, port_or_channel))
            return sock

        raise ValueError(f"Unsupported mode: {self.mode}")

    def create_client_socket(self):
        if self.mode == "tcp":
            return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        elif self.mode == "bluetooth":
            return socket.socket(
                socket.AF_BLUETOOTH,
                socket.SOCK_STREAM,
                socket.BTPROTO_RFCOMM
            )

        raise ValueError(f"Unsupported mode: {self.mode}")

    def _send_packet(self, packet):
        if not self.client_socket or not self.is_connected:
            raise OSError("Not connected")
        self.client_socket.sendall(encode_packet(packet))

    def _set_connected_socket(self, sock, addr=None):
        with self.lock:
            self.client_socket = sock
            self.peer_addr = addr
            self.is_connected = True
            self.connecting = False

    def _clear_connection(self):
        with self.lock:
            self.is_connected = False
            self.connecting = False
            self.peer_addr = None

            if self.client_socket:
                try:
                    self.client_socket.close()
                except OSError:
                    pass
                self.client_socket = None

        self.recv_buffer = ""
        self.incoming_transfers.clear()
        self.incoming_transfer_status = None
        self.outgoing_transfer = None

        with self.pending_acks_lock:
            self.pending_acks.clear()

    # host logic
    def start_host(self, host, port_or_channel):
        if self.is_hosting:
            self.status_msg = "Already hosting"
            return False

        try:
            self.server_socket = self.create_server_socket(host, port_or_channel)
            self.server_socket.listen()
            self.is_hosting = True
            self.host_addr = host
            self.status_msg = "Hosting..."

            self.accept_thread = threading.Thread(
                target=self._accept_loop,
                daemon=True
            )
            self.accept_thread.start()
            return True

        except OSError as e:
            self.status_msg = "Host failed"
            self.is_hosting = False
            return False

    def stop_host(self):
        self.is_hosting = False

        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass
            self.server_socket = None

        self._clear_connection()
        self.status_msg = "Host stopped"

    def _accept_loop(self):
        while self.is_hosting:
            try:
                client, addr = self.server_socket.accept()

                if self.is_connected:
                    try:
                        client.close()
                    except OSError:
                        pass
                    continue

                self._set_connected_socket(client, addr)
                self.status_msg = "Peer connected"

                self.recv_thread = threading.Thread(
                    target=self._receive_loop,
                    daemon=True
                )
                self.recv_thread.start()

            except OSError:
                break

    # connect logic
    def connect_to_peer(self, host, port_or_channel):
        if self.connecting or self.is_connected:
            self.status_msg = "Busy"
            return False

        self.connecting = True
        self.status_msg = "Connecting..."

        thread = threading.Thread(
            target=self._connect_worker,
            args=(host, port_or_channel),
            daemon=True
        )
        thread.start()
        return True

    def _connect_worker(self, host, port_or_channel):
        try:
            sock = self.create_client_socket()
            sock.settimeout(3)
            sock.connect((host, port_or_channel))
            sock.settimeout(None)

            self._set_connected_socket(sock, host)
            self.status_msg = "Connected"

            self.recv_thread = threading.Thread(
                target=self._receive_loop,
                daemon=True
            )
            self.recv_thread.start()

        except OSError as e:
            self.status_msg = "Connect failed"
            self.connecting = False

    # text messaging
    def send_message(self, text):
        text = text.strip()
        if not text:
            return False, "Empty message"

        if not self.client_socket or not self.is_connected:
            return False, "Not connected"

        try:
            packet = {
                "type": "text",
                "text": text
            }
            self._send_packet(packet)
            add_message("out", text)
            self.status_msg = "Sent"
            return True, "Sent"

        except OSError as e:
            self.status_msg = "Send failed"
            self._clear_connection()
            return False, "Send failed"

    # file transfer
    def send_file(self, filepath, ack_timeout=3.0):
        if not self.client_socket or not self.is_connected:
            return False, "Not connected"

        if not filepath.exists():
            return False, "File not found"

        if filepath.suffix.lower() != ".zip":
            return False, "Only .zip supported here"

        if self.outgoing_transfer is not None:
            return False, "Transfer in progress"

        self.file_send_thread = threading.Thread(
            target=self._send_file_worker,
            args=(filepath, ack_timeout),
            daemon=True
        )
        self.file_send_thread.start()
        return True, "Transfer started"

    def _send_file_worker(self, filepath, ack_timeout=3.0):
        try:
            meta = build_file_start_packet(filepath)
            transfer_id = meta["transfer_id"]
            total_chunks = meta["chunks"]

            self.outgoing_transfer = {
                "transfer_id": transfer_id,
                "name": meta["name"],
                "current": 0,
                "total": total_chunks,
                "direction": "out"
            }

            self._send_packet(meta)
            self.status_msg = f"Sending {meta['name']}"

            for chunk_packet in iter_file_chunks(filepath):
                chunk_packet["transfer_id"] = transfer_id
                index = chunk_packet["index"]

                ack_event = threading.Event()
                with self.pending_acks_lock:
                    self.pending_acks[(transfer_id, index)] = ack_event

                self._send_packet(chunk_packet)

                ok = ack_event.wait(timeout=ack_timeout)

                with self.pending_acks_lock:
                    self.pending_acks.pop((transfer_id, index), None)

                if not ok:
                    self.status_msg = "ACK timeout"
                    return

                self.outgoing_transfer["current"] = index + 1
                self.status_msg = f"Sending {meta['name']} {index + 1}/{total_chunks}"

            self._send_packet({
                "type": "file_end",
                "transfer_id": transfer_id
            })

            self.status_msg = "File sent"

        except OSError as e:
            self.status_msg = "File send failed"
            self._clear_connection()

        finally:
            self.outgoing_transfer = None
        
    # receive loop
    def _receive_loop(self):
        while self.is_connected and self.client_socket:
            try:
                data = self.client_socket.recv(16384)
                if not data:
                    self.status_msg = "Disconnected"
                    self._clear_connection()
                    break

                self.recv_buffer += data.decode("utf-8")

                while "\n" in self.recv_buffer:
                    line, self.recv_buffer = self.recv_buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        packet = try_parse_packet(line)
                    except json.JSONDecodeError:
                        continue

                    self._handle_packet(packet)

            except OSError as e:
                self.status_msg = "Disconnected"
                self._clear_connection()
                break

    def _handle_packet(self, packet):
        ptype = packet.get("type")

        if ptype == "text":
            text = packet.get("text", "").strip()
            if text:
                add_message("in", text)
                self.status_msg = "New message"
            return

        if ptype == "file_start":
            transfer_id = packet["transfer_id"]
            transfer = IncomingFileTransfer(
                transfer_id=transfer_id,
                name=packet["name"],
                size=packet["size"],
                chunks=packet["chunks"],
                sha256_hex=packet["sha256"]
            )
            self.incoming_transfers[transfer_id] = transfer
            self.incoming_transfer_status = {
                "name": transfer.name,
                "current": 0,
                "total": transfer.chunks,
                "direction": "in"
            }
            self.status_msg = f"Receiving {packet['name']}"
            self.request_open_transfer_popup = True
            return

        if ptype == "file_chunk":
            transfer_id = packet["transfer_id"]
            index = packet["index"]
            data_b64 = packet["data"]

            transfer = self.incoming_transfers.get(transfer_id)
            if not transfer:
                self._send_packet({
                    "type": "file_error",
                    "transfer_id": transfer_id,
                    "reason": "unknown transfer"
                })
                return

            raw = decode_chunk_data(data_b64)
            transfer.add_chunk(index, raw)

            self._send_packet({
                "type": "file_ack",
                "transfer_id": transfer_id,
                "index": index
            })

            self.incoming_transfer_status = {
                "name": transfer.name,
                "current": transfer.received_count,
                "total": transfer.chunks,
                "direction": "in"
            }

            self.status_msg = f"Receiving {transfer.name} {transfer.received_count}/{transfer.chunks}"
            return

        if ptype == "file_ack":
            transfer_id = packet["transfer_id"]
            index = packet["index"]

            with self.pending_acks_lock:
                event = self.pending_acks.get((transfer_id, index))
                if event:
                    event.set()
            return

        if ptype == "file_end":
            transfer_id = packet["transfer_id"]
            transfer = self.incoming_transfers.get(transfer_id)
            if not transfer:
                return

            ok, result = transfer.save()
            if ok:
                self.status_msg = "File received"
                self._send_packet({
                    "type": "file_ok",
                    "transfer_id": transfer_id
                })
            else:
                self.status_msg = "File error"
                self._send_packet({
                    "type": "file_error",
                    "transfer_id": transfer_id,
                    "reason": result
                })

            self.incoming_transfers.pop(transfer_id, None)
            self.incoming_transfer_status = None
            return

        if ptype == "file_ok":
            self.status_msg = "File transfer complete"
            return

        if ptype == "file_error":
            reason = packet.get("reason", "unknown error")
            self.status_msg = f"File error: {reason}"
            return

        if ptype == "system":
            return

    # disconnect
    def disconnect(self):
        self._clear_connection()
        self.status_msg = "Disconnected"