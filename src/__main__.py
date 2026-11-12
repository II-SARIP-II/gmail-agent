import asyncio

from src.imap_fetcher import MailFetcher
from src.llm_analyst import Agent
from src.telegram_bot import TelegramBot


def main():
    mail_fetcher = MailFetcher()
    unread_mails = mail_fetcher.getUnreadMail()
    mail_fetcher.disconnect()
    agent = Agent()
    mails_to_answer = []

    for mail in unread_mails:
        agent.isAnswering(mail)
        if mail.to_answer:
            mails_to_answer.append(mail)

    if mails_to_answer:
        bot = TelegramBot(mails_to_answer)
        asyncio.run(bot.start())


if __name__ == "__main__":
    main()
