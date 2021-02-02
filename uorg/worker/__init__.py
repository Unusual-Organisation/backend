from uorg import celery
from uorg.worker.emails import send_mail_html
from uorg.worker.emails import send_mail_text

__all__ = ["send_mail_text", "send_mail_html"]


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    pass
