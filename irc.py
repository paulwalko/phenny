#!/usr/bin/env python3
"""
irc.py - A Utility IRC Bot
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import asynchat
import asyncore
import functools
import proto
import re
import socket
import ssl
import sys
import time
import traceback
import threading
from tools import decorate


class Origin(object):
    source = re.compile(r'([^!]*)!?([^@]*)@?(.*)')

    def __init__(self, bot, source, args):
        if not source:
            source = ""
        match = Origin.source.match(source)
        self.nick, self.user, self.host = match.groups()

        if len(args) > 1:
            target = args[1]
        else:
            target = None

        mappings = {bot.nick: self.nick, None: None}
        self.sender = mappings.get(target, target)


class Bot(asynchat.async_chat):
    def __init__(self, nick, name, channels, password=None):
        asynchat.async_chat.__init__(self)
        self.set_terminator(b'\n')
        self.buffer = b''

        self.nick = nick
        self.user = nick
        self.name = name
        self.password = password

        self.verbose = True
        self.channels = channels or []
        self.stack = []

        self.sending = threading.RLock()

        proto_func = lambda attr: functools.partial(proto.commands[attr], self)
        proto_map = {attr: proto_func(attr) for attr in proto.commands}
        self.proto = decorate(object(), proto_map)

    def initiate_send(self):
        self.sending.acquire()
        asynchat.async_chat.initiate_send(self)
        self.sending.release()

    # def push(self, *args, **kargs):
    #     asynchat.async_chat.push(self, *args, **kargs)

    def __write(self, args, text=None):
        line = b' '.join(args)

        if text is not None:
            line += b' :' + text

        # 510 because CR and LF count too
        self.push(line[:510] + b'\r\n')

    def write(self, args, text=None):
        """This is a safe version of __write"""
        def safe(input):
            if type(input) == str:
                input = re.sub(' ?(\r|\n)+', ' ', input)
                return input.encode('utf-8')
            else:
                input = re.sub(b' ?(\r|\n)+', b' ', input)
                return input
        try:
            args = [safe(arg) for arg in args]
            if text is not None:
                text = safe(text)
            self.__write(args, text)
        except Exception as e:
            raise

    def run(self, host, port=6667, ssl=False, ipv6=False, ca_certs=None,
            ssl_context=None):
        if ssl_context is None:
            ssl_context = self.get_ssl_context(ca_certs)
        self.initiate_connect(host, port, ssl, ipv6, ssl_context)

    def get_ssl_context(self, ca_certs):
        return ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=ca_certs)

    def initiate_connect(self, host, port, use_ssl, ipv6, ssl_context):
        if self.verbose:
            message = 'Connecting to %s:%s...' % (host, port)
            print(message, end=' ', file=sys.stderr)
        if ipv6 and socket.has_ipv6:
            af = socket.AF_INET6
        else:
            af = socket.AF_INET
        self.create_socket(af, socket.SOCK_STREAM, use_ssl, host, ssl_context)
        self.connect((host, port))
        try:
            asyncore.loop()
        except KeyboardInterrupt:
            sys.exit()

    def create_socket(self, family, type, use_ssl=False, hostname=None,
                      ssl_context=None):
        self.family_and_type = family, type
        sock = socket.socket(family, type)
        if use_ssl:
            sock = ssl_context.wrap_socket(sock, server_hostname=hostname)
        # FIXME: this doesn't work with SSL enabled
        #sock.setblocking(False)
        self.set_socket(sock)

    def handle_connect(self):
        if self.verbose:
            print('connected!', file=sys.stderr)

        if self.password:
            self.proto.pass_(self.password)

        self.proto.nick(self.nick)
        self.proto.user(self.user, '+iw', self.name)

    def handle_close(self):
        self.close()
        print('Closed!', file=sys.stderr)

    def collect_incoming_data(self, data):
        self.buffer += data

    def found_terminator(self):
        line = self.buffer
        if line.endswith(b'\r'):
            line = line[:-1]
        self.buffer = b''

        try:
            line = line.decode('utf-8')
        except UnicodeDecodeError:
            line = line.decode('iso-8859-1')

        if line.startswith(':'):
            source, line = line[1:].split(' ', 1)
        else:
            source = None

        if ' :' in line:
            argstr, text = line.split(' :', 1)
        else:
            argstr, text = line, ''
        args = argstr.split()

        origin = Origin(self, source, args)
        self.dispatch(origin, tuple([text] + args))

        if args[0] == 'PING':
            self.proto.pong(text)

    def dispatch(self, origin, args):
        pass

    def msg(self, recipient, text):
        self.sending.acquire()

        # Cf. http://swhack.com/logs/2006-03-01#T19-43-25
        if isinstance(text, str):
            try:
                text = text.encode('utf-8')
            except UnicodeEncodeError as e:
                text = e.__class__ + ': ' + str(e)
        if isinstance(recipient, str):
            try:
                recipient = recipient.encode('utf-8')
            except UnicodeEncodeError as e:
                return

        # No messages within the last 3 seconds? Go ahead!
        # Otherwise, wait so it's been at least 0.8 seconds + penalty
        if self.stack:
            elapsed = time.time() - self.stack[-1][0]
            if elapsed < 3:
                penalty = float(max(0, len(text) - 50)) / 70
                wait = 0.8 + penalty
                if elapsed < wait:
                    time.sleep(wait - elapsed)

        # Loop detection
        messages = [m[1] for m in self.stack[-8:]]
        if messages.count(text) >= 5:
            text = '...'
            if messages.count('...') >= 3:
                self.sending.release()
                return

        self.proto.privmsg(recipient, text)
        self.stack.append((time.time(), text))
        self.stack = self.stack[-10:]

        self.sending.release()

    def action(self, recipient, text):
        text = "\x01ACTION {0}\x01".format(text)
        return self.msg(recipient, text)

    def error(self, origin):
        try:
            trace = traceback.format_exc()
            print(trace)
            lines = list(reversed(trace.splitlines()))

            report = [lines[0].strip()]
            for line in lines:
                line = line.strip()
                if line.startswith('File "/'):
                    report.append(line[0].lower() + line[1:])
                    break
            else:
                report.append('source unknown')

            self.msg(origin.sender, report[0] + ' (' + report[1] + ')')
        except:
            self.msg(origin.sender, "Got an error.")


class TestBot(Bot):
    def f_ping(self, origin, match, args):
        delay = match.group(1)
        if delay is not None:
            import time
            time.sleep(int(delay))
            self.msg(origin.sender, 'pong (%s)' % delay)
        else:
            self.msg(origin.sender, 'pong')
    f_ping.rule = r'^\.ping(?:[ \t]+(\d+))?$'


def main():
    bot = TestBot('testbot007', 'testbot007', ['#wadsworth'])
    bot.run('irc.freenode.net')
    print(__doc__)


if __name__ == "__main__":
    main()
