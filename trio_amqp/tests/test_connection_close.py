import pytest

from trio_amqp.protocol import OPEN, CLOSED
from trio_amqp.exceptions import AmqpClosedConnection

from . import testcase
from . import testing


class TestClose(testcase.RabbitTestCase):

    async def test_close(self, amqp):
        assert amqp.state == OPEN
        # grab a ref here because py36 sets _stream_reader to None in
        # StreamReaderProtocol.connection_lost()
        sock = amqp._stream.socket
        await amqp.aclose()
        assert amqp.state == CLOSED
        assert sock.fileno() == -1
        # make sure those 2 tasks/futures are properly set as finished
        assert amqp.connection_closed.is_set()
        assert amqp._heartbeat_timer_recv is None
        assert amqp._heartbeat_timer_send is None

    async def test_multiple_close(self, amqp):
        # aclose is supposed to be idempotent
        await amqp.aclose()
        assert amqp.state == CLOSED
        await amqp.aclose()
        assert amqp.state == CLOSED
