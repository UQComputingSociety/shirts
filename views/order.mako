<!DOCTYPE html>
<html>
<head>
<title>UQCS Shirts 2017</title>
<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">

<!-- Optional theme -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css" integrity="sha384-fLW2N01lMqjakBkx3l/M9EahuwpSfeNvV63J5ezn3uZzapT0u7EYsXMjQV+0En5r" crossorigin="anonymous">

<link rel="stylesheet" href="/static/style.css">

</head>
<body>
<div class="container">
  <div class="row">
    <div class="col-md-12">
      <h1>UQCS Shirt Preorders</h1>
      <p>Another year has come, and with it another round of UQCS shirt preorders!</p>
      <p>Shirts cost $20 each, with a 30c online payment fee, plus 35c per shirt.</p>
    </div>
  </div>
  <div class="row">
    <div class="col-md-7">
      <form method="POST" id="form" action="." name="form">
        <div class="form-group">
          ${form.first_name.label}
          ${form.first_name(class_="form-control")}
        </div>
        % for error in form.first_name.errors:
        <p class="alert alert-danger">${error}</p>
        % endfor
        <div class="form-group">
          ${form.last_name.label}
          ${form.last_name(class_="form-control")}
        </div>
        % for error in form.last_name.errors:
        <p class="alert alert-danger">${error}</p>
        % endfor
        <div class="form-group">
          ${form.email.label}
          ${form.email(class_="form-control")}
        </div>
        % for error in form.email.errors:
        <p class="alert alert-danger">${error}</p>
        % endfor
        % for shirtform in form.shirts:
        <div class="form-group">
          ${shirtform.shirt_style.label}
          % for sub in shirtform.shirt_style:
          <div class="radio">
            ${sub} ${sub.label}
          </div>
          % endfor
        </div>
        %for error in shirtform.shirt_style.errors:
        <p class="alert alert-danger">${error}</p>
        %endfor
        <div class="form-group">
          ${shirtform.shirt_size.label}
          % for sub in shirtform.shirt_size:
          <div class="radio">
            ${sub} ${sub.label}
          </div>
          % endfor
          <span class="help-block">Note: Women's sizes only go up to 2XL</span>
        </div>
        %for error in shirtform.shirt_size.errors:
        <p class="alert alert-danger">${error}</p>
        %endfor
            %endfor
        <div class='form-group'>
          <label>Cardholder Name</label>
          <input class='form-control' type='text' data-stripe="name">
        </div>
        <div class='form-group'>
          <label>Card Number</label>
          <input class='form-control' size='20' type='text' data-stripe="number">
        </div>
        <div class='form-group row'>
          <div class='col-xs-4 form-group cvc required'>
            <label class='control-label'>CVC</label>
            <input class='form-control' placeholder='ex. 311' size='4' type='text' data-stripe="cvc">
          </div>
          <div class='col-xs-4 form-group expiration required'>
            <label class='control-label'>Expiration</label>
            <input class='form-control card-expiry-month' placeholder='MM' size='2' type='text' data-stripe="exp_month">
          </div>
          <div class='col-xs-4 form-group expiration required'>
            <label class='control-label'> </label>
            <input class='form-control' placeholder='YY' size='2' type='text' data-stripe="exp_year">
          </div>
        </div>
        <div id="payment_errors">
        %for error in form.payment_token.errors:
        <p class="alert alert-danger">${error}</p>
        %endfor
        </div>
        ${form.payment_token}
        <input class="btn btn-primary submit" name="submit" type="submit" id="payonline_submit" value="Pay Online">
      </form>
    </div>
    <div class="col-md-5">
      <div class="row">
        <div class="col-md-12">
          <h3>Shirt Mockup</h3>
          <p>Note: While the mockup is blue, the final shirts will be black.</p>
          <img src="/static/mockup.jpg" class="mockup" />
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
Stripe.setPublishableKey('pk_live_Nsovfda3IOO0YXlDEOr1bOjb');
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
          $form.find("#payment_errors").append('<p class="alert alert-danger">'.concat(resp.error.message).concat("</p>"));
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
});

</script>

</body>
</html>
