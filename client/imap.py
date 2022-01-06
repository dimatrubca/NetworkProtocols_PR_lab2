import imaplib
import pprint
import os
from dotenv import load_dotenv
from os.path import join, dirname
import email
from email.header import decode_header
import webbrowser

from models import User


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

# todo: refactor
def retrieve_mailbox(user: User):
    # connect to host using SSL
    imap_host = os.environ['imap_host']
    imap_user = user.email
    imap_pass = user.password

    imap = imaplib.IMAP4_SSL(imap_host)

    ## login to server
    imap.login(imap_user, imap_pass)

    status, messages = imap.select("INBOX")
    # number of top emails to fetch
    N = 3
    # total number of emails
    messages = int(messages[0])

    mailbox = []
        
    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                print("Subject:", subject)
                print("From:", From)


            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # print text/plain emails and skip attachments
                        print(body)
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print only text email parts
                    print(body)

        mailbox.append([From, subject, body])
    # close the connection and logout
    imap.close()
    imap.logout()

    return mailbox