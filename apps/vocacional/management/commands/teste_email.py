from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = "Envia um e-mail de teste usando as credenciais SMTP configuradas"

    def add_arguments(self, parser):
        parser.add_argument("--to", default="wygazeta@gmail.com", help="Destinatário do teste")
        parser.add_argument("--subject", default="Teste SMTP", help="Assunto")
        parser.add_argument("--body", default="Funcionou! 🎉", help="Mensagem")

    def handle(self, *args, **opts):
        to = [opts["to"]]
        subject = opts["subject"]
        body = opts["body"]
        sent = send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=to,
            fail_silently=False,
        )
        self.stdout.write(self.style.SUCCESS(f"E-mail enviado: {sent}"))
