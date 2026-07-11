import grpc
from concurrent import futures
import time
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "generated"))

import video_pb2
import video_pb2_grpc


OUTPUT_FILE = "stream.h264"


class VideoStreamer(video_pb2_grpc.VideoStreamerServicer):

    def Stream(self, request_iterator, context):

        print("=" * 50)
        print("Client connected")

        total_bytes = 0
        chunk_count = 0

        with open(OUTPUT_FILE, "wb") as f:

            for chunk in request_iterator:

                data = chunk.data

                f.write(data)

                total_bytes += len(data)

                chunk_count += 1

                if chunk_count % 100 == 0:
                    print(
                        f"Chunks: {chunk_count:6d} | "
                        f"Received: {total_bytes / 1024 / 1024:.2f} MB"
                    )

        print("\nClient disconnected")
        print(f"Saved -> {OUTPUT_FILE}")
        print(f"Total chunks : {chunk_count}")
        print(f"Total bytes  : {total_bytes}")

        return video_pb2.Empty()


def serve():

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=2)
    )

    video_pb2_grpc.add_VideoStreamerServicer_to_server(
        VideoStreamer(),
        server
    )

    server.add_insecure_port("[::]:50051")

    server.start()

    print("=" * 50)
    print("gRPC Video Server Started")
    print("Listening on port 50051")
    print("=" * 50)

    try:
        while True:
            time.sleep(86400)

    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop(0)


if __name__ == "__main__":
    serve()