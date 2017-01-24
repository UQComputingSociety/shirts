from typing import List

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
import sanic

stripe.api_key = os.environ.get("STRIPE_API_KEY")
lookup = TemplateLookup(["views", "emails"], input_encoding='utf-8')
queue = Queue()
app = Flask(__name__)
sizes = ["XS", "S", "M", "L", "XL", "2XL", "3XL"]
styles = ["Men's", "Women's"]
SHIRT_PRICE = 20.0

class Shirt(object):
    def __init__(self, shirt_style, shirt_size):
        # type:
        self.shirt_size = shirt_size
        self.shirt_style = shirt_style

class Order(object):
    def __init__(self, first_name: str=None, last_name: str=None, email: str=None, payment_token: str=None, shirts: List[Shirt]=[]):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.shirts = shirts
        self.payment_token = payment_token
        self.charge_id = None

    @property
    def total_transaction_price(self):
        return SHIRT_PRICE * len(self.shirts)

    @property
    def payment_fee(self):
        return 0.0175 * self.total_transaction_price + 0.30

    def to_csv(self):
        return "\n".join([
            ",".join(map(str,[
                self.first_name,
                self.last_name,
                self.email,
                shirt.shirt_size,
                shirt.shirt_style,
                self.payment_token
            ]))
            for shirt in self.shirts
        ])

    def send_email(self):
        template_data = {
            'user': self,
            'dt': dt,
            'shirt_price': SHIRT_PRICE,
        }

        receiptText = lookup.get_template("text.mako") \
            .render(**template_data)
        receiptHTML = lookup.get_template('html.mako') \
            .render(**template_data)
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

class ShirtForm(form.Form):
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


class OrderForm(form.Form):
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
    shirts = fields.FieldList(fields.FormField(ShirtForm), min_entries=1)
    payment_token = fields.HiddenField()

    def validate_payment_token(form, field):
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


@app.route("/", methods=["GET", "POST"])
def form():
    
    res = OrderForm(request.form)
    if request.method == "POST" and res.validate():
        print(request)
        order_obj = Order()
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

    app.run(host='0.0.0.0', port=4321, threaded=True)

    queue.put(None)
    worker_thread.join()
