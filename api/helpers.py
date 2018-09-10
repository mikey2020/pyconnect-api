from flask import jsonify
# from main import celery

def response_json(status_code, value):
    """ helps send a json response """
    response = jsonify(value)
    response.status_code = status_code
    return response

# @celery.task()
# def email_notification(subject, recipients, _link):
#     msg = Message(subject, sender=sender, recipients=recipients)
#     msg.body = "Confirm Email: {}".format(_link)
#     with app.app_context():
#         mail.send(msg)
#     return "\n\nEmail sent successfully\n\n"