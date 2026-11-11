from .imap_fetcher import MailFetcher


def main():
    mail_fetcher = MailFetcher()
    mail_fetcher = MailFetcher()
    unread_mails = mail_fetcher.getUnreadMail()
    mail_fetcher.disconnect()

    