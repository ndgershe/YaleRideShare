let form = document.getElementById("register");
            form.onsubmit = function()  {

                if (!form.username.value)
                {
                    alert("must provide username");
                    return false;
                }
                else if (!form.name.value)
                {
                    alert("must provide first name");
                    return false;
                }
                else if (!form.surname.value)
                {
                    alert("must provide last name");
                    return false;
                }
                else if (!form.email.value)
                {
                    alert("must provide email address");
                    return false;
                }
                else if (!form.password.value)
                {
                    alert("must provide password");
                    return false;
                }
                else if (form.confirmation.value != form.password.value)
                {
                    alert("passwords must match");
                    return false;
                }
                else if (!form.phone.value)
                {
                    alert("must provide phone number");
                    return false;
                }
            }