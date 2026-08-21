import smtplib
from email.message import EmailMessage


def enviar_relatorio(
    remetente,
    senha,
    destinatario,
    assunto,
    conteudo,
    servidor="smtp.gmail.com",
    porta=465,
):

    mensagem = EmailMessage()
    mensagem["From"] = remetente
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.set_content(conteudo)

    with smtplib.SMTP_SSL(servidor, porta) as smtp:
        smtp.login(remetente, senha)
        smtp.send_message(mensagem)
