**********
$ ${ "{:.2f}".format(user.total_transaction_price) }
**********

-----------------------
2018 UQCS T-Shirt Pre-order
-----------------------

${user.first_name} ${user.last_name}

${str(dt.datetime.now().replace(microsecond=0).isoformat())}

% for shirt in user.shirts:
${shirt.style} ${shirt.size} UQCS T-shirt ((${shirt.text_colour}))
$ ${ shirt_price }

% endfor

Online Payment Fee
$ ${ "{:.2f}".format(user.payment_fee) }

Total
$ ${ "{:.2f}".format(user.total_transaction_price) }

UQ Computing Society

Level 2 Union Building,

University of Queensland, 4067

Questions? Email contact@uqcs.org.au