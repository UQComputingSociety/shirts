<!DOCTYPE html>
<html>
<head>
<title>UQCS Shirts 2017</title>
<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">

<!-- Optional theme -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css" integrity="sha384-fLW2N01lMqjakBkx3l/M9EahuwpSfeNvV63J5ezn3uZzapT0u7EYsXMjQV+0En5r" crossorigin="anonymous">
<link rel="stylesheet" href="/static/style.css">
<script id="initial_json">
    ${values}
</script>
<script type="text/javascript">
    INITIAL_JSON = JSON.parse(document.getElementById("initial_json").innerHTML);
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/knockout/3.4.1/knockout-min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.4/lodash.min.js"></script>
</head>
<body>
<div class="container">
  <div class="row">
    <div class="col-md-7">
        <h1>UQCS Shirt Preorders</h1>
        <p>Another year has come, and with it another round of UQCS shirt preorders!</p>
        <p>Shirts cost $${"{:2.2f}".format(SHIRT_PRICE)} each, with an online payment fee of 30c plus ${int(SHIRT_PRICE * 0.0175 * 100)}c per shirt.</p>
        <div id="errors">
          % for category, message in get_flashed_messages(True, ['danger', 'warning', 'success']):
            <p class="alert alert-${category}">${message}</p>
          % endfor
        </div>
      <form method="POST" id="form" action="." name="form">
          <input type="hidden" name="json" data-bind="value: asJSON">
        <div class="form-group">
            <label>First Name</label>
            <input type="text" data-bind="value: firstName" class="form-control" placeholder="First Name" name="first_name" required="true">
        </div>
        <div class="form-group">
            <label>Last Name</label>
            <input type="text" data-bind="value: lastName" class="form-control" placeholder="Last Name" name="last_name" required="true">
        </div>
        <div class="form-group">
          <label>Email</label>
          <input type="email" data-bind="value: email" class="form-control" placeholder="Email" name="email" required="true">
        </div>
        <hr />
          <div style="float: right" data-bind="click: newShirt">
            <button type="button" class="btn btn-success">
              <span class="glyphicon glyphicon-plus" aria-hidden="true"></span>
            </button>
          </div>
          <h3>Shirts</h3>
        <!-- ko foreach: shirts -->
          <div style="float: right" data-bind="click: removeShirt">
            <button type="button" class="btn btn-danger">
              <span class="glyphicon glyphicon-minus" aria-hidden="true"></span>
            </button>
          </div>
        <div class="form-group">
          <label>Shirt Style</label>
          % for idx, style in enumerate(shirt_styles):
          <div class="radio">
            <label class=".radio-inline">
              <input type="radio" value="${style}" data-bind="checked: style">
              ${style}
            </label>
          </div>
          % endfor
        </div>
        <div class="form-group">
          <label>Shirt Size</label>
          <div>
          % for idx, size in enumerate(shirt_sizes):
            <div class="radio" style="display: inline-block">
              <label>
                <input type="radio" value="${size}" data-bind="checked: size">
                ${size}
              </label>
            </div>
          % endfor
          </div>
          <span class="help-block">Note: Women's sizes only go up to 2XL</span>
        </div>
        <div class="form-group">
          <label>Shirt Colours</label>
          % for idx, colour in enumerate(shirt_colours):
            <div class="radio">
              <label>
                <input type="radio" value="${colour}" data-bind="checked: colour">
                  ${colour}
              </label>
            </div>
          % endfor
          <hr/>
        </div>
        <!-- /ko -->
        <div class='form-group'>
          <label>Cardholder Name</label>
          <input class='form-control' type='text' data-stripe="name" required>
        </div>
        <div class='form-group'>
          <label>Card Number</label>
          <input class='form-control' size='20' type='text' data-stripe="number" required>
        </div>
        <div class='form-group row'>
          <div class='col-xs-4 form-group cvc required'>
            <label class='control-label'>CVC</label>
            <input class='form-control' placeholder='ex. 311' size='4' type='text' data-stripe="cvc" required>
          </div>
          <div class='col-xs-4 form-group expiration required'>
            <label class='control-label'>Expiration</label>
            <input class='form-control card-expiry-month' placeholder='MM' size='2' type='text' data-stripe="exp_month" required>
          </div>
          <div class='col-xs-4 form-group expiration required'>
            <label class='control-label'> </label>
            <input class='form-control' placeholder='YY' size='2' type='text' data-stripe="exp_year" required>
          </div>
        </div>
        <div id="payment_errors">
        </div>
        <input id="payment_token" name="payment_token" type="hidden" data-bind="value: paymentToken">
        <input class="btn btn-primary submit" name="submit" type="submit" id="payonline_submit" data-bind="value: submitText">
      </form>
    </div>
    <div class="col-md-5">
      <div class="row">
        <div class="col-md-12">
          <h3>Shirt Design</h3>
          <p>Note: Shirts are available with both a black print on a white shirt, or white print on a black shirt</p>\
        </div>
        <div class="col-md-12">
          <img src="/static/mockup-white.png" class="mockup" />
        </div>

        <div class="col-md-12">
          <img src="/static/mockup-black.png" class="mockup" />
        </div>
      </div>
      <div class="row">
        <div class="col-md-12">
          <h3>Men's sizing table</h3>
          <table class="table table-bordered">
          <tr>
          <th scope="col" >SIZE</th>
          <th scope="col" >XS</th>
          <th scope="col" >S</th>
          <th scope="col" >M</th>
          <th scope="col" >L</th>
          <th scope="col" >XL</th>
          <th scope="col" >2XL</th>
          <th scope="col" >3XL</th>
          </tr>
          <tr>
          <td>Half Chest (cm)</td>
          <td>47</td>
          <td>50</td>
          <td>53</td>
          <td>56</td>
          <td>59</td>
          <td>62</td>
          <td>65</td>
          </tr>
          <tr>
          <td>Body Length (cm)</td>
          <td>67</td>
          <td>70</td>
          <td>72</td>
          <td>74</td>
          <td>76</td>
          <td>78</td>
          <td>80</td>
          </tr>

          </table>
        </div>
        <div class="col-md-12">
        <h3>Women's sizing table</h3>
        <table class="table table-bordered">
          <tr>
            <th scope="col">SIZE</th>
            <th scope="col">XS/6</th>
            <th scope="col">S/8</th>
            <th scope="col">M/10</th>
            <th scope="col">L/12</th>
            <th scope="col">XL/14</th>
            <th scope="col">2XL/16</th>
          </tr>
          <tr>
            <td>Half Chest (cm)</td>
            <td>41</td>
            <td>43</td>
            <td>46</td>
            <td>49</td>
            <td>53</td>
            <td>57</td>
          </tr>
          <tr>
            <td>Body Length (cm)</td>
            <td>59</td>
            <td>61</td>
            <td>63</td>
            <td>65</td>
            <td>67</td>
            <td>69</td>
          </tr>
        </table>

        </div>
      </div>
    </div>
  </div>
</div>
<!-- Latest compiled and minified JavaScript -->
<script src="https://code.jquery.com/jquery-2.2.4.min.js" type="text/javascript"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js" integrity="sha384-0mSbJDEHialfmuBBQP6A4Qrprq5OVfW37PRR3j5ELqxss1yVqOtnepnHVP9aJ7xS" crossorigin="anonymous"></script>
<script type="text/javascript" src="https://js.stripe.com/v2/"></script>
<script type="text/javascript">
Stripe.setPublishableKey('${stripe_public_key}');
DAT_GLOBAL_STATE_THO = false;
$(function() {
  var $form = $('#form');
  $form.on('submit', function(event) {
    // Disable the submit button to prevent repeated clicks:
    $form.find('.submit').prop('disabled', true);

    // Request a token from Stripe:
    if (!DAT_GLOBAL_STATE_THO){
      Stripe.card.createToken($form, function(status, resp){
        console.log(resp);
        if (status != 200){
          $form.find('.submit').prop('disabled', false);
          $("#errors").append('<p class="alert alert-danger">'.concat(resp.error.message).concat("</p>"));
          return;
        }
        $form.find("[name=payment_token]").val(resp.id);
        DAT_GLOBAL_STATE_THO = true;
        $form.unbind();
        $form.find('.submit').prop('disabled', false);
        document.form.submit.click();
      });
    }
    return DAT_GLOBAL_STATE_THO;
  });
})
</script>
<script src="/static/shirts.js" type="text/javascript"></script>

</body>
</html>
