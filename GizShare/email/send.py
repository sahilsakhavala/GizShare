import threading
from GizShare.email.templates import verify_email, reset_password_mail, send_email_to_interested_users


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        print(self.email, 'Email send successfully')


class EmailSender:
    @staticmethod
    def verify_email(request, user):
        EmailThread(verify_email(request, user)).start()

    @staticmethod
    def reset_password_request_mail(request, user):
        EmailThread(reset_password_mail(request, user)).start()

    @staticmethod
    def post_mail(request, post, interested_users):
        EmailThread(send_email_to_interested_users(request, post, interested_users)).start()
