from aiosmtpd.controller import Controller


class CapturingAiosmtpdHandler:
    """An async SMTP handler.

    More or less follows the docs example:
    https://github.com/aio-libs/aiosmtpd/blob/master/aiosmtpd/docs/controller.rst

    Important! Rejects messages not addressed to the "@example.com" domain.
    """

    def __init__(self, context):
        self.context = context

    async def handle_RCPT(
            self, server, session, envelope, address, rcpt_options):
        if not address.endswith('@example.com'):
            return '550 not relaying to that domain'
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        self.context.messages.append(envelope)
        return '250 Message accepted for delivery'


class CapturingAiosmtpdServer:
    """An async SMTP server / context manager for testing RPC effects."""

    def __init__(self):
        self.messages = []
        self.handler = CapturingAiosmtpdHandler(context=self)
        self.controller = Controller(
            handler=self.handler, hostname="localhost", port=10025)

    def __enter__(self):
        self.controller.start()
        return self

    def __exit__(self, *exc):
        self.controller.stop()
