"""Optional SMTP adapter; disabled unless explicitly configured by its caller."""

import smtplib
from email.message import EmailMessage


class NotificationService:
    def __init__(
        self, host=None, port=587, username=None, password=None, enabled=False
    ):
        self.host, self.port, self.username, self.password, self.enabled = (
            host,
            port,
            username,
            password,
            enabled,
        )

    def send_email(self, to, subject, body):
        if not self.enabled:
            return False
        if not all((self.host, self.username, self.password)):
            raise ValueError("SMTP configuration required")
        message = EmailMessage()
        message["From"] = self.username
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP(self.host, self.port, timeout=5) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(message)
        return True

    def notify_task_assigned(self, user, task):
        return self.send_email(
            user.email, f"Nova task: {task.title}", f"Task {task.id} atribuída"
        )

    def notify_task_overdue(self, user, task):
        return self.send_email(
            user.email, f"Task atrasada: {task.title}", f"Prazo: {task.due_date}"
        )
