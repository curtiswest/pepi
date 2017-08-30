from server import StreamerThread


def test_streamer_thread_init():
    _ = StreamerThread('/tmp')
