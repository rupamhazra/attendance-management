from django.conf import settings
from rest_framework import mixins
from rest_framework import filters
from datetime import datetime, timedelta, date
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q, Count, query
import os
import platform
from decimal import *
import re
from dateutil.relativedelta import relativedelta
import platform
from redis_handler import pub as email_pub
from django.template import Context, Template
from mailsend.models import MailHistory, MailTemplate
from history.models import ActionHistory
import json


def json_default(o):
    if isinstance(o, (date, datetime)):
        return str(o)

def get_host_with_port(request, media=False):
    if os.environ.get('SERVER_GATEWAY_INTERFACE') == 'Web':
        protocol = 'https://' if request.is_secure() else 'http://'
        url = protocol+request.get_host()+'/media/' if media else protocol + \
            request.get_host()+'/'
    else:
        url = settings.SERVER_URL+'media/' if media else settings.SERVER_URL
    return url


def get_path_from_media_url(url):
    spiltted = url.split('media/')
    relative_path = spiltted[1]
    path = os.path.join(settings.MEDIA_ROOT, relative_path)
    os_name = platform.system().lower()
    if os_name == "windows":
        path = path.replace('/', '\\')
    return path


def get_media_upload_path(file_name):
    path = None
    if file_name:
        path = os.path.join(settings.MEDIA_ROOT, file_name)
        os_name = platform.system().lower()
        if os_name == "windows":
            path = path.replace('/', '\\')
    return path


def remove_existing_media(file_name):
    if file_name:
        existing_path = get_media_upload_path(file_name)
        print('remove', existing_path)
        if existing_path and os.path.isfile(existing_path):
            print('removed', existing_path)
            os.remove(existing_path)


def get_media_download_path(app, module, file_name, request):
    media_path = os.path.join('media', app, module)
    dir_path = os.path.join(settings.MEDIA_ROOT_EXPORT, media_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    url = get_host_with_port(request) + os.path.join(media_path, file_name)
    os_name = platform.system().lower()
    if os_name == "windows":
        url = url.replace('\\', '/')
    file_path = os.path.join(dir_path, file_name)
    return (file_path, url)


def create_simple_excel_file(headers, rows, file_path):
    import xlsxwriter
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()
    header_format = workbook.add_format(
        {'bold': True, 'font_size': 9, 'align': 'center', 'valign': 'vcenter'})
    cell_format = workbook.add_format(
        {'font_size': 9, 'font_color': '#1e1e1e', 'align': 'center', 'valign': 'vcenter'})
    cell_width_map, cell_height_map = {}, {}

    col_idx, row_idx = 0, 0
    for h_idx, header in enumerate(headers):
        worksheet_write(worksheet, cell_width_map, row_idx,
                        col_idx + h_idx, header, header_format)
    row_idx += 1
    for i, row in enumerate(rows):
        for item in row:
            worksheet_write(worksheet, cell_width_map, row_idx,
                            col_idx, str(item), cell_format)
            col_idx += 1
        row_idx += 1
        col_idx = 0
    workbook.close()
    return file_path


def raw_query_extract(query):

    return query.query


def round_calculation(days: int, leave_count: int) -> float:
    print('days', days, ":int,", leave_count)
    int_value = days*leave_count//365
    frq_value = round((days*leave_count/365), 2) - int_value
    print("int_value", int_value, "frq_value", frq_value)
    frq_add = 0.0
    if frq_value < 0.25:
        value = float(int_value)+frq_add
    elif frq_value >= 0.25 and frq_value < 0.75:
        frq_add = 0.5
        value = float(int_value)+frq_add
    elif frq_value >= 0.75:
        frq_add = 1.0
        value = float(int_value)+frq_add
    print("value", value)
    return value


def round_calculation_V2(days: int, leave_count: int) -> float:
    return value


def convert24(str1):
    # 1:56PM
    # Checking if last two elements of time
    # is AM and first two elements are 12
    if str1[-2:] == "AM" and str1[:2] == "12":
        return "00" + str1[2:-2]

    # remove the AM
    elif str1[-2:] == "AM":
        # return "0"+str1[:-2]
        return str1[:-2]

    # Checking if last two elements of time
    # is PM and first two elements are 12
    elif str1[-2:] == "PM" and str1[:2] == "12":
        print('str 1', str1[:-2])
        return str1[:-2]

    else:

        # add 12 to hours and remove PM
        return str(int(str1[:1]) + 12) + str1[1:4]


def get_time_diff(DurationFrom, durationTo):
    date_format = "%H:%M:%S"
    durationTo = datetime.strptime(str(durationTo), date_format)
    DurationFrom = datetime.strptime(str(DurationFrom), date_format)
    timediff = (durationTo-DurationFrom).total_seconds()
    hours = round(timediff / 3600, 2)
    return hours

def get_current_financial_year():
    return [2020, 2021]

def get_pagination_offset(page=1, page_count=10):
    return slice(page_count*(page-1), page*page_count)

def create_pagination_data(request, data_list):
    page = int(request.query_params.get('page', 1))
    page_count = int(request.query_params.get('page_count', 10))
    pagination_offset_slice = get_pagination_offset(page=page, page_count=page_count)
    res = dict()
    res['results'] = data_list[pagination_offset_slice]
    res['count'] = len(data_list)
    res['request_status'] = 1
    res['msg'] = 'Success' if res['count'] else 'Data Not Found'

    return res


def send_mail(code, user_email, mail_data, ics=''):
    send_mail_list(code, [user_email], mail_data, ics)


def send_mail_list(code, user_email_list, mail_data, ics=''):
    #print('Mail sending is currently disabled')
    mail_content = MailTemplate.objects.get(code=code)
    subject = mail_content.subject
    if mail_content.is_test:
        subject = 'Test Mail - ' + mail_content.subject
    template_variable = mail_content.template_variable.split(",")
    html_content = Template(mail_content.html_content)
    match_data_dict = {}
    for data in template_variable:
        if data.strip() in mail_data:
            match_data_dict[data.strip()] = mail_data[data.strip()]
    if match_data_dict:
        context_data = Context(match_data_dict)
        html_content = html_content.render(context_data)

    entry = MailHistory()
    entry.code = code
    entry.recipient_list = json.dumps(user_email_list)
    entry.body = html_content
    entry.subject = subject
    entry.attachment = ics
    entry.save()
    success, msg = email_pub.publish('email-ssml', [entry.id])


def save_history(request, module_name, action, previous_data=None, current_data=None, mode='API'):

    action_entry = ActionHistory(
        module_name=module_name,
        action_by=request.user,
        previous_data=json.dumps(previous_data, default=json_default),  # convert data to json
        current_data=json.dumps(current_data, default=json_default),  # convert data to json
        action=action,
        url=request.build_absolute_uri(),
        mode=mode
    )
    action_entry.save()


def get_ordering(field_name, order):
    if str(order).lower() == 'asc':
        return field_name
    else:
        return '-{0}'.format(field_name)


def check_unique(model_or_qyery_set, data, key, skip_id=None):
    
    filter = {
        key: data[key]
    }
    if key == 'username':
        filter['is_active'] = True
    else:
        filter['is_deleted'] = False

    if type(model_or_qyery_set) is query.QuerySet:
        query_set = model_or_qyery_set.filter(**filter)
    else:
        query_set = model_or_qyery_set.objects.filter(**filter)
    if skip_id:
        query_set = query_set.filter(~Q(id=skip_id))
        #print('query_set',query_set.query)
    return query_set.count() == 0

# added by Shubhadeep for writing excel using xlsxwriter


def worksheet_write(worksheet, cell_width_map, row_idx, col_idx, val, cell_format):
    worksheet.write(row_idx, col_idx, val, cell_format)
    width = 8
    if len(str(val)) > 8:
        width = len(str(val)) * 0.9
    if col_idx in cell_width_map and cell_width_map[col_idx] > width:
        width = cell_width_map[col_idx]
    cell_width_map[col_idx] = width
    worksheet.set_column(col_idx, col_idx, width=cell_width_map[col_idx])


def worksheet_merge_range(worksheet, cell_height_map, row_idx1, col_idx1, row_idx2, col_idx2, val, format):
    worksheet.merge_range(row_idx1, col_idx1, row_idx2, col_idx2, val, format)
    height = 15
    for c in str(val):
        if c == '\n':
            height += 16
    if row_idx1 in cell_height_map and cell_height_map[row_idx1] > height:
        height = cell_height_map[row_idx1]
    cell_height_map[row_idx1] = height
    worksheet.set_row(row_idx1, height=cell_height_map[row_idx1])


def worksheet_merge_range_by_width(worksheet, cell_width_map, row_idx1, col_idx1, row_idx2, col_idx2, val, format):
    worksheet.merge_range(row_idx1, col_idx1, row_idx2, col_idx2, val, format)
    width = 8
    if len(str(val)) > 8:
        width = len(str(val)) * 0.9
    col_idx = col_idx1
    if col_idx in cell_width_map and cell_width_map[col_idx] > width:
        width = cell_width_map[col_idx]
    cell_width_map[col_idx] = width
    worksheet.set_column(col_idx, col_idx, width=cell_width_map[col_idx])


def doc_details(self,instance,model=''):
    request = self.context.get('request')
    doc_list = list()
    docs  = model.objects.filter(approval_request=instance,is_deleted=False)
    for doc in docs:
        doc_list.append({
            'id':doc.id,
            'doc_name':doc.doc_name,
            'doc': request.build_absolute_uri(doc.doc.url)
        })
    return doc_list

def modify_model_field_name(self,instance,model='',fetch_columns=list()):
    # import inspect
    # curframe = inspect.currentframe()
    # calframe = inspect.getouterframes(curframe, 2)
    # method_name = calframe[1][3]
    # prefix_name = method_name.replace('get_','').replace('_details','')
    prefix_name = str(model.__name__).lower()
    details = model.objects.filter(pk=instance.employee.department.id,is_deleted=False).values(*fetch_columns)[0]
    res = {prefix_name+'_' + str(key): val for key, val in details.items()}
    return res

