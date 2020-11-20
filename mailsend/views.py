from mailsend.models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from global_function import send_mail
from knox.auth import TokenAuthentication

class MailSendApiView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        email = request.data['email']
        # updated by Shubhadeep for ICS testing
        send_calendar = request.data.get('send_calendar', False)
        subject = request.data.get('subject', 'This is test mail')
        # --
        mail_response = ''

        mail_id = request.data['email']
        # ============= Mail Send ==============#
        if mail_id:
            mail_data = {
                        "subject": subject
                       }
            # updated by Shubhadeep for ICS testing
            if send_calendar:
                import datetime
                import random
                import uuid
                uid = uuid.uuid4()
                even_time = datetime.datetime.now() + datetime.timedelta(hours=2)
                end_time = even_time + datetime.timedelta(hours=2)
                summery = "Demo event {0}".format(random.randint(1, 10))
                desc = "Demo event generated by Django backend"

                s_date = even_time.strftime("%Y%m%dT%H%M%S")
                e_date = end_time.strftime("%Y%m%dT%H%M%S")
                ics_data = """BEGIN:VCALENDAR
VERSION:2.0
METHOD:PUBLISH
CALSCALE:GREGORIAN
BEGIN:VEVENT
SUMMARY: {}
DTSTART;TZID=Asia/Kolkata:{}
DTEND;TZID=Asia/Kolkata:{}
LOCATION:Shyam Tower,Kolkata-700091
DESCRIPTION: {}
STATUS:CONFIRMED
SEQUENCE:0
UID:{}
BEGIN:VALARM
TRIGGER:-PT10M
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR""".format(summery, s_date, e_date, desc, uid)

                send_mail('TEST001', mail_id, mail_data, ics_data)
            else:
                send_mail('TEST001', mail_id, mail_data)
            # --
        response_dict = {
            "msg":"success"
        }
        return Response(response_dict)