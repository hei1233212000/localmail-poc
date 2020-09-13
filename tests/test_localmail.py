import email
import imaplib
import smtplib
import threading
from typing import Optional

import localmail
from waiting import wait

from src.my_logger import get_logger

__logger = get_logger(__name__)
__localmail_thread: Optional[threading.Thread] = None
__smtp_port: Optional[int] = None
__imap_port: Optional[int] = None
__http_port: Optional[int] = None
__host = 'localhost'


def setup_function(function):
    __logger.info('going to start localmail thread...')

    def report(smtp, imap, http):
        global __smtp_port
        __smtp_port = smtp
        __logger.info('smtp port: {}'.format(smtp))

        global __imap_port
        __imap_port = imap
        __logger.info('imap port: {}'.format(imap))

        global __http_port
        __http_port = http
        __logger.info('http port: {}'.format(http))

    global __localmail_thread
    __localmail_thread = threading.Thread(
        target=localmail.run,
        args=(0, 0, 0, None, report)
    )
    __localmail_thread.start()
    wait(lambda: __http_port is not None, timeout_seconds=5)
    __logger.info('localmail thread is started')


def teardown_function(function):
    __logger.info('going to shut down the localmail thread...')
    localmail.shutdown_thread(__localmail_thread)
    __logger.info('localmail thread is stopped')


def test_send_and_receive():
    # send out email
    __logger.info('__smtp_port: {}'.format(__smtp_port))
    smtp = smtplib.SMTP(__host, __smtp_port)
    smtp.login('a', 'b')
    smtp.sendmail('a@b.com', ['c@d.com'], 'Subject: test\n\ntest')
    smtp.quit()

    # receive the mail
    __logger.info('__imap_port: {}'.format(__imap_port))
    imap = imaplib.IMAP4(__host, __imap_port)
    imap.login('any', 'thing')
    imap.select()
    status, data = imap.search('ALL')
    assert status == 'OK'

    for num in data[0].split():
        typ, data = imap.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        # converts byte literal to string removing b''
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)
        __logger.info(email_message)

    imap.close()
    imap.logout()
