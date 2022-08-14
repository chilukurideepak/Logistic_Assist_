import pyrebase
import requests
import json
from kivymd.app import MDApp
import random as r


class account():
    def __init__(self):
        firebaseConfig = {
            "apiKey": "AIzaSyBP1fict95m3IT27qe2jXC4yovr8AW3NxA",
            "authDomain": "logistic-assist-01.firebaseapp.com",
            "projectId": "logistic-assist-01",
            "databaseURL": "https://logistic-assist-01-default-rtdb.firebaseio.com/Company/",
            "storageBucket": ""
        }

        firebase_com = pyrebase.initialize_app(firebaseConfig)

        self.auth = firebase_com.auth()
        self.database = firebase_com.database()

        config_sample = {
            "apiKey": "AIzaSyBP1fict95m3IT27qe2jXC4yovr8AW3NxA",
            "authDomain": "logistic-assist-01.firebaseapp.com",
            "projectId": "logistic-assist-01",
            "databaseURL": "https://logistic-assist-01-default-rtdb.firebaseio.com/carriers/",
            "storageBucket": ""
        }
        carrier_db = pyrebase.initialize_app(config_sample)
        self.carrier_db = carrier_db.database()

    def sign_in(self, email, password):
        app = MDApp.get_running_app()
        try:
            check = self.auth.sign_in_with_email_and_password(email, password)

            localId = check['localId']
            idToken = check['idToken']

            with open("localId.txt", "w") as i:
                i.write(localId)
            with open("idToken.txt", "w") as o:
                o.write(idToken)

            self.refresh_dashboard()



        except:
            logedin_message = "Wrong Credentials"
            app.root.ids["Company_login_screen"].ids["signin_message"].text = logedin_message
            app.root.ids["Company_login_screen"].ids["signin_message"].color = (1, 0, 0, 1)

    def sign_up(self, email, password, con_password):

        if password == con_password:
            app = MDApp.get_running_app()
            # send email &pass to firebase
            # firebase return localid, authtoken, refreshtoken
            signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=AIzaSyBP1fict95m3IT27qe2jXC4yovr8AW3NxA"
            signup_data = {"email": email, "password": password, "returnSecureToken": True}
            sign_up_request = requests.post(signup_url, data=signup_data)
            sign_up_data = json.loads(sign_up_request.content.decode())
            if sign_up_request.ok == True:
                refresh_token = sign_up_data['refreshToken']
                localId = sign_up_data['localId']
                idToken = sign_up_data['idToken']
                # Save refreshToken to a file
                with open("refresh_token.txt", "w") as f:
                    f.write(refresh_token)
                with open("localId.txt", "w") as i:
                    i.write(localId)
                with open("idToken.txt", "w") as o:
                    o.write(idToken)
                # Save localId to a variable in main app class
                # Save idToken to a variable in main app class
                app.local_id = localId
                app.id_token = idToken

                # Create new key in database from localId
                my_data = '{"data": ""}'
                post_request = requests.patch(
                    "https://logistic-assist-01-default-rtdb.firebaseio.com/Company/" + localId + ".json?auth=" + idToken,
                    data=my_data)
                self.emailid = email

                if post_request.ok == True:

                    logedin_message = "Account Successfully created...!!!"
                    app.root.ids["Company_signup_screen"].ids["login_message"].text = logedin_message
                    app.root.ids["Company_signup_screen"].ids["login_message"].color = (0, 1, 0, 1)
                    app.change_screen('Company_details')

            if sign_up_request.ok == False:
                error_data = json.loads(sign_up_request.content.decode())
                error_message = error_data["error"]["message"]
                app.root.ids["Company_signup_screen"].ids["login_message"].text = error_message
                app.root.ids["Company_signup_screen"].ids["login_message"].color = (1, 0, 0, 1)
        else:
            msg = "Please check Password"
            MDApp.get_running_app().root.ids["Company_signup_screen"].ids["login_message"].text = msg
            MDApp.get_running_app().root.ids["Company_signup_screen"].ids["login_message"].color = (1,0,0,1)

    def reset_password(self, email):
        try:
            self.auth.send_password_reset_email(email)
            msg = "             Mail sent..!\nPlease check mail to reset"
            MDApp.get_running_app().root.ids["ResetPassword"].ids["reset_message"].text = msg
            MDApp.get_running_app().root.ids["ResetPassword"].ids["reset_message"].color = (0,1,0,1)
        except:
            msg = "Enter the valid Email"
            MDApp.get_running_app().root.ids["ResetPassword"].ids["reset_message"].text = msg
            MDApp.get_running_app().root.ids["ResetPassword"].ids["reset_message"].color = (1, 0, 0, 1)


    def post_details(self, username, company_name, phone_number):
        app = MDApp.get_running_app()
        with open("localId.txt", 'r') as i:
            localId = i.read()

        d ={"user_name": username, "company_name": company_name, "phone_number": phone_number, "email": self.emailid}
        if phone_number.isdigit():
            self.database.child(localId).child('data').set(d)
            self.refresh_dashboard()
        else:
            details_message = "enter valid number...!"
            app.root.ids["Company_details"].ids["details_message"].text = details_message
            app.root.ids["Company_details"].ids["details_message"].color = (1, 0, 0, 1)


    def post_goods(self,goods_name, from_city, to_city, total_kms, load_weight, start_price):
        app = MDApp.get_running_app()
        with open("localId.txt", 'r') as i:
            localId = i.read()
        try:
            current_post_id = self.database.child(localId).child('all_load_data').get()

            current_post_id = len(current_post_id.val())
        except:
            current_post_id = 1



        if current_post_id == None:
            pass
        elif current_post_id == 1:
            pass
        else:
            current_post_id = current_post_id-1
            self.database.child(localId).child("current_load_data").remove()

            self.database.child(localId).child("all_load_data").child(current_post_id).update({"Status": 'Removed'})

        add_post = self.database.child(localId).child("data").get()
        add_post = add_post.val()["user_name"]

        try:
            all_post = self.database.child(localId).child("all_load_data").get()

            no_of_posts = int(len(all_post.val()))



        except:
            no_of_posts = 1



        no_of_posts = str(no_of_posts)
        Processing = "Processing"
        if goods_name!="":
            if from_city!="":
                if to_city!="":
                    if total_kms!="":
                        if load_weight!="" :
                            if start_price!="":
                                ############################################################################
                                ############################################################################
                                ################       ENTER THE BIDDING CODE HERE      ####################
                                ############################################################################
                                ############################################################################

                                #uploding details in database
                                load_data = {
                                    "Goods_name": goods_name,
                                    "From_city": from_city,
                                    "To_city": to_city,
                                    "Total_kms": total_kms,
                                    "Load_weight": load_weight,
                                    "start_price": start_price,
                                    "Status": Processing,
                                    "Company_ID": localId,
                                    "cur_bid": start_price,
                                    "cur_bid_palced_by": add_post,
                                    "cur_bid_no": ""
                                }
                                self.database.child(localId).child('current_load_data').set(load_data)
                                self.database.child(localId).child('all_load_data').child(no_of_posts).set(load_data)
                                data_1 = {"no_of_post": (int(no_of_posts)+1)}
                                self.database.child(localId).child("data").update(data_1)

                                try:
                                    curent = self.database.child("current").get()
                                    curent = len(curent.val())
                                except:
                                    curent = 1
                                if curent>1:
                                    te = curent
                                    while te>1:
                                        te=te-1
                                        curent_te = self.database.child("current").child(te).get()
                                        curent_te =  curent_te.val()["Company_ID"]
                                        if curent_te == localId:
                                            li_da = {"Status": 'Removed'}
                                            self.database.child("current").child(te).update(li_da)
                                self.database.child("current").child(curent).set(load_data)


                                self.refresh_dashboard()

                        else:
                            add_msg = "Enter weight"
                            app.root.ids["Add_goods"].ids["add_message"].text = add_msg
                    else:
                        add_msg = "Enter Kilometers"
                        app.root.ids["Add_goods"].ids["add_message"].text = add_msg
                else:
                    add_msg = "Enter To City"
                    app.root.ids["Add_goods"].ids["add_message"].text = add_msg
            else:
                add_msg = "Enter the From City"
                app.root.ids["Add_goods"].ids["add_message"].text = add_msg
        else:
            add_msg = "Enter the Goods Name"
            app.root.ids["Add_goods"].ids["add_message"].text = add_msg

    def refresh_dashboard(self):
        app = MDApp.get_running_app()
        with open("localId.txt", 'r') as i:
            localId = i.read()
        try:
            load_data = self.database.child(localId).child('current_load_data').get()

            goods_name = ("Goods : " + load_data.val()["Goods_name"])
            from_city = ("From : " + load_data.val()["From_city"])
            to_city = ("To : " + load_data.val()["To_city"])
            total_kms = ("Kms : " + load_data.val()["Total_kms"])
            load_weight = ("Load Weight : " + load_data.val()["Load_weight"])
            start_price = ("Bid Price : " + load_data.val()["start_price"])
            placed_by = ("Bid By : " + load_data.val()["cur_bid_palced_by"])
            placed_bid = ("Current Bid : " + load_data.val()["cur_bid"])
            text_status = ("Status : "+ load_data.val()["Status"] )
            app.root.ids["Company_dashboard"].ids["current_goods_NA"].color = (120/255,120/255,120/255,0)
            app.root.ids["Company_dashboard"].ids["goods_name"].text = goods_name
            app.root.ids["Company_dashboard"].ids["goods_name"].color = (86/255,55/255,173/255,1)
            app.root.ids["Company_dashboard"].ids["from_city"].text = from_city
            app.root.ids["Company_dashboard"].ids["from_city"].color = (86/255,55/255,173/255,1)
            app.root.ids["Company_dashboard"].ids["to_city"].text = to_city
            app.root.ids["Company_dashboard"].ids["to_city"].color = (86/255,55/255,173/255,1)
            app.root.ids["Company_dashboard"].ids["kms"].text = total_kms
            app.root.ids["Company_dashboard"].ids["kms"].color = (86/255,55/255,173/255,1)
            app.root.ids["Company_dashboard"].ids["load_weight"].text = load_weight
            app.root.ids["Company_dashboard"].ids["load_weight"].color = (86/255,55/255,173/255,1)
            app.root.ids["Company_dashboard"].ids["start_price"].text = start_price
            app.root.ids["Company_dashboard"].ids["start_price"].color = (86/255,55/255,173/255,1)
            app.root.ids["Company_dashboard"].ids["placed_by"].text = placed_by
            app.root.ids["Company_dashboard"].ids["placed_by"].color = (86 / 255, 55 / 255, 173 / 255, 1)
            app.root.ids["Company_dashboard"].ids["placed_bid"].text =placed_bid
            app.root.ids["Company_dashboard"].ids["placed_bid"].color = (86 / 255, 55 / 255, 173 / 255, 1)
            app.root.ids["Company_dashboard"].ids["status"].text = text_status
            app.root.ids["Company_dashboard"].ids["status"].color = (86 / 255, 55 / 255, 173 / 255, 1)
            app.change_screen('Company_dashboard')

        except:
            app.root.ids["Company_dashboard"].ids["current_goods_NA"].color = (120 / 255, 120 / 255, 120 / 255, 1)
            app.root.ids["Company_dashboard"].ids["goods_name"].color = (86 / 255, 55 / 255, 173 / 255, 0)
            app.root.ids["Company_dashboard"].ids["from_city"].color = (86 / 255, 55 / 255, 173 / 255, 0)
            app.root.ids["Company_dashboard"].ids["to_city"].color = (86 / 255, 55 / 255, 173 / 255, 0)
            app.root.ids["Company_dashboard"].ids["kms"].color = (86 / 255, 55 / 255, 173 / 255, 0)
            app.root.ids["Company_dashboard"].ids["load_weight"].color = (86 / 255, 55 / 255, 173 / 255, 0)
            app.root.ids["Company_dashboard"].ids["start_price"].color = (86 / 255, 55 / 255, 173 / 255, 0)
            app.root.ids["Company_dashboard"].ids["placed_by"].color = (86 / 255, 55 / 255, 173 / 255, 0)
            app.root.ids["Company_dashboard"].ids["placed_bid"].color = (86 / 255, 55 / 255, 173 / 255, 0)
            app.root.ids["Company_dashboard"].ids["status"].color = (86 / 255, 55 / 255, 173 / 255, 0)
            app.change_screen('Company_dashboard')


    def delete(self):
        app = MDApp.get_running_app()
        with open("localId.txt", 'r') as i:
            localId = i.read()
        try:
            get_mobile_no = self.database.child(localId).child("current_load_data").get()
            get_mobile_no = get_mobile_no.val()["cur_bid_no"]
            if get_mobile_no != "":
                self.carrier_db.child(get_mobile_no).child("Requests").remove()
        except:
            pass
        ######################################################################
        try:
            all_post = self.database.child(localId).child("all_load_data").get()

            no_of_posts = int(len(all_post.val()))


        except:
            no_of_posts = 0

        if no_of_posts == 0:
            pass
        elif no_of_posts == 1:
            pass
        else:
            self.database.child(localId).child("current_load_data").remove()
            n = no_of_posts-1
            self.database.child(localId).child("all_load_data").child(n).update({"Status": 'Removed'})


        try:
            length_cur = len((self.database.child("current").get()).val())
        except:
            length_cur = 1

        while length_cur >1:
            length_cur = length_cur-1
            q = self.database.child("current").child(length_cur).get()
            if q.val()["Company_ID"] == localId:
                self.database.child("current").child(length_cur).update({"Status": "Removed"})



        #self.database.child("current").child(localId).remove()








        self.refresh_dashboard()



    def end(self):
        with open("localId.txt", 'r') as i:
            localId = i.read()
        app = MDApp.get_running_app()
        #geting data of addd

        my_username = self.database.child(localId).child("data").get()

        my_username = my_username.val()["user_name"]
        try:
            get_data = self.database.child(localId).child("current_load_data").get()
            cur_bid_user = get_data.val()["cur_bid_palced_by"]
        except:
            cur_bid_user = my_username


        if my_username != cur_bid_user :

            bidder_number = get_data.val()["cur_bid_no"]
            set_requests = {
                "com_id": get_data.val()["Company_ID"],
                "Goods_name": get_data.val()["Goods_name"],
                "from_city": get_data.val()["From_city"],
                "to_city": get_data.val()["To_city"],
                "weight": get_data.val()["Load_weight"],
                "cur_bid": get_data.val()["cur_bid"]
            }
            request_Status = {"Status": 'Requested'}
            self.carrier_db.child(bidder_number).child("Requests").set(set_requests)
            self.database.child(localId).child("current_load_data").update(request_Status)
            #change all_data status
            val_cur = self.database.child(localId).child("all_load_data").get()
            val_cur_len = len(val_cur.val())
            while val_cur_len >1:
                val_cur_len = val_cur_len - 1
                ko = self.database.child(localId).child("all_load_data").child(val_cur_len).get()
                ko = ko.val()["Status"]
                if ko == 'Processing':
                    self.database.child(localId).child("all_load_data").child(val_cur_len).update(request_Status)


            #change current status
            val_current = self.database.child("current").get()
            cur_val = len(val_current.val())
            while cur_val > 1:
                cur_val = cur_val-1
                mo = self.database.child("current").child(cur_val).get()
                cu_status = mo.val()["Status"]
                if cu_status == 'Processing':
                    lo = mo.val()["Company_ID"]
                    if lo == localId:
                        self.database.child("current").child(cur_val).update(request_Status)




        else:
            pass


    def profile(self):
        app = MDApp.get_running_app()
        with open("localId.txt", 'r') as i:
            localId = i.read()
        data = self.database.child(localId).child('data').get()
        company_name = data.val()["company_name"]
        user_name = data.val()["user_name"]
        phone_number = data.val()["phone_number"]
        email = data.val()["email"]
        app.root.ids["Company_profile"].ids["username_display"].text = user_name
        app.root.ids["Company_profile"].ids["username_display"].color = (0,0,0,1)

        app.root.ids["Company_profile"].ids["company_display"].text = company_name
        app.root.ids["Company_profile"].ids["company_display"].color = (0,0,0,1)

        app.root.ids["Company_profile"].ids["phone_display"].text = phone_number
        app.root.ids["Company_profile"].ids["phone_display"].color = (0,0,0,1)

        app.root.ids["Company_profile"].ids["email_display"].text = email
        app.root.ids["Company_profile"].ids["email_display"].color = (0,0,0,1)

        app.change_screen("Company_profile")


    def history(self):
        app = MDApp.get_running_app()
        with open("localId.txt", 'r') as i:
            localId = i.read()
        history = self.database.child(localId).child('all_load_data').get()


        list = app.root.ids["Company_transaction_history"]
        if history.val() == None:
            list.ids["5"].text = "No Items"
            list.ids["4"].text = "No Items"
            list.ids["3"].text = "No Items"
            list.ids["2"].text = "No Items"
            list.ids["1"].text = "No Items"
        else:


            no_of_posts = ( len(history.val()) - 1)
            list_no = 5
            while no_of_posts > ((len(history.val())-1)-5):

                if no_of_posts > 0:

                    Goods_name = history.val()[no_of_posts]["Goods_name"]
                    from_city = history.val()[no_of_posts]["From_city"]
                    to_city = history.val()[no_of_posts]["To_city"]
                    ton = history.val()[no_of_posts]["Load_weight"]
                    price = history.val()[no_of_posts]["start_price"]
                    status = history.val()[no_of_posts]["Status"]

                    line2 = ("From: " + from_city + ", To: " + to_city + ", Tons: " + ton)
                    line1 = ("Goods Name: " + Goods_name + ", Price: " + price)
                    line3 = ("Status: " + status)
                    list_str = str(list_no)
                    list.ids[list_str].text = line1
                    list.ids[list_str].secondary_text = line2
                    list.ids[list_str].tertiary_text = line3


                else:
                    list_str = str(list_no)
                    list.ids[list_str].text = ""


                list_no = list_no-1
                no_of_posts = no_of_posts-1

        app.change_screen("Company_transaction_history")
























class otp():

    def send_otp(self, Mobile_number):
        app = MDApp.get_running_app()
        url = 'https://www.fast2sms.com/dev/bulkV2'
        if Mobile_number.isdigit():
            if len(Mobile_number) == 10:

                ran_otp = str(r.randint(1000, 9999))
                message = ("Logistic Assist OTP is "+ran_otp)
                payload = f'variables_values={message}&route=otp&numbers={Mobile_number}'
                headers = {
                    'authorization': "ws1D6A7HXU34yKNbWSLFmuI5fzEkjplcOgQeCxvdPr0TYZM2Vi5qKx2ArblfDJ4EhH1XPjpuIYgSmUde",
                    'Content-Type': "application/x-www-form-urlencoded",
                    'Cache-Control': "no-cache"
                }
                response = requests.request("POST", url, data=payload, headers=headers)

                with open("mobile_number.txt", "w") as i:
                    i.write(Mobile_number)
                app.root.ids["Carrier_otp_verify"].ids["message"].text = 'OTP Successfully Sent'
                app.root.ids["Carrier_otp_verify"].ids["message"].color = (0, 1, 0, 1)
                app.root.ids["Carrier_otp_verify"].ids["real_otp"].text = ran_otp

                app.change_screen('Carrier_otp_verify')

            elif len(Mobile_number) < 10:
                msg = "Enter The Valid Number"
                app.root.ids["Carrier_login_screen"].ids["otp_login"].text = msg
                app.root.ids["Carrier_login_screen"].ids["otp_login"].color = (1, 0, 0, 1)
            elif len(Mobile_number) == None:
                msg = "Enter Number"
                app.root.ids["Carrier_login_screen"].ids["otp_login"].text = msg
                app.root.ids["Carrier_login_screen"].ids["otp_login"].color = (1, 0, 0, 1)
            else:
                msg = "enter only 10 digits"
                app.root.ids["Carrier_login_screen"].ids["otp_login"].text = msg
                app.root.ids["Carrier_login_screen"].ids["otp_login"].color = (1, 0, 0, 1)
        else:
            msg = "only digits!"
            app.root.ids["Carrier_login_screen"].ids["otp_login"].text = msg
            app.root.ids["Carrier_login_screen"].ids["otp_login"].color = (1, 0, 0, 1)

    def verify(self, entered_otp, real_otp):
        firebaseConfig = {
            "apiKey": "AIzaSyBP1fict95m3IT27qe2jXC4yovr8AW3NxA",
            "authDomain": "logistic-assist-01.firebaseapp.com",
            "projectId": "logistic-assist-01",
            "databaseURL": "https://logistic-assist-01-default-rtdb.firebaseio.com/carriers/",
            "storageBucket": ""
        }
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()
        app = MDApp.get_running_app()
        d= {"data":""}
        with open("mobile_number.txt", 'r') as i:
            mobile_number = i.read()
        mobile_number = str(mobile_number)
        if entered_otp == real_otp:
            try:
                x = db.get().val()
                for i in x:
                    if mobile_number == i:
                        member = "yes"
                        break
                    else:
                        member = "no"
            except:
                member = "no"

            if member == "yes":
                self.carrier_dashboard()
            else:
                db.child(mobile_number).set(d)
                app.change_screen('Carrier_details')




        else:
            msg = "Enter valid otp"
            app.root.ids["Carrier_otp_verify"].ids["message"].text = msg
            app.root.ids["Carrier_otp_verify"].ids["message"].color = (1, 0, 0, 1)


    def carrier_post_details(self, user_name, transport_name, truck_type, truck_no):
        firebaseConfig = {
            "apiKey": "AIzaSyBP1fict95m3IT27qe2jXC4yovr8AW3NxA",
            "authDomain": "logistic-assist-01.firebaseapp.com",
            "projectId": "logistic-assist-01",
            "databaseURL": "https://logistic-assist-01-default-rtdb.firebaseio.com/carriers/",
            "storageBucket": ""
        }
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()
        app = MDApp.get_running_app()
        with open("mobile_number.txt", 'r') as i:
            mobile_number = i.read()
        data = {
            "user_name": user_name,
            "transport_name": transport_name,
            "truck_type": truck_type,
            "truck_no": truck_no
        }
        db.child(mobile_number).child("data").set(data)
        self.carrier_dashboard()


    def profile(self):
        firebaseConfig = {
            "apiKey": "AIzaSyBP1fict95m3IT27qe2jXC4yovr8AW3NxA",
            "authDomain": "logistic-assist-01.firebaseapp.com",
            "projectId": "logistic-assist-01",
            "databaseURL": "https://logistic-assist-01-default-rtdb.firebaseio.com/carriers/",
            "storageBucket": ""
        }
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()
        app = MDApp.get_running_app()
        with open("mobile_number.txt", 'r') as i:
            mobile_number = i.read()
        display = app.root.ids["Carrier_profile"]
        data = db.child(mobile_number).child("data").get()
        name = data.val()["user_name"]
        trans = data.val()["transport_name"]
        phone = mobile_number
        truck_type = data.val()["truck_type"]
        truck_no = data.val()["truck_no"]
        display.ids["username_display"].text = name
        display.ids["transport_display"].text = trans
        display.ids["phone_display"].text = phone
        display.ids["truck_type_display"].text = truck_type
        display.ids["truck_no_display"].text = truck_no
        app.change_screen('Carrier_profile')

    def carrier_dashboard(self):
        firebaseConfig = {
            "apiKey": "AIzaSyBP1fict95m3IT27qe2jXC4yovr8AW3NxA",
            "authDomain": "logistic-assist-01.firebaseapp.com",
            "projectId": "logistic-assist-01",
            "databaseURL": "https://logistic-assist-01-default-rtdb.firebaseio.com/",
            "storageBucket": ""
        }
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()
        app = MDApp.get_running_app()
        with open("mobile_number.txt", 'r') as i:
            mobile_number = i.read()

        try:
            request_check = db.child("carriers").child(mobile_number).child("Requests").get()
            request_check = request_check.val()
            print(request_check)
        except:
            request_check = None


        if request_check == None:
            app.root.ids["Carrier_dashboard"].ids["Requests_id"].text = "<No Requests Available>"
            app.root.ids["Carrier_dashboard"].ids["Requests_id"].color = (120/255, 120/255, 120/255, 1)
            app.root.ids["Carrier_dashboard"].ids["Requests_line1"].color = (120 / 255, 120 / 255, 120 / 255, 0)
            app.root.ids["Carrier_dashboard"].ids["accept"].color = (120/255, 120/255, 120/255, 0)
            app.root.ids["Carrier_dashboard"].ids["reject"].color = (120/255, 120/255, 120/255, 0)
            app.root.ids["Carrier_dashboard"].ids["value"].text = 'False'
        else:

            line1_das = ("Load : "+ request_check["Goods_name"]+ "   Rs : "+request_check["cur_bid"])
            line2_das = ("Form : "+request_check["from_city"]+ "   To : "+request_check["to_city"])

            app.root.ids["Carrier_dashboard"].ids["Requests_line1"].text = line1_das
            app.root.ids["Carrier_dashboard"].ids["Requests_line1"].color = (120/255,120/255,120/255, 1)

            app.root.ids["Carrier_dashboard"].ids["Requests_id"].text = line2_das
            app.root.ids["Carrier_dashboard"].ids["Requests_id"].color = (120/255,120/255,120/255, 1)

            app.root.ids["Carrier_dashboard"].ids["accept"].color = (126/255, 6/255, 255/255, 1)
            app.root.ids["Carrier_dashboard"].ids["reject"].color = (126/255, 6/255, 255/255, 1)

            app.root.ids["Carrier_dashboard"].ids["value"].text = 'True'


        try:
            length_cur = db.child("Company").child("current").get()
            length_cur = len(length_cur.val())
        except:
            length_cur = 1

        list_no = 10
        list = app.root.ids["Carrier_dashboard"]
        while length_cur >1:
            length_cur = length_cur-1
            data = db.child("Company").child("current").child(length_cur).get()
            cur_status = data.val()["Status"]
            if cur_status == "Processing":
                comid = data.val()["Company_ID"]
                goods_name = data.val()["Goods_name"]
                from_city = data.val()["From_city"]
                to_city = data.val()["To_city"]
                total_kms = data.val()["Total_kms"]
                load_weight = ("Tons : " + data.val()["Load_weight"])
                start_price = ("Bid Price : " + data.val()["cur_bid"])

                no = str(list_no)
                line1 = ("Goods Name : " + goods_name)
                line2 = ("From : " + from_city + ", To : " + to_city + ", " + load_weight)
                line3 = (start_price)
                list.ids[no].text = line1
                list.ids[no].secondary_text = line2
                list.ids[no].tertiary_text = line3

                list_no=list_no-1
        app.change_screen('Carrier_dashboard')


    #Bidding screen
    def bid(self,id):

        app = MDApp.get_running_app()
        with open("mobile_number.txt", 'r') as i:
            mobile_number = i.read()
        firebaseConfig = {
            "apiKey": "AIzaSyBP1fict95m3IT27qe2jXC4yovr8AW3NxA",
            "authDomain": "logistic-assist-01.firebaseapp.com",
            "projectId": "logistic-assist-01",
            "databaseURL": "https://logistic-assist-01-default-rtdb.firebaseio.com/",
            "storageBucket": ""
        }
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()
        list = app.root.ids["Carrier_dashboard"]

        goods_name = list.ids[id].text
        price = list.ids[id].tertiary_text
        goods_name = goods_name.split(" ")
        price = price.split(" ")
        goods_name = goods_name[::-1]
        price = price[::-1]
        goods_name = goods_name[0]
        price = price[0]



        try:
            length_cur = db.child("Company").child("current").get()
            length_cur = len(length_cur.val())
        except:
            length_cur = 1


        while length_cur > 1:
            length_cur = length_cur - 1
            data = db.child("Company").child("current").child(length_cur).get()
            cur_status = data.val()["Status"]
            cur_goods = data.val()["Goods_name"]
            cur_price = data.val()["cur_bid"]
            if cur_status == "Processing":
                if cur_goods == goods_name:
                    if cur_price == price:
                        company_id = data.val()["Company_ID"]
                        com_name = db.child("Company").child(company_id).child("data").get()
                        com_name = com_name.val()["company_name"]
                        b_name = data.val()["Goods_name"]
                        b_name = ("Good Name : "+ b_name)
                        b_from = data.val()["From_city"]
                        b_from = ("From : "+ b_from)
                        b_to = data.val()["To_city"]
                        b_to = ("To : "+b_to)
                        b_tons = data.val()["Load_weight"]
                        b_tons = ("Load Weight : "+ b_tons)
                        start_price = data.val()["start_price"]
                        start_price = ("Start Bid Price : "+start_price)
                        cur_price = data.val()["cur_bid"]

                        app.root.ids["Bidding"].ids['com_name'].text = com_name
                        app.root.ids["Bidding"].ids['bid_name'].text = b_name
                        app.root.ids["Bidding"].ids["b_from"].text = b_from
                        app.root.ids["Bidding"].ids["b_to"].text = b_to
                        app.root.ids["Bidding"].ids["b_tons"].text = b_tons
                        app.root.ids["Bidding"].ids["b_com_id"].text = company_id
                        app.root.ids["Bidding"].ids["start_price"].text = start_price
                        app.root.ids["Bidding"].ids["cur_bid"].text = cur_price

                        app.change_screen('Bidding')



    def place_bid(self,com_id, bid_price, bid_name, price_a):
        app = MDApp.get_running_app()
        with open("mobile_number.txt", 'r') as i:
            mobile_number = i.read()
        firebaseConfig = {
            "apiKey": "AIzaSyBP1fict95m3IT27qe2jXC4yovr8AW3NxA",
            "authDomain": "logistic-assist-01.firebaseapp.com",
            "projectId": "logistic-assist-01",
            "databaseURL": "https://logistic-assist-01-default-rtdb.firebaseio.com/",
            "storageBucket": ""
        }
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()

        current_bid_price = db.child("Company").child(com_id).child("current_load_data").get()

        current_bid_price = current_bid_price.val()["cur_bid"]
        user_data = db.child("carriers").child(mobile_number).child("data").get()
        user_data = user_data.val()["user_name"]

        #checking bid placing value is less than current bid value are not
        if bid_price < current_bid_price:
            cur_bid_data = {"cur_bid": bid_price}
            cur_post_data = {"cur_bid_palced_by": user_data}
            cur_bid_no = {"cur_bid_no": mobile_number}
            #sending bid value to database
            db.child("Company").child(com_id).child("current_load_data").update(cur_bid_data)
            db.child("Company").child(com_id).child("current_load_data").update(cur_post_data)
            db.child("Company").child(com_id).child("current_load_data").update(cur_bid_no)
            data_current = db.child("Company").child("current").get()
            lene = len(data_current.val())
            while (lene)>1:
                lene = lene-1
                check = db.child("Company").child("current").child(lene).get()
                check_id = check.val()["Company_ID"]
                check_status = check.val()["Status"]
                if check_id == com_id:
                    if check_status == 'Processing':
                        db.child("Company").child("current").child(lene).update(cur_bid_data)
                        db.child("Company").child("current").child(lene).update(cur_post_data)
                        db.child("Company").child("current").child(lene).update(cur_bid_no)
            le1 = db.child("Company").child(com_id).child("all_load_data").get()

            le = len(le1.val())

            while le > 1:
                le = le-1
                le_data = db.child("Company").child(com_id).child("all_load_data").child(le).get()
                le_data = le_data.val()["Status"]
                if le_data == 'Processing':
                    db.child("Company").child(com_id).child("all_load_data").child(le).update(cur_bid_data)
                    db.child("Company").child(com_id).child("all_load_data").child(le).update(cur_post_data)
                    db.child("Company").child(com_id).child("all_load_data").child(le).update(cur_bid_no)


            self.carrier_dashboard()

    def accept(self, value):
        app = MDApp.get_running_app()
        with open("mobile_number.txt", 'r') as i:
            mobile_number = i.read()
        firebaseConfig = {
            "apiKey": "AIzaSyBP1fict95m3IT27qe2jXC4yovr8AW3NxA",
            "authDomain": "logistic-assist-01.firebaseapp.com",
            "projectId": "logistic-assist-01",
            "databaseURL": "https://logistic-assist-01-default-rtdb.firebaseio.com/",
            "storageBucket": ""
        }
        firebase = pyrebase.initialize_app(firebaseConfig)
        db = firebase.database()

        #checking value request presence
        if value == 'True':

            #get current request details
            get_request_data = db.child("carriers").child(mobile_number).child("Requests").get()
            get_request_data = get_request_data.val()
            print(get_request_data)

        else:
            pass

    def reject(self):
        pass