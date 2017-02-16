from typing import List, Dict, Optional
from flask import Flask, request, redirect, flash, get_flashed_messages
from queue import Queue
from threading import Thread
import datetime as dt
import premailer
import requests
import os
import json
import stripe
import random
from .templates import lookup

stripe.api_key = os.environ.get("STRIPE_API_KEY")
app = Flask(__name__)
app.secret_key = random.SystemRandom().getrandbits(20)
sizes = ["XS", "S", "M", "L", "XL", "2XL", "3XL"]
styles = ["Men's", "Women's"]
colours = [
    "Black print on white shirt",
    "White print on black shirt",
    "White (logo pocket print only) on black shirt",
    "Black (logo pocket print only) on white shirt"
]
SHIRT_PRICE = 15.0
queue = Queue()  # type: Queue

class Shirt(object):
    def __init__(self, style: str, size: str, colour: str) -> None:
        self.size = size
        self.style = style
        self.colour = colour

    @classmethod
    def from_json(cls, obj: dict) -> 'Shirt':
        size = obj.get('size')
        style = obj.get('style')
        colour = obj.get('colour')
        return Shirt(size=size, style=style, colour=colour)

    def validate(self) -> bool:
        result = True
        if self.size not in sizes:
            flash("Invalid shirt size entered", "danger")
            result = False
        if self.style not in styles:
            flash("Invalid shirt style entered", "danger")
            result = False
        if self.colour not in colours:
            flash("Invalid shirt colour entered", "danger")
            result = False
        return result

    def as_json(self) -> Dict[str, str]:
        return {
            'size': self.size,
            'style': self.style,
            'colour': self.colour,
        }

    @property
    def text_colour(self) -> str:
        result = self.colour.split()[-2].strip() + " shirt"
        if "logo" in self.colour:
            result += " logo only"
        return result


class Order(object):
    def __init__(self, first_name: str=None, last_name: str=None, email: str=None, payment_token: str=None, shirts: List[Shirt]=None) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.shirts = shirts or [] # type: List[Shirt]
        self.payment_token = payment_token
        self.charge_id = None # type: Optional[str]

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
        result = True
        if len(self.first_name) == 0:
            flash("No first name entered", "danger")
            result = False
        if len(self.last_name) == 0:
            flash("No last name entered", "danger")
            result = False
        if len(self.email) == 0:
            flash("No email entered", 'danger')
            result = False
        if len(self.shirts) == 0:
            flash("No shirts ordered", "danger")
            result = False

        for shirt in self.shirts:
            result = result and shirt.validate()
        if result:
            try:
                charge = stripe.Charge.create(
                    amount=int(self.total_transaction_price * 100), # amount in cents, again
                    currency="aud",
                    source=self.payment_token,
                    description="UQCS Shirt Preorder"
                )
                self.charge_id = charge['id']
            except stripe.error.CardError as e:
                flash("Card declined", "danger")
                result = False
            except stripe.error.InvalidRequestError as e:
                flash("Something went wrong when processing your payment ({})".format(e), "danger")
                result = False
        return result

    def as_json(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'shirts': [
                shirt.as_json() for shirt in self.shirts
            ]
        }

    @property
    def total_transaction_price(self):
        return self.shirts_price + self.payment_fee

    @property
    def shirts_price(self):
        return SHIRT_PRICE * len(self.shirts)

    @property
    def payment_fee(self):
        return (0.0175 * SHIRT_PRICE) * len(self.shirts) + 0.30

    def to_csv(self):
        return "\n".join([
            ",".join(map(str,[
                self.first_name,
                self.last_name,
                self.email,
                shirt.size,
                shirt.style,
                shirt.colour,
                self.charge_id
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

    def notify_slack(self):
        plural = 's' if len(self.shirts) != 1 else ''
        message = "\n".join([
            "Order for {n} shirt{plural} by {s.first_name} {s.last_name} ({s.email})".format(s=self, n=len(self.shirts), plural=plural)
        ] + [
            "\t {sh.style} {sh.size} ({sh.colour})".format(sh=shirt)
            for shirt in self.shirts
        ])
        requests.post(os.environ.get("SLACK_HOOK_URL"), data={
            'payload': json.dumps({
                'text': message
            })
        })

@app.route("/", methods=["GET", "POST"])
def form():
    form_data = request.form.get('json')
    values = {}
    if request.method == "POST" and form_data:
        cont = True
        try:
            data = json.loads(form_data)
        except ValueError:
            flash("Internal server error - could not decode JSON", "danger")
            cont = False
        if cont:
            order_obj = Order.from_json(data)
            order_obj.payment_token = request.form.get('payment_token', order_obj.payment_token)
            values = order_obj.as_json()
            cont = order_obj.validate()
        if cont:
            queue.put(order_obj)
            with open("out.csv", "a+") as f:
                f.write(order_obj.to_csv() + "\n")
            return redirect('/confirmed', 303)

    return lookup.get_template("order.mako").render(
        errors={},
        values=values,
        SHIRT_PRICE=SHIRT_PRICE,
        shirt_sizes=sizes,
        shirt_styles=styles,
        shirt_colours=colours,
        get_flashed_messages=get_flashed_messages,
        stripe_public_key=os.environ.get("STRIPE_PUBLIC_KEY", 'pk_test_D7aaK6LbIHvw56Dp5qgr74hG')
    )

@app.route("/confirmed")
def confirmed():
    return lookup.get_template("confirmed.mako").render()


def order_processing():
    for order in iter(queue.get, None):
        order.send_email()
        order.notify_slack()


def main():
    worker_thread = Thread(target=order_processing)
    worker_thread.start()

    app.run(host='0.0.0.0', port=4321, threaded=True)

    queue.put(None)
    worker_thread.join()
