import email
import imaplib
import os
from datetime import datetime
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime
from typing import Any

from dotenv import load_dotenv

from src.models.mail import Mail

load_dotenv()


class MailFetcher:
    def __init__(self):
        EMAIL = os.environ["GMAIL_ADDR"]
        PASSWORD = os.environ["GMAIL_PASSWORD"]
        IMAP_LINK = os.environ["GMAIL_IMAP_LINK"]
        IMAP_PORT = os.environ["GMAIL_IMAP_PORT"]
        if not EMAIL or not PASSWORD or not IMAP_LINK or not IMAP_PORT:
            raise ValueError("EMAIL or PASWORD or IMAP field \
                are not configured correctly in .env")
        self.gmail = imaplib.IMAP4_SSL(IMAP_LINK, IMAP_PORT)
        self.gmail.login(EMAIL, PASSWORD)

    def getUnreadMailId(self) -> list[Any]:
        self.gmail.select("inbox")

        _, messages = self.gmail.search(None, "UNSEEN")
        mail_ids = messages[0].split()
        return mail_ids

    @staticmethod
    def _decode_header_value(raw_value: str | None) -> str:
        if not raw_value:
            return ""
        decoded_fragments: list[str] = []
        for part, encoding in decode_header(raw_value):
            if isinstance(part, bytes):
                decoded_fragments.append(
                    part.decode(encoding or "utf-8", errors="replace")
                )
            else:
                decoded_fragments.append(str(part))
        return "".join(decoded_fragments)

    def getUnreadMail(self) -> list[Mail]:
        mail_ids = self.getUnreadMailId()
        mails: list[Mail] = []
        for mail_id in mail_ids:
            _, data = self.gmail.fetch(mail_id, "(RFC822)")

            for mail_id in mail_ids:
                _, data = self.gmail.fetch(mail_id, "(RFC822)")

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        subject = (
                            self._decode_header_value(msg["Subject"])
                            or "Sans sujet"
                        )
                        sender = (
                            self._decode_header_value(msg["From"])
                            or "Expéditeur inconnu"
                        )
                        body = self.getEmailBody(msg)
                        attachments = self.getAttachmentTitles(msg)

                        raw_date = msg["Date"]
                        mail_date = (
                            parsedate_to_datetime(raw_date)
                            if raw_date
                            else datetime.now()
                        )

                        mail_obj = Mail(
                            id=mail_id.decode() if isinstance(mail_id, bytes) else mail_id,
                            sender=sender,
                            date=mail_date,
                            subject=subject,
                            message=body,
                            attachment=attachments,
                        )
                        mails.append(mail_obj)
        return mails

    def getAttachmentTitles(self, msg: Message) -> list[str]:
        titles: list[str] = []

        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue

            raw_filename = part.get_filename()
            content_disposition = str(part.get("Content-Disposition", ""))

            if raw_filename or "attachment" in content_disposition:
                filename = (
                    self._decode_header_value(raw_filename)
                    if raw_filename
                    else "piece_jointe_sans_nom"
                )
                titles.append(os.path.basename(filename))

        return titles

    def getEmailBody(self, msg: Message) -> str:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if (
                    content_type == "text/plain"
                    and "attachment" not in content_disposition
                ):
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        charset = part.get_content_charset() or "utf-8"
                        body = payload.decode(charset, errors="replace")
                    break
        else:
            payload = msg.get_payload(decode=True)
            if isinstance(payload, bytes):
                charset = msg.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="replace")

        return body

    def disconnect(self):
        if self.gmail:
            try:
                self.gmail.close()
            except imaplib.IMAP4.error:
                pass
            self.gmail.logout()


if __name__ == "__main__":
    m = MailFetcher()
    m.getUnreadMail()
    m.disconnect()
