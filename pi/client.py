import subprocess
import grpc

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "generated"))

import video_pb2
import video_pb2_grpc


# ==========================
# CONFIG
# ==========================

SERVER_IP = "192.168.1.11"      # <-- IP PC
SERVER_PORT = 50051

WIDTH = 640
HEIGHT = 480
FPS = 15
DURATION_MS = 30000

CHUNK_SIZE = 4096

# ==========================


def video_generator():

    cmd = [
        "rpicam-vid",

        "-t", str(DURATION_MS),

        "--codec", "h264",

        "--width", str(WIDTH),

        "--height", str(HEIGHT),

        "--framerate", str(FPS),

        "--inline",

        "-o", "-"
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=0
    )

    print("Camera started.")

    while True:

        chunk = process.stdout.read(CHUNK_SIZE)

        if not chunk:
            break

        yield video_pb2.VideoChunk(data=chunk)

    process.wait()

    print("Camera stopped.")


def main():

    target = f"{SERVER_IP}:{SERVER_PORT}"

    channel = grpc.insecure_channel(target)

    stub = video_pb2_grpc.VideoStreamerStub(channel)

    print(f"Connecting to {target}")

    try:

        stub.Stream(video_generator())

        print("Streaming finished.")

    except grpc.RpcError as e:

        print("gRPC Error")
        print(e)


if __name__ == "__main__":
    main()