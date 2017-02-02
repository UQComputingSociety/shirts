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
colours = ["Black print on white shirt", "White print on black shirt"]
SHIRT_PRICE = 15.0

class Shirt(object):
    def __init__(self, style: str, size: str, colour: str):
        # type:
        self.size = size
        self.style = style
        self.colour = colour

    @classmethod
    def from_json(cls, obj):
        # type: (dict) -> Shirt
        size = obj.get('size')
        style = obj.get('style')
        colour = obj.get('colour')
        return Shirt(size, style, colour)

    def validate(self):
        assert self.size in sizes
        assert self.style in styles
        assert self.colour in colours

    def as_json(self):
        return {
            'size': self.size,
            'style': self.style,
            'colour': self.colour,
        }


class Order(object):
    def __init__(self, first_name: str=None, last_name: str=None, email: str=None, payment_token: str=None, shirts: List[Shirt]=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.shirts = shirts or [] # type: List[Shirt]
        self.payment_token = payment_token
        self.charge_id = None

    @classmethod
    def from_json(cls, obj):
        # type: (dict) -> Order
        first_name = obj.get("first_name").strip()
        last_name = obj.get("last_name").strip()
        email = obj.get('email').strip()
        shirts = [Shirt.from_json(shirt) for shirt in obj.get("shirts", [])]
        payment_token = obj.get("payment_token")

        return Order(first_name, last_name, email, payment_token, shirts)

    def validate(self):
        errors = {}
        for shirt in self.shirts:
            shirt.validate()
        assert len(self.first_name) > 0
        assert len(self.last_name) > 0
        assert len(self.email) > 0

        return errors

    def as_json(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'shirts': [
                self.shirts.as_json()
            ]
        }

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
    if request.method == "POST":
        print(request)
        order_obj = Order()
        res.populate_obj(order_obj)
        queue.put(order_obj)
        with open("out.csv", "a+") as f:
            f.write(order_obj.to_csv() + "\n")
        return redirect('/confirmed', 303)

    return lookup.get_template("order.mako").render(
        form=res,
        errors={},
        values={},
        SHIRT_PRICE=SHIRT_PRICE,
        shirt_sizes=sizes,
        shirt_styles=styles,
        shirt_colours=colours,
    )

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
