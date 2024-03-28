import ast
import pickle
from datetime import datetime, timedelta

import numpy as np
# from django.http import JsonResponse
import psycopg2
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from twilio.rest import Client

from .models import CustomUser, Doctor_Auth, AshaWorker_Auth


# twilio recovery code "2EY9E9T8BU3596PR97PZCZSE"


# postgres database connection
def build_connection_with_database():
    conn = psycopg2.connect(database="telemedapp", host="localhost", port="5432", user="postgres",
                            password="Pukale@123")
    return conn


def close_connection_with_database(cur, conn):
    conn.commit()
    cur.close()
    conn.close()


def registration(request):
    if request.method == 'POST':
        if request.POST.get('userType') == 'Doctor':
            docName = request.POST.get('name')
            registrationNo = request.POST.get('regNo')  # using regNo as password
            cityVillage = request.POST.get('cityVillage')
            taluka = request.POST.get('taluka')
            state = request.POST.get('state')
            phone = request.POST.get('phone')
            # print(docName, registrationNo, cityVillage, taluka, state, phone)
            if Doctor_Auth.objects.filter(name=docName, reg_no=registrationNo):  # checking if doctor is valid
                if not User.objects.filter(username=docName).exists():  # checking if already registered
                    # create a user object
                    user = User(username=docName)
                    user.set_password(raw_password=registrationNo)
                    user.save()
                    # create a customuser object associated with user
                    custom_user = CustomUser.objects.create(user=user, city=cityVillage, taluka=taluka,
                                                            state=state, phone=phone)
                    # put the doctor data into doctor -- postgres
                    conn = build_connection_with_database()
                    cur = conn.cursor()
                    cur.execute(
                        f"INSERT INTO doctor(name, city, taluka, state, phone) VALUES ('{docName}', '{cityVillage}', '{taluka}', '{state}', '{phone}')")
                    close_connection_with_database(cur, conn)
                    messages.info(request, 'Doctor Registered Successfully')
                    return redirect('login_user')
                else:
                    messages.info(request, 'Doctor Already Registered')
                    return redirect('login_user')
            else:
                messages.info(request, 'Doctor is Not Valid')
                return redirect('registration')
        elif request.POST.get('userType') == 'User':
            name = request.POST.get('name')
            cityVillage = request.POST.get('cityVillage')
            taluka = request.POST.get('taluka')
            state = request.POST.get('state')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            # cycle_length = request.POST.get('cycle_length')
            # period_length = request.POST.get('period_length')
            if not User.objects.filter(username=name).exists():  # checking is user exists
                user = User(username=name)
                user.set_password(raw_password=password)
                user.save()
                custom_user = CustomUser.objects.create(user=user, city=cityVillage, taluka=taluka,
                                                        state=state, phone=phone)
                # put users data into patient -- postgres
                conn = build_connection_with_database()
                cur = conn.cursor()
                cur.execute(
                    f"INSERT INTO patient(name, city, taluka, state, phone, period_start) VALUES ('{name}', '{cityVillage}', '{taluka}', '{state}', '{phone}', 'none')")
                close_connection_with_database(cur, conn)
                messages.info(request, 'User Registered Successfully')
                return redirect('login_user')
            else:
                messages.info(request, 'Username Already Exist')
                return redirect(request, 'login_user')
        elif request.POST.get('userType') == 'Asha Worker':
            name = request.POST.get('name')
            cityVillage = request.POST.get('cityVillage')
            taluka = request.POST.get('taluka')
            state = request.POST.get('state')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            link = request.POST.get('link')
            # print(name, cityVillage, taluka, state, phone, password, link)
            if AshaWorker_Auth.objects.filter(name=name, id_no=password):  # checking if ashaworker is valid
                if not User.objects.filter(username=name).exists():  # checking if already registered
                    # create a user object
                    user = User(username=name)
                    user.set_password(raw_password=password)
                    user.save()
                    # create a customuser object associated with user
                    custom_user = CustomUser.objects.create(user=user, city=cityVillage, taluka=taluka,
                                                            state=state, phone=phone)
                    # put the doctor data into doctor -- postgres
                    conn = build_connection_with_database()
                    cur = conn.cursor()
                    cur.execute(
                        f"INSERT INTO ashaworker(name, city, taluka, state, phone, link) VALUES ('{name}', '{cityVillage}', '{taluka}', '{state}', '{phone}', '{link}')")
                    close_connection_with_database(cur, conn)
                    messages.info(request, 'AshaWorker Registered Successfully')
                    return redirect('login_user')
                else:
                    messages.info(request, 'AshaWorker Already Registered')
                    return redirect('login_user')
            else:
                messages.info(request, 'AshaWorker is Not Valid')
                return redirect('registration')
    return render(request, 'registration.html')


def login_user(request):
    if request.method == 'POST':
        userType = request.POST.get('userType')
        if userType == 'Doctor':
            name = request.POST.get('name')
            password = request.POST.get('regNo')
            user = authenticate(username=name, password=password)
            if user:
                login(request, user=user)
                messages.info(request, 'logged in successfully')
                return redirect('doctor_dashboard')
            else:
                messages.info(request, 'Doctor not Registered')
                return redirect('login_user')
        elif userType == 'User':
            name = request.POST.get('name')
            password = request.POST.get('password')
            user = authenticate(username=name, password=password)
            if user:
                login(request, user=user)
                messages.info(request, 'logged in successfully')
                return redirect('user_dashboard')
            else:
                messages.info(request, 'User not Registered')
                return redirect('registration')
        elif userType == 'Asha Worker':
            name = request.POST.get('name')
            password = request.POST.get('idNo')
            user = authenticate(username=name, password=password)
            if user is not None:
                login(request, user=user)
                messages.info(request, 'logged in successfully')
                return redirect('ashaworker_dashboard')
            else:
                messages.info(request, 'AshaWorker not Registered')
                return redirect('login_user')
    return render(request, 'login_user.html')


def logout_user(request):
    logout(request)
    return redirect('login_user')


@login_required
def user_dashboard(request):
    current_user = request.user
    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT city FROM patient WHERE name = '{current_user}'")
    current_user_city = cur.fetchone()
    cur.execute(f"SELECT * FROM ashaworker WHERE city = '{current_user_city[0]}'")
    data = cur.fetchall()

    # Example Dates

    # today = datetime.now().date()
    # period_start = today
    # dates = menstrual_cycle(period_start)
    # current_year = datetime.now().year
    context = {
        'data': data,
        'current_user': current_user
        # 'dates_json': dates,
        # 'current_year': current_year
    }
    return render(request, 'user_dashboard.html', context=context)


@login_required
def mc_tracking(request):
    patient = request.user
    if request.method == 'POST':
        reset = request.POST.get('reset')
        if reset == "reset":
            conn = build_connection_with_database()
            cur = conn.cursor()
            cur.execute(f"UPDATE patient SET period_start = '{datetime.now().date()}' WHERE name = '{patient}'")
            cur.execute(f"SELECT period_length FROM patient WHERE name = '{patient}'")
            period_length = cur.fetchone()[0]
            cur.execute(
                f"INSERT INTO period(period_start, period_end, name) VALUES ('{datetime.now().date()}', '{datetime.now().date() + timedelta(days=int(period_length) - 1)}', '{patient}')")
            close_connection_with_database(cur, conn)
        else:
            new_mcl = int(request.POST.get('mcl'))
            new_pl = int(request.POST.get('pl'))
            new_ps = request.POST.get('ps')
            new_ps = datetime.strptime(new_ps, "%Y-%m-%d").date()
            conn = build_connection_with_database()
            cur = conn.cursor()
            cur.execute(
                f"UPDATE patient SET period_length = '{new_pl}', menstrual_cycle_length = '{new_mcl}', period_start = '{new_ps}' WHERE name = '{patient}'")
            cur.execute(
                f"INSERT INTO period(period_start, period_end, name) VALUES ('{new_ps}', '{new_ps + timedelta(days=new_pl - 1)}', '{patient}')")
            close_connection_with_database(cur, conn)

    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM patient WHERE name = '{patient}'")
    data = cur.fetchone()
    menstrual_cycle_length = data[5]
    period_length = data[6]
    period_start = data[7]
    # print(menstrual_cycle_length, period_length, period_start)
    # print(period_start + "s")
    dates = None
    # print(period_start)
    if period_start != 'none':
        period_start = datetime.strptime(period_start, "%Y-%m-%d").date()
        period_start = period_start - timedelta(days=1)
        dates = menstrual_cycle(period_start, int(period_length), int(menstrual_cycle_length))
    current_year = datetime.now().year
    context = {
        'dates_json': dates,
        'current_year': current_year
    }
    return render(request, 'mc_tracking.html', context=context)


@login_required
def period_history(request):
    patient = request.user
    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM period WHERE name = '{patient}' ORDER BY period_start LIMIT 5")
    data = cur.fetchall()
    context = {
        'data': data
    }
    return render(request, 'period_history.html', context=context)


def menstrual_cycle(period_start, period_length, mc_length):
    cycle_dates = []

    for _ in range(12):
        period_end = (period_start + timedelta(days=period_length)).strftime("%Y-%m-%d")
        follicular_phase_start = (datetime.strptime(period_end, "%Y-%m-%d") + timedelta(days=0)).strftime("%Y-%m-%d")
        follicular_phase_end = (datetime.strptime(follicular_phase_start, "%Y-%m-%d") + timedelta(days=7)).strftime(
            "%Y-%m-%d")
        ovulatory_phase_start = (datetime.strptime(follicular_phase_end, "%Y-%m-%d") + timedelta(days=0)).strftime(
            "%Y-%m-%d")
        ovulatory_phase_end = (datetime.strptime(ovulatory_phase_start, "%Y-%m-%d") + timedelta(days=7)).strftime(
            "%Y-%m-%d")
        # luteal_phase_start = (datetime.strptime(ovulatory_phase_end, "%Y-%m-%d") + timedelta(days=1)).strftime(
        #     "%Y-%m-%d")
        # luteal_phase_end = (datetime.strptime(luteal_phase_start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
        cycle_dates.append({
            "period_start": period_start.strftime("%Y-%m-%d"),
            "period_end": period_end,
            "follicular_Phase_start": follicular_phase_start,
            "follicular_Phase_end": follicular_phase_end,
            "ovulatory_Phase_start": ovulatory_phase_start,
            "ovulatory_Phase_end": ovulatory_phase_end,
            # "luteal_Phase_start": luteal_phase_start,
            # "luteal_Phase_end": luteal_phase_end
        })

        period_start = period_start + timedelta(days=mc_length)

    return cycle_dates


@login_required
def appointments(request):
    patient_name = request.user
    date = datetime.today().date()
    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM pad WHERE patient = '{patient_name}' AND requested_date = '{date}'")
    data = cur.fetchone()
    status = ""
    if data is None:
        status = "no request's"
    elif data[0] is not None and data[7] is None:
        status = "pending"
    elif data[0] is not None and data[7] is not None:
        status = "booked"
    worker_name = None
    if data is not None:
        worker_name = data[1]
    cur.execute(f"SELECT link FROM ashaworker WHERE name = '{worker_name}'")
    data1 = cur.fetchone()
    link = None
    if data1 is not None:
        link = data1[0]
    context = {
        'data': data,
        'link': link,
        'status': status,
    }
    return render(request, 'appointments.html', context=context)


@login_required
def user_vc(request):
    patient_name = request.user
    date = datetime.today().date()
    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM pad WHERE patient = '{patient_name}' AND appointment_date ='{date}'")
    data = cur.fetchone()
    worker_name = None
    if data is not None:
        worker_name = data[1]
    cur.execute(f"SELECT link FROM ashaworker WHERE name = '{worker_name}'")
    data1 = cur.fetchone()
    link = None
    if data1 is not None:
        link = data1[0]
    context = {
        'link': link
    }
    return render(request, 'user_vc.html', context=context)


@login_required
def user_request_ashaworker(request):
    patient_name = request.user
    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT city FROM patient WHERE name = '{patient_name}'")
    city = cur.fetchone()[0]
    date = datetime.now().date() + timedelta(days=1)
    cur.execute(f"SELECT * FROM doctor_calendar WHERE city = '{city}' AND appointment_date = '{date}'")
    data = cur.fetchall()
    today = datetime.now().date()
    cur.execute(f"SELECT * FROM doctor_calendar WHERE city = '{city}' AND appointment_date = '{today}'")
    data1 = cur.fetchall()
    close_connection_with_database(cur,conn)
    time_slot = set()
    for tup in data:
        for i in range(1, 14):
            if tup[i] == 'no':
                time_slot.add(i)
    time_slot1 = set()
    for tup in data1:
        for i in range(1, 14):
            if tup[i] == 'no':
                time_slot1.add(i)
    if f"{datetime.now().hour}:{datetime.now().minute} == 10:00":
        if 1 in time_slot1:
            time_slot1.remove(1)
    if f"{datetime.now().hour}:{datetime.now().minute} == 10:30":
        if 2 in time_slot1:
            time_slot1.remove(2)
    if f"{datetime.now().hour}:{datetime.now().minute} == 11:00":
        if 3 in time_slot1:
            time_slot1.remove(3)
    if f"{datetime.now().hour}:{datetime.now().minute} == 11:30":
        if 4 in time_slot1:
            time_slot1.remove(4)
    if f"{datetime.now().hour}:{datetime.now().minute} == 12:00":
        if 5 in time_slot1:
            time_slot1.remove(5)
    if f"{datetime.now().hour}:{datetime.now().minute} == 12:30":
        if 6 in time_slot1:
            time_slot1.remove(6)
    if f"{datetime.now().hour}:{datetime.now().minute} == 01:00":
        if 7 in time_slot1:
            time_slot1.remove(7)
    if f"{datetime.now().hour}:{datetime.now().minute} == 01:30":
        if 8 in time_slot1:
            time_slot1.remove(8)
    if f"{datetime.now().hour}:{datetime.now().minute} == 02:00":
        if 9 in time_slot1:
            time_slot1.remove(9)
    if f"{datetime.now().hour}:{datetime.now().minute} == 02:30":
        if 10 in time_slot1:
            time_slot1.remove(10)
    if f"{datetime.now().hour}:{datetime.now().minute} == 03:00":
        if 11 in time_slot1:
            time_slot1.remove(11)
    if f"{datetime.now().hour}:{datetime.now().minute} == 03:30":
        if 12 in time_slot1:
            time_slot1.remove(12)
    if f"{datetime.now().hour}:{datetime.now().minute} == 04:00":
        if 13 in time_slot1:
            time_slot1.remove(13)
    if f"{datetime.now().hour}:{datetime.now().minute} == 04:30":
        if 14 in time_slot1:
            time_slot1.remove(14)
    # print(time_slot1)
    # time_slot2 = set()
    # for tup in default_doc:
    #     for i in range(1, 14):
    #         if tup[i] == 'no':
    #             time_slot2.add(i)
    # print(time_slot2)
    context = {
        'time_slots': time_slot,
        'time_slots1': time_slot1,
    }
    if request.method == 'POST':
        age = request.POST.get('age')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        problem = request.POST.get('problems')
        additionalProblem = request.POST.get('additionalProblem')
        worker = request.GET.get('worker')
        worker_phone = request.GET.get('phone')
        slot_tomorrow = request.POST.get('slot')
        slot_today = request.POST.get('slot1')
        date = datetime.now().date()
        if slot_today == "none":
            conn = build_connection_with_database()
            cur = conn.cursor()
            cur.execute(
                f"INSERT INTO pad (patient, worker, age, height, weight, problem, additionalproblem, requested_slot, requested_date)"
                f"VALUES ('{patient_name}', '{worker}', '{age}', '{height}', '{weight}', '{problem}', "
                f"'{additionalProblem}', '{slot_tomorrow}', '{date}')")
            cur.execute(f"SELECT phone FROM ashaworker WHERE name = '{worker}'")
            ashaworker_phone = cur.fetchone()
            today_date = datetime.now().date()
            cur.execute(
                f"INSERT INTO todays_patients(patient_name, date, worker) VALUES ('{patient_name}', '{today_date}', '{worker}')")
            close_connection_with_database(cur, conn)
        elif slot_tomorrow == "none":
            conn = build_connection_with_database()
            cur = conn.cursor()
            cur.execute(
                f"INSERT INTO pad (patient, worker, age, height, weight, problem, additionalproblem, requested_slot, requested_date)"
                f"VALUES ('{patient_name}', '{worker}', '{age}', '{height}', '{weight}', '{problem}', "
                f"'{additionalProblem}', '{slot_today}', '{date}')")
            cur.execute(f"SELECT phone FROM ashaworker WHERE name = '{worker}'")
            ashaworker_phone = cur.fetchone()
            today_date = datetime.now().date()
            cur.execute(
                f"INSERT INTO todays_patients(patient_name, date, worker) VALUES ('{patient_name}', '{today_date}', '{worker}')")
            close_connection_with_database(cur, conn)

        messages.success(request, "Your request has been sent.")

        # send ashaworker a notification about new patient's request

        account_sid = 'ACa5f2857641077158c8ed19e6ed604843'
        auth_token = '4869049d5c7df6a8c04d73c1616dacf7'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_='+14807255279',
            body=f"Hello worker, you've got a new patient's request with the name {patient_name}, plz check your dashboard",
            to='+918433813239'
        )

        return redirect('user_dashboard')
    return render(request, 'user_request_ashaworker.html', context=context)


@login_required
def ashaworker_dashboard(request):
    worker_name = request.user
    context = {
        'worker_name': worker_name
    }
    return render(request, 'ashaworker_dashboard.html', context=context)


@login_required
def appointment_booking(request):
    worker_name = request.user
    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM todays_patients WHERE worker = '{worker_name}' AND date = '{datetime.now().today()}'")
    data = cur.fetchall()
    cur.execute(f"SELECT city FROM ashaworker WHERE name = '{worker_name}'")
    city = cur.fetchone()[0]
    current_date = datetime.today().date()
    date = datetime.today().date() + timedelta(days=1)
    cur.execute(f"SELECT * FROM doctor_calendar WHERE appointment_date='{date}'")
    doctor_calendar = cur.fetchall()
    cur.execute(f"SELECT * FROM doctor_calendar WHERE appointment_date='{current_date}'")
    today_available_doctor = cur.fetchall()
    # print(today_available_doctor)
    cur.execute(f"SELECT * FROM ashaworker WHERE name = '{worker_name}'")
    worker_data = cur.fetchone()
    close_connection_with_database(cur, conn)
    patient_details = None
    if request.method == 'POST':
        selected_patient = request.POST.get('patient')
        # print(selected_patient)
        conn = build_connection_with_database()
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM pad WHERE patient = '{selected_patient}' AND worker = '{worker_name}' ORDER BY requested_date LIMIT 1 ")
        patient_details = cur.fetchone()
        # print(patient_details)
        close_connection_with_database(cur, conn)
    context = {
        'data': [row[0] for row in data],
        'patient_details': patient_details,
        'doctor_calendar': doctor_calendar,
        'worker_data': worker_data,
        'today_available_doctor': today_available_doctor,
        # 'worker_name': worker_name
    }
    return render(request, 'appointment_booking.html', context=context)


@login_required
def ashaworker_appointments(request):
    worker_name = request.user
    today = datetime.now().date()
    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM pad WHERE appointment_date = '{today}' AND worker = '{worker_name}'")
    data = cur.fetchall()
    cur.execute(f"SELECT link FROM ashaworker WHERE name = '{worker_name}'")
    link = cur.fetchone()[0]
    context = {
        'link': link,
        'data': data,
    }
    return render(request, 'ashaworker_appointments.html', context=context)


@login_required
def user_ashaworkers(request):
    current_user = request.user
    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT city FROM patient WHERE name = '{current_user}'")
    current_user_city = cur.fetchone()
    cur.execute(f"SELECT * FROM ashaworker WHERE type = 'default'")
    default_ashaworker = cur.fetchall()
    cur.execute(f"SELECT * FROM ashaworker WHERE city = '{current_user_city[0]}'")
    data = cur.fetchall()
    context = {
        'data': data,
        'default_ashaworker': default_ashaworker
    }
    return render(request, 'user_ashaworkers.html', context=context)


# images and designing
@login_required
def educational_resources(request):
    return render(request, 'educational_resources.html')


# not done
@login_required
def predictive_analysis(request):
    return render(request, 'predictive_analysis.html')


@login_required
def prediction_input(request):
    if request.method == 'POST':
        age = request.POST.get('age')
        fsh = request.POST.get('fsh')
        lh = request.POST.get('lh')
        glucose_fasting = request.POST.get('glucose_fasting')
        glucose_pp = request.POST.get('glucose_pp')
        insulin_fasting = request.POST.get('insulin_fasting')
        insulin_pp = request.POST.get('insulin_pp')
        prolactin = request.POST.get('prolactin')
        testosterone = request.POST.get('testosterone')
        t3 = request.POST.get('t3')
        t4 = request.POST.get('t4')
        tsh = request.POST.get('tsh')
        input_data = [age, fsh, lh, glucose_fasting, glucose_pp, insulin_fasting, insulin_pp, prolactin, testosterone,
                      t3, t4, tsh]
        input_data_reshaped = np.array(input_data).reshape(1, -1)
        file_path = 'trained_model.pkl'
        with open(file_path, 'rb') as file:
            loaded_model = pickle.load(file)
        predictions = loaded_model.predict(input_data_reshaped)
        result = ""
        description = ""
        if predictions[0] == 1:
            result = "YES"
            description = "We would suggest that according to the parameters you entered, you might have PCOD/PCOS. Thus, kindly contact a doctor as soon as possible. If you require assistance in booking an appointment, you can also connect with your nearest ASHA worker."
        elif predictions[0] == -1:
            result = "NO"
            description = "We would suggest that according to the parameters you entered, you do not have PCOD/PCOS. But you can check our educational resources for quick tips for maintaining a healthy lifestyle."
        else:
            result = "SYMPTOMS OF PCOD/PCOS PREDICTED "
            description = "We would suggest that according to the parameters you entered, some symptoms of PCOD/PCOS are being detected. Thus, kindly contact a doctor for further clarification. If you require assistance in booking an appointment, you can also connect with your nearest ASHA worker."
        context = {
            'result': result,
            'description': description,
            'input_data': input_data
        }
        return render(request, 'prediction_result.html', context=context)
    return render(request, 'prediction_input.html')


@login_required
def prediction_result(request):
    input_data = request.GET.get('input_data')
    result = request.GET.get('result')
    # print(input_data, result)

    input_data = ast.literal_eval(input_data)
    data = {
        "Age": input_data[0],
        "FSH": input_data[1],
        "LH": input_data[2],
        "Glucose (Fasting)": input_data[3],
        "Glucose (Postprandial)": input_data[4],
        "Insulin (Fasting)": input_data[5],
        "Insulin (Postprandial)": input_data[6],
        "Prolactin": input_data[7],
        "Testosterone": input_data[8],
        "T3": input_data[9],
        "T4": input_data[10],
        "TSH": input_data[11]
    }
    msg = ""
    # print(data)
    # print(input_data)
    for k, v in data.items():
        msg += k
        msg += " : "
        msg += v
        msg += " \n"
    msg += f"Result : {result}."
    # print(msg)
    account_sid = 'ACa5f2857641077158c8ed19e6ed604843'
    auth_token = '4869049d5c7df6a8c04d73c1616dacf7'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=f'{msg}',
        to='whatsapp:+918433813239'
    )
    return render(request, 'prediction_result.html')


@login_required
def send_prescription(request):
    patient_name = request.GET.get('patient')
    # print(patient_name)
    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT phone FROM patient WHERE name = '{patient_name}'")
    phone_no = cur.fetchone()[0]
    msg = """Doctor's Prescription for Blood Test (PCOD/PCOS Evaluation)
        Instructions:
        •	Fasting: Please avoid food or sugary drinks for at least 8 hours before the test. Water is okay.
        •	Medications: Please inform the laboratory if you are taking any medications.
        
        Blood Tests:
        •	Hormones: 
        o	Follicle-Stimulating Hormone (FSH)
        o	Luteinizing Hormone (LH)
        o	Prolactin
        o	Testosterone
        •	Thyroid Function: 
        o	Triiodothyronine (T3)
        o	Thyroxine (T4)
        o	Thyroid Stimulating Hormone (TSH)
        •	Blood Sugar: 
        o	Fasting Blood Sugar
        o	Postprandial Blood Sugar (2 hours after eating)
        •	Insulin: 
        o	Fasting Insulin
        o	Postprandial Insulin (2 hours after eating)
        Additional Notes:
        •	It is recommended to perform this blood test during the follicular phase of your menstrual cycle.
        •	You can use the menstrual tracking feature in Telegynaec App to confirm your follicular phase.
        •	If you are pregnant, please inform your doctor before proceeding with this test.
        Disclaimer: This blood test panel is used to screen for PCOS, but it cannot definitively diagnose the condition. Your doctor will interpret your results in conjunction with your medical history and further examination.
        
        """
    account_sid = 'ACa5f2857641077158c8ed19e6ed604843'
    auth_token = '4869049d5c7df6a8c04d73c1616dacf7'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=f'{msg}',
        to='whatsapp:+918433813239'
    )
    return redirect('doctor_todays_patient')


@login_required
def ashaworker_is_booking_appointment(request):
    if request.method == 'POST':
        patient = request.GET.get('patient')
        problem = request.GET.get('problem')
        additional_problem = request.GET.get('additional_problem')
        doctor = request.POST.get('doctor')
        time = doctor[-1]
        print(patient, problem, doctor, time)
        spl = ['t', 'e', 'v', 'h', 'o']
        if time in spl:
            if time == 't':
                time = "10"
            elif time == "e":
                time = "11"
            elif time == "v":
                time = "12"
            elif time == "h":
                time = "13"
            else:
                time = "14"

        date = datetime.today().date() + timedelta(days=1)
        conn = build_connection_with_database()
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO patient_history(doctor, patient, problem, date) VALUES ('{doctor[:-1]}', '{patient}', '{problem}', '{date}')")
        cur.execute(
            f"UPDATE pad SET doctor = '{doctor[:-1]}', appointment_date = '{date}', appointment_time = '{time}' WHERE patient = '{patient}' AND additionalproblem = '{additional_problem}'")
        cur.execute(f'UPDATE doctor_calendar SET "{time}" = \'yes\' WHERE name = \'{doctor[:-1]}\'')
        cur.execute(f"SELECT phone FROM patient WHERE name = '{patient}'")
        patient_phone = cur.fetchone()
        cur.execute(f"SELECT worker FROM pad WHERE patient = '{patient}'")
        ashaworker_name = cur.fetchone()
        close_connection_with_database(cur, conn)

        messages.success(request, 'Appointment Booked')
        #     now appointment set for tomorrow and at time selected by ashaworker

        #     send sms to patient about appointment confirmation
        if time == "1":
            time = "10:00 to 10:30"
        elif time == "2":
            time = "10:30 to 11:00"
        elif time == "3":
            time = "11:00 to 11:30"
        elif time == "4":
            time = "11:30 to 12:00"
        elif time == "5":
            time = "12:00 to 12:30"
        elif time == "6":
            time = "12:30 to 13:00"
        elif time == "7":
            time = "13:00 to 13:30"
        elif time == "8":
            time = "13:30 to 14:00"
        elif time == "9":
            time = "14:00 to 14:30"
        elif time == "10":
            time = "14:30 to 15:00"
        elif time == "11":
            time = "15:00 to 15:30"
        elif time == "12":
            time = "15:30 to 16:00"
        elif time == "13":
            time = "16:00 to 16:30"
        elif time == "14":
            time = "16:30 to 17:00"

        account_sid = 'ACa5f2857641077158c8ed19e6ed604843'
        auth_token = '4869049d5c7df6a8c04d73c1616dacf7'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_='+14807255279',
            body=f"Hello User, your appointment is confirmed by Ashaworker {ashaworker_name[0]}\n Time: {time} \n Date : {date}",
            to='+918433813239'
        )

        #  scheduling machine (I've to build one)
        #  my scheduling machine will take date and time, worker name, doc name, patient name and send the sms / remainder

        return redirect('ashaworker_dashboard')


@login_required
def ashaworker_is_booking_appointment1(request):
    if request.method == 'POST':
        patient = request.GET.get('patient')
        problem = request.GET.get('problem')
        additional_problem = request.GET.get('additional_problem')
        doctor = request.POST.get('doctor')
        time = doctor[-1]
        # print(patient, problem, doctor, time)
        spl = ['t', 'e', 'v', 'h', 'o']
        if time in spl:
            if time == 't':
                time = "10"
            elif time == "e":
                time = "11"
            elif time == "v":
                time = "12"
            elif time == "h":
                time = "13"
            else:
                time = "14"

        date = datetime.today().date()
        conn = build_connection_with_database()
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO patient_history(doctor, patient, problem, date) VALUES ('{doctor[:-1]}', '{patient}', '{problem}', '{date}')")
        cur.execute(
            f"UPDATE pad SET doctor = '{doctor[:-1]}', appointment_date = '{date}', appointment_time = '{time}' WHERE patient = '{patient}' AND additionalproblem = '{additional_problem}'")
        cur.execute(f'UPDATE doctor_calendar SET "{time}" = \'yes\' WHERE name = \'{doctor[:-1]}\'')
        cur.execute(f"SELECT phone FROM patient WHERE name = '{patient}'")
        patient_phone = cur.fetchone()
        cur.execute(f"SELECT worker FROM pad WHERE patient = '{patient}'")
        ashaworker_name = cur.fetchone()
        close_connection_with_database(cur, conn)

        messages.info(request, 'Appointment Booked')

        #     now appointment set for tomorrow and at time selected by ashaworker

        #     send sms to patient about appointment confirmation
        if time == "1":
            time = "10:00 to 10:30"
        elif time == "2":
            time = "10:30 to 11:00"
        elif time == "3":
            time = "11:00 to 11:30"
        elif time == "4":
            time = "11:30 to 12:00"
        elif time == "5":
            time = "12:00 to 12:30"
        elif time == "6":
            time = "12:30 to 13:00"
        elif time == "7":
            time = "13:00 to 13:30"
        elif time == "8":
            time = "13:30 to 14:00"
        elif time == "9":
            time = "14:00 to 14:30"
        elif time == "10":
            time = "14:30 to 15:00"
        elif time == "11":
            time = "15:00 to 15:30"
        elif time == "12":
            time = "15:30 to 16:00"
        elif time == "13":
            time = "16:00 to 16:30"
        elif time == "14":
            time = "16:30 to 17:00"


        account_sid = 'ACa5f2857641077158c8ed19e6ed604843'
        auth_token = '4869049d5c7df6a8c04d73c1616dacf7'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_='+14807255279',
            body=f"Hello User, your appointment is confirmed by Ashaworker {ashaworker_name[0]}\n Time: {time} \n Date : {date}",
            to='+918433813239'
        )

        #  scheduling machine (I've to build one)
        #  my scheduling machine will take date and time, worker name, doc name, patient name and send the sms / remainder

        return redirect('ashaworker_dashboard')


@login_required
def ashaworker_update_link(request):
    worker = request.user
    if request.method == 'POST':
        link = request.POST.get('link')
        conn = build_connection_with_database()
        cur = conn.cursor()
        cur.execute(f"UPDATE ashaworker SET link = '{link}' WHERE name = '{worker}'")
        close_connection_with_database(cur, conn)
    return render(request, 'ashaworker_update_link.html')


@login_required
def doctor_dashboard(request):
    doctor_name = request.user
    # doctor calendar madhe editing
    if request.method == 'POST':
        one = request.POST.get('1')
        two = request.POST.get('2')
        three = request.POST.get('3')
        four = request.POST.get('4')
        five = request.POST.get('5')
        six = request.POST.get('6')
        seven = request.POST.get('7')
        eight = request.POST.get('8')
        nine = request.POST.get('9')
        ten = request.POST.get('10')
        eleven = request.POST.get('11')
        twelve = request.POST.get('12')
        thirteen = request.POST.get('13')
        fourteen = request.POST.get('14')
        query_part = '"name" ,'
        count = 0
        if one is not None:
            query_part += '"'
            query_part += one
            query_part += '"'
            query_part += ","
            count += 1
        if two is not None:
            query_part += '"'
            query_part += two
            query_part += '"'
            query_part += ","
            count += 1
        if three is not None:
            query_part += '"'
            query_part += three
            query_part += '"'
            query_part += ","
            count += 1
        if four is not None:
            query_part += '"'
            query_part += four
            query_part += '"'
            query_part += ","
            count += 1
        if five is not None:
            query_part += '"'
            query_part += five
            query_part += '"'
            query_part += ","
            count += 1
        if six is not None:
            query_part += '"'
            query_part += six
            query_part += '"'
            query_part += ","
            count += 1
        if seven is not None:
            query_part += '"'
            query_part += seven
            query_part += '"'
            query_part += ","
            count += 1
        if eight is not None:
            query_part += '"'
            query_part += eight
            query_part += '"'
            query_part += ","
            count += 1
        if nine is not None:
            query_part += '"'
            query_part += nine
            query_part += '"'
            query_part += ","
            count += 1
        if ten is not None:
            query_part += '"'
            query_part += ten
            query_part += '"'
            query_part += ","
            count += 1
        if eleven is not None:
            query_part += '"'
            query_part += eleven
            query_part += '"'
            query_part += ","
            count += 1
        if twelve is not None:
            query_part += '"'
            query_part += twelve
            query_part += '"'
            query_part += ","
            count += 1
        if thirteen is not None:
            query_part += '"'
            query_part += thirteen
            query_part += '"'
            query_part += ","
            count += 1
        if fourteen is not None:
            query_part += '"'
            query_part += fourteen
            query_part += '"'
            query_part += ","
            count += 1

        query_part1 = f"'{doctor_name}', "
        for i in range(0, count):
            query_part1 += "'"
            query_part1 += "no"
            query_part1 += "'"
            query_part1 += ","
        conn = build_connection_with_database()
        cur = conn.cursor()
        cur.execute(f"SELECT city FROM doctor WHERE name = '{doctor_name}'")
        city = cur.fetchone()[0]
        query_part += "appointment_date , city"
        date = datetime.today().date() + timedelta(days=1)
        # print(date)
        query_part1 += f"'{date}', '{city}'"
        main_query = f"INSERT INTO doctor_calendar({query_part}) VALUES ({query_part1})"
        # print(main_query)
        cur.execute(main_query)
        close_connection_with_database(cur, conn)

    # + timedelta(days=1) for testing
    conn = build_connection_with_database()
    cur = conn.cursor()
    # cur.execute(f"SELECT * FROM pad WHERE doctor = '{doctor_name}' AND appointment_date = '{todays_date}'")
    # data = cur.fetchall()
    cur.execute(f"SELECT * FROM doctor WHERE name = '{doctor_name}'")
    doctor_data = cur.fetchone()
    close_connection_with_database(cur, conn)
    context = {
        # 'data': data,
        'doctor_data': doctor_data,
        'doctor_name': doctor_name
    }
    return render(request, 'doctor_dashboard.html', context=context)


@login_required
def doctor_todays_patient(request):
    doctor_name = request.user
    todays_date = datetime.today().date()
    conn = build_connection_with_database()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM pad WHERE doctor = '{doctor_name}' AND appointment_date = '{todays_date}'")
    data = cur.fetchall()
    cur.execute(
        f"SELECT * FROM pad WHERE doctor = '{doctor_name}' AND appointment_date = '{todays_date + timedelta(days=1)}'")
    tomorrow_appointment = cur.fetchall()
    close_connection_with_database(cur, conn)
    context = {
        'data': data,
        'tomorrow_appointment': tomorrow_appointment
    }
    return render(request, 'doctor_todays_patient.html', context=context)


# doctor sathi ahe
@login_required
def patient_history(request):
    doctor = request.user
    today = datetime.now().date()
    context = {
        'data': None
    }
    if request.method == 'POST':
        patient = request.POST.get('patient')
        conn = build_connection_with_database()
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM patient_history WHERE patient = '{patient}' AND doctor = '{doctor}'")
        data = cur.fetchall()
        context = {
            'data': data
        }
    return render(request, 'patient_history.html', context=context)


@login_required
def doctor_timeslot(request):
    return render(request, 'doctor_timeslot.html')


def home(request):
    return render(request, 'home.html')


# posters


def poster(request):
    today = datetime.now().date()
    period_start = today
    dates = menstrual_cycle(period_start)

    # Convert dates to JSON string
    print(dates)
    context = {
        'dates_json': dates  # Pass the JSON string to the template
    }
    return render(request, 'poster.html', context=context)


def poster1(request):
    return render(request, 'poster1.html')


def poster2(request):
    return render(request, 'poster2.html')


def poster3(request):
    return render(request, 'poster3.html')


def poster4(request):
    return render(request, 'poster4.html')
