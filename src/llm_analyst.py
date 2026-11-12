import os

from dotenv import load_dotenv
from ollama import chat

from src.models.mail import Mail

load_dotenv()


class Agent:
    def __init__(self):
        self.model = "mistral"
        self.user_context = self._loadUserContext()

    def _loadUserContext(self) -> str:
        return f"""
        - Nom complet : {os.getenv('USER_FIRST_NAME', '')} \
            {os.getenv('USER_LAST_NAME', '')}
        - Centre d'interet: {os.getenv('USER_ROLE', '')} chez \
            {os.getenv('USER_COMPANY', '')}
        - Localisation : {os.getenv('USER_CITY', '')}
        - Style d'écriture : {os.getenv('USER_TONE', '')}
        - Règles strictes à respecter : {os.getenv('USER_RULES', '')}
        - Famille: {os.getenv('USER_FAMILY', '')}
        - Amis: {os.getenv('USER_FRIENDS', '')}
        - Mail personnel: {os.getenv('GMAIL_ADDR'), ''}
        """

    def isAnswering(self, mail: Mail) -> None:
        prompt_mail = f"De : {mail.sender}\nSujet : {mail.subject}\n\
            Message:\n{mail.message}\n\
            Piece jointe: {" ".join(mail.attachment)}"

        general_prompt = f"""
        Tu es un assistant chargé de trier les e-mails.
        Détermine si l'e-mail suivant nécessite une réponse humaine \
            (ignore les newsletters, pubs, notifications automatiques, spams).
        Réponds UNIQUEMENT par 'True' ou 'False', sans aucun autre mot.

        E-mail :
        {prompt_mail}
        """

        response = chat(
            model=self.model,
            messages=[{"role": "user", "content": general_prompt}],
        )

        content = response.message.content or ""
        if "True" in content:
            mail.to_answer = True
            res1, res2 = self.createAnswer(prompt_mail)
            if res1:
                mail.response1 = res1
            if res2:
                mail.response2 = res2

    def createAnswer(self, mail_content: str) -> tuple[str | None, str | None]:
        system_prompt_1 = f"""
        Tu es {os.getenv('USER_FIRST_NAME')}. Tu réponds à tes propres e-mails.
        Voici ton profil et tes règles de comportement :
        {self.user_context}

        CONSIGNE DE STYLE (Option 1 - Direct & Efficace) :
        - Rédige une réponse courte, claire et professionnelle.
        - Va droit au but sans phrases de politesse à rallonge.
        - Reflète tes valeurs et tes règles strictes.
        - Réponds uniquement avec le corps du mail prêt à être envoyé \
            (sans objet, sans commentaire avant ou après).
        - Écris dans la même langue que l'e-mail reçu.
        """

        system_prompt_2 = f"""
        Tu es {os.getenv('USER_FIRST_NAME')}. Tu réponds à tes propres e-mails.
        Voici ton profil et tes règles de comportement :
        {self.user_context}

        CONSIGNE DE STYLE (Option 2 - Humain & Chaleureux) :
        - Rédige une réponse naturelle, empathique et engageante, \
            comme si tu écrivais à un contact apprécié.
        - N'hésite pas à rebondir sur un détail du message ou \
            à proposer un échange ouvert selon tes disponibilités.
        - Évite le jargon robotique ou trop corporatif.
        - Réponds uniquement avec le corps du mail prêt à être envoyé \
            (sans objet, sans commentaire avant ou après).
        - Écris dans la même langue que l'e-mail reçu.
        """

        response1 = chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt_1},
                {"role": "user", "content": f"Voici l'e-mail reçu auquel \
                    tu dois répondre :\n\n{mail_content}"},
            ],
        )

        response2 = chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt_2},
                {"role": "user", "content": f"Voici l'e-mail reçu auquel \
                    tu dois répondre :\n\n{mail_content}"},
            ],
        )

        return (response1.message.content, response2.message.content)
