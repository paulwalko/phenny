#!/usr/bin/python3
"""
bash.py - bash.org clone. Saves quotes from quote-logger module to a db
author: paulwalko <paul@walko.org>
"""

from threading import Thread
import os, sqlite3, time, web

queue = []

def setup(self):
    """Creates sqlite database to store quotes
    """
    fn = self.nick + '-' + self.config.host + '.bash.db'
    bash_quotes = 'bash_logs'
    self.bash_quotes_path = os.path.join(os.path.expanduser('~/.phenny'), bash_quotes)
    self.bash_db = os.path.join(os.path.expanduser('~/.phenny'), fn)
    self.bash_conn = sqlite3.connect(self.bash_db)

    if not os.path.exists(self.bash_quotes_path):
        os.makedirs(self.bash_quotes_path)

    c = self.bash_conn.cursor()
    c.execute('''create table if not exists quotes (
        id      integer primary key autoincrement,
        channel varchar(255),
        nick    varchar(255),
        quote   text,
        time    timestamp default CURRENT_TIMESTAMP
    );''')

    c.execute('''create table if not exists stats (
        id      integer primary key autoincrement,
        channel varchar(255),
        nick    varchar(255),
        lines   unsigned big int not null default 0,
        unique (channel, nick) on conflict replace
    );''')
    c.close()

    # Start thread to check for new messages
    Thread(target = insert_into_db_caller, args=(self,)).start()

def insert_into_db(phenny, sqlite_data):
    """inserts message to to temp db"""

    if not bash.conn:
        bash.conn = sqlite3.connect(phenny.bash_db)

    c = bash.conn.cursor()

    c.execute('''INSERT INTO quotes
        (channel, nick, quote, time)
        VALUES(
            :channel,
            :nick,
            :quote,
            CURRENT_TIMESTAMP
        );''', sqlite_data)

    c.execute('''INSERT OR REPLACE INTO stats
        (channel, nick, lines)
        VALUES(
            :channel,
            :nick,
            COALESCE((SELECT lines FROM stats WHERE channel=:channel AND nick=:nick) + 1, 1)
        );''', sqlite_data)


    c.close()
    bash.conn.commit()

    c = bash.conn.cursor()

    c.execute('''SELECT id FROM quotes ORDER BY id DESC LIMIT 1''')
    last_id = c.fetchall()[0][0] - 99

    c.execute('''SELECT channel, nick FROM quotes WHERE id < ?''', (last_id,))
    rows = c.fetchall()
    for row in rows:
        channel = row[0]
        nick = row[1]

        c.execute('''SELECT lines FROM stats WHERE channel=? AND nick=?''', (channel, nick))
        lines = 0
        lines = c.fetchall()[0][0]

        if lines - 1 == 0:
            c.execute('''DELETE FROM stats WHERE channel=? AND nick=?''', (channel, nick))
        else:
            c.execute('''REPLACE INTO stats
                (channel, nick, lines)
                VALUES(
                    ?,
                    ?,
                    (SELECT lines FROM stats WHERE channel=? AND nick=?) - 1
             );''', (channel, nick, channel, nick))

        c.execute('''DELETE FROM quotes WHERE id < ?''', (last_id,))

    c.close()
    bash.conn.commit()

def insert_into_db_caller(phenny):
    """Checks for a new quote once a second
    """
    while True:
        global queue
        if len(queue) > 0:
            insert_into_db(phenny, queue.pop(0))
        time.sleep(1)

def logger(phenny, input):
    """logs everyting to specific format, except we only keep last 100 lines
    """

    allowed_actions = ['PRIVMSG', 'JOIN', 'QUIT', 'PART', 'NICK', 'KICK', 'MODE']

    if input.event not in allowed_actions:
        return

    message=''
    if input.event == 'PRIVMSG':
        channel = input.sender
        nick = input.nick
        if input.group(1)[:8] == '\x01ACTION ':
            quote = "* {nick} {msg}".format(nick=nick, msg=input.group(1)[8:-1])
        else:
            quote = "<{nick}> {msg}".format(nick=nick, msg=input.group(1))
    elif input.event == 'JOIN':
        channel = input.group(1)
        nick = input.nick
        quote = "--> {nick} has joined {channel}".format(nick=nick, channel=channel)
    elif input.event == 'PART':
        channel = input.sender
        nick = input.nick
        if input.group(1):
            message = " ({message})".format(message=input.group(1))
        quote = "<-- {nick} has left {channel}{message}" \
                .format(nick=nick, channel=channel, message=message)
    elif input.event == 'QUIT':
        channel = 'ALL'
        nick = input.nick
        if input.group(1):
            message = " ({message})".format(message=input.group(1))
        quote = "<-- {nick} has quit{message}".format(nick=nick, message=message)
    elif input.event == 'KICK':
        channel = input.sender
        nick = input.nick
        quote = "<-- {nick} has kicked {nick_kick} [{kick_msg}] from {channel}" \
                .format(nick=nick, nick_kick=input.args[1],
                        kick_msg=input.group(1), channel=channel)
    elif input.event == 'NICK':
       channel = 'ALL'
       nick = input.nick
       quote = "-- {nick} is now known as {nick_new}" \
               .format(nick=nick, nick_new=input.group(1))
    elif len(input.args) > 0 and input.args[0].startswith('#'):
        channel = input.sender
        nick = input.nick
        args = str(input.args[1:]).replace('(', '').replace(')', '').replace("'", '')
        if args.endswith(','):
            args = args.replace(',', '')
        else:
            args = args.replace(',', ' ')
        quote = "-- Mode {channel} [{args}] by {nick}" \
                .format(channel=input.sender, args=args, nick=input.nick)
    else:
        return

    quote = "{quote}\n".format(quote=quote)

    sqlite_data = {
        'channel': channel,
        'nick': nick,
        'quote': quote
    }

    global queue
    queue.append(sqlite_data)

def bash(phenny, input):
    """'.bash' - queries a quote selection to add"""
    usage = ('Usage: .bash <nick_1> <# msgs to start at> <nick_2>'
            ' <# msgs to end at> (Specifies a range of messages)')

    input_all = input.group(2)
    if not input_all:
        phenny.say(usage)
        return

    input_args = input_all.split()
    if len(input_args) < 4:
        phenny.say(usage)
        return

    channel = input.sender
    nick1 = input_args[0]
    nick1_start_str = input_args[1]
    nick2 = input_args[2]
    nick2_end_str = input_args[3]

    # Check Input Type
    if not nick1_start_str.isdigit() or not nick2_end_str.isdigit():
        phenny.say('Error: 2nd & 4th argument must be integers')
        phenny.say(usage)
        return

    nick1_start = int(nick1_start_str)
    nick2_end = int(nick2_end_str)

    # Connect to db
    fn = phenny.nick + '-' + phenny.config.host + '.bash.db'
    bash_db = os.path.join(os.path.expanduser('~/.phenny'), fn)
    bash_conn = sqlite3.connect(bash_db)
    c = bash_conn.cursor()

    # Check input for validity
    c.execute('''SELECT lines FROM stats
            WHERE (channel=? OR channel='NULL')
            AND nick=?''', (channel, nick1))
    rows = c.fetchall()
    nick1_total = 0
    for row in rows:
        nick1_total = nick1_total + row[0]

    c.execute('''SELECT lines FROM stats
            WHERE (channel=? OR channel='NULL')
            AND nick=?''', (channel, nick2))
    rows = c.fetchall()
    nick2_total = 0
    for row in rows:
        nick2_total = nick2_total + row[0]

    if nick1_total < nick1_start:
        phenny.say("Error: {} has not done {} actions ({} replies not included)" \
                .format(nick1, nick1_start, phenny.nick))
        return

    if nick2_total < nick2_end:
        phenny.say("Error: {} has not done {} actions ({} replies not included)" \
                .format(nick2, nick2_end, phenny.nick))
        return

    # Fetch quote ids
    c.execute('''SELECT id, channel, nick FROM quotes
            WHERE (channel=? OR channel='ALL')
            AND nick=?''', (channel, nick1))
    rows = c.fetchall()
    nick1_id = -1
    for row, i in zip(reversed(rows), range(nick1_start)):
        if i == nick1_start - 1:
            nick1_id = row[0]

    c.execute('''SELECT id, channel, nick FROM quotes
            WHERE (channel=? OR channel='ALL')
            AND nick=?''', (channel, nick2))
    rows = c.fetchall()
    nick2_id = -1
    for row, i in zip(reversed(rows), range(nick2_end)):
        if i == nick2_end - 1:
            nick2_id = row[0]

    if nick2_id < nick1_id:
        phenny.say('Error, try again. 2nd message must occur after first message.')
        phenny.say(usage)
        return

    # Fetch quotes within range of ids
    c.execute('''SELECT quote FROM quotes
            WHERE (channel=? OR channel='ALL')
            AND id >= ? AND id <= ?''', (channel, nick1_id, nick2_id))
    final_lines = []
    for line in c.fetchall():
        final_lines.append(line[0])
    final_lines = ''.join(final_lines)


    quote_json = {
        'body': final_lines,
        'tags': ','.join([phenny.nick, nick1, nick2]),
        'key': phenny.config.bash_api_key
    }

    web.post('https://bash.vtluug.org/quotes', {}, {}, True, json=quote_json)

    phenny.say('Check https://bash.vtluug.org/quotes to see your quote!')

bash.conn = None
bash.rule = (['bash', 'vtbash', 'quote'], r'(.*)')
logger.event = '*'
logger.rule = r'(.*)'

if __name__ == '__main__':
    print(__doc__.strip())
