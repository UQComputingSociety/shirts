from wtforms import validators, fields, form
from mako.lookup import TemplateLookup
from flask import Flask, request, redirect
from queue import Queue
from threading import Thread
import datetime as dt
import premailer
import requests
import os
import stripe

stripe.api_key = os.environ.get("STRIPE_API_KEY")
lookup = TemplateLookup(["views", "emails"], input_encoding='utf-8')
queue = Queue()
app = Flask(__name__)
sizes = ["XS", "S", "M", "L", "XL", "2XL", "3XL"]
styles = ["Men's", "Women's"]

class Preorder(object):
    def __init__(self, first_name=None, last_name=None, email=None, shirt_size=None, shirt_style=None, payment_token=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.shirt_size = shirt_size
        self.shirt_style = shirt_style
        self.payment_token = payment_token

    def to_csv(self):
        return ",".join(map(str,[
            self.first_name,
            self.last_name,
            self.email,
            self.shirt_size,
            self.shirt_style,
            self.payment_token
        ]))

    def send_email(self):
        receiptText = lookup.get_template("text.mako") \
            .render(user=self, dt=dt)
        receiptHTML = lookup.get_template('html.mako') \
            .render(user=self, dt=dt)
        requests.post("https://api.mailgun.net/v3/uqcs.org.au/messages",
                      auth=('api', os.environ.get("MAILGUN_API_KEY")),
                      data={
                          'from': 'receipts@uqcs.org.au',
                          'to': self.email,
                          'bcc': "receipts@uqcs.org.au",
                          'text': receiptText,
                          'html': premailer.transform(receiptHTML),
                          'subject': "2016 Shirt Pre-order",
                      })


def do_stripe_payment(form, field):
    try:
        charge = stripe.Charge.create(
            amount=2065, # amount in cents, again
            currency="aud",
            source=field.data,
            description="UQCS Shirt Preorder"
        )
        field.data = charge['id']
    except stripe.error.CardError as e:
        raise validators.ValidationError("Card declined")
    except stripe.error.InvalidRequestError as e:
        raise validators.ValidationError("Something went wrong when processing your payment")


class ShirtForm(form.Form):
    first_name = fields.StringField(
        "First Name",
        validators=[
            validators.InputRequired(),
        ],
    )
    last_name = fields.StringField(
        "Last Name",
        validators=[
            validators.InputRequired(),
        ],
    )
    email = fields.StringField(
        "Email",
        validators=[
            validators.Email(),
        ],
    )
    shirt_size = fields.RadioField(
        "Shirt Size",
        choices=list(zip(sizes, sizes)),
        validators=[
            validators.InputRequired(),
        ],
    )
    shirt_style = fields.RadioField(
        "Shirt Style",
        choices=list(zip(styles, styles)),
        validators=[
            validators.InputRequired(),
        ],
    )
    payment_token = fields.HiddenField(
        validators=[
            do_stripe_payment,
        ],
    )


@app.route("/", methods=["GET", "POST"])
def form():
    
    res = ShirtForm(request.form)
    if request.method == "POST" and res.validate():
        print(request)
        order_obj = Preorder()
        res.populate_obj(order_obj)
        queue.put(order_obj)
        with open("out.csv", "a+") as f:
            f.write(order_obj.to_csv() + "\n")
        return redirect('/confirmed', 303)
    return lookup.get_template("order.mako").render(form=res)

@app.route("/confirmed")
def confirmed():
    return lookup.get_template("confirmed.mako").render()


def order_processing():
    for order in iter(queue.get, None):
        order.send_email()


if __name__ == "__main__":
    worker_thread = Thread(target=order_processing)
    worker_thread.start()

    app.run(port=4321)

    queue.put(None)
    worker_thread.join()
