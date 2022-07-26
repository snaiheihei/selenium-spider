import time
from driver import Driver
from selenium.webdriver.common.action_chains import ActionChains
import csv
import requests
import re

patient_infos = []
driver = Driver()
actionChain = ActionChains(driver.driver)

def logon(url_logon, name, passwd):
    driver.open_url(url_logon)
    driver.input_data("id", "account", name)
    driver.input_data("id", "password", passwd)
    driver.click("id", "login-button")
    print("="*50)
    print("logon successful~")
    time.sleep(1)
    driver.click("css", "#mCSB_4 > div.mCSB_container > div.ares3-sidebar-container.ng-isolate-scope > ul > li:nth-child(2) > a")
    driver.switch_iframe(driver.locateElement("css", "#hebe-container-level-0 > iframe"))
    print("switch iframe successful")
    # 跳过引导，切到今日
    driver.click("css", ".introjs-skipbutton")
    driver.click("css", "#switch-appt-date > button")
    time.sleep(1)

def get_eventID():
    # new requirment one week data 7/21
    select_el = driver.locateElement("css", "#switch-appt-view > nz-select")
    actionChain.move_to_element(select_el).perform()
    select_el = driver.locateElement("css", "#switch-appt-view > nz-select")
    select_el.click()
    actionChain.move_to_element(select_el).move_by_offset(30,50).click().perform()
    driver.click("css", "#switch-appt-view > nz-radio-group > label:nth-child(2)")
    # find child patient  7/23
    time.sleep(8)
    html = driver.driver.execute_script("return document.documentElement.outerHTML")
    regex = re.compile(r'event_id="(\d{3,10})[\s\S]{50,650}icon-child')
    event_id = regex.findall(html)
    print(event_id)
    return event_id

    # 获取所有event ID
    # time.sleep(8)
    # els_eventID = driver.locateElements("css", "#calendar-container > div.dhx_cal_data div[event_id]")

    # for el in  els_eventID:
    #     try:
    #         id = el.get_attribute("event_id")
    #         print("eventID: ", id)
    #         el.find_element(by=By.CSS_SELECTOR, value=".icon-child")
    #         print(":::::::: is a child patient....")
    #         event_id.append(id)
    #     except Exception:
    #         pass

    # 展开更多
    # more_arrow = driver.locateElement("css", "#calendar-container > div.event-count-hint.next.ng-star-inserted > div.count")
    # if more_arrow:
    #     # headless 模式下会出现click not reachable exception
    #     my_actionChain = ActionChains(driver.driver)
    #     my_actionChain.move_to_element(more_arrow).perform()
    #     driver.click("css", "#calendar-container > div.event-count-hint.next.ng-star-inserted > div.count")
    #     time.sleep(8)
    #     more_els_eventID = driver.locateElements("css", "#calendar-container > div.dhx_cal_data div[event_id]")
    #     for el in more_els_eventID:
    #         id = el.get_attribute("event_id")
    #         event_id.append(id)
    # return list(set(event_id))

def get_patientID(eventIDs):
    # 请求API 获取所有的patient ID
    # 获取所有event_id , https://api-hn01.linkedcare.cn:9001/api/v1/appointment/1298361  >> 获取patient_id
    patientIds = []
    current_cookies = driver.driver.get_cookies()
    s = requests.Session()
    [s.cookies.set(c['name'], c['value']) for c in current_cookies]
    headers = {
        'authorization': 'bearer 69-pAufpdUy8U1nUPootQzEaZhwrMFQ6LXFfRsEKe-3Xf86L-2NqNDrA06gNDKBipzlpHcesIN-HDrjPWRXrJI07lEal29iGA4mPCP1Fzjs3alaH7NjAj_cC1hKYWH-M8RAKwdOG_DHfeqQhBkMQV7CvOPX7V-Ak68PKV1GxZBBWctZCqSTfw9OScUiXFkX7r5sDRCG4uSrOVXgh8K12WKOB5N3Sic_Altd0KwJq-35cSK4lk0MfRT9NE_VtnnkK_mrajRcYD5IKaQKzZANsaNEraqhRMeY9cWt6nfC57mk.eyJ0aWQiOiIxYjdiZTBjMy1lNTliLTRhZDctODcyNC03MDUxZWEwN2IxN2EifQ==',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.66 Safari/537.36',
        'authority': 'api-hn01.linkedcare.cn:9001',
        'method': 'GET',
        'path': '/api/v1/office/option/IsCloudCallCenterEnabled',
        'scheme': 'https',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'clientid': 'c2de5046-27cf-4dc8-aba7-9cb37e08fe3c',
        'origin': 'https://bjhzck.linkedcare.cn',
        'referer': 'https://bjhzck.linkedcare.cn/',
        'requestid': '19B855BC-F141-4DD9-8B89-4F746DC50D37',
    }
    for eid in eventIDs:
        url_patient_info = f"https://api-hn01.linkedcare.cn:9001/api/v1/appointment/{eid}"
        res = s.get(url_patient_info, headers=headers)
        # print(res.content.decode("utf8"))
        print("startTime: ", res.json()["startTime"].split("T")[0].strip())
        print("patientID: ", res.json()["patientId"])
        patient_dic = {"startTime": res.json()["startTime"].split("T")[0].strip(), "patientID": res.json()["patientId"]}
        # patientIds.append(res.json()["patientId"])
        patientIds.append(patient_dic)
    s.close()
    print(f"will ACQ {len(patientIds)} patients data")
    return  patientIds

def get_patientInfo(i, url_patient_detail, starttime):
    # 请求每一个patient 页面，获取详细信息
    # https://bjhzck.linkedcare.cn/ares3/#/patient/info/406275/record
    driver.driver.get(url_patient_detail)
    # 获取数据
    time.sleep(0.5)
    pt_name = driver.get_text("css", "td > label.ng-binding")
    pt_num = driver.get_text("css", "#patient-info-base-wrap > div.panel.panel-default > div.panel-body > div:nth-child(1) > div.sub-panel-body > table > tbody > tr:nth-child(2) > td:nth-child(1) > span.notes-value.ng-binding")
    time.sleep(0.3)
    driver.click("css", "#patientContainer > div.patient-content-container.k-pane > div:nth-child(1) > div:nth-child(2) > div.patient-menu-bar-view > div > ul > li:nth-child(2) > span")
    date = starttime
    els_time = driver.locateElements("css", "#timeline > div > div.timeline-icon.bg-primary.ng-binding")
    # 就诊记录时间对应
    diagnostic = ""
    if els_time:
        for index, value in enumerate(els_time):
            c = value.text
            list_time = starttime.split("-")
            if c.split("\n")[1] in list_time[0] and c.split("\n")[0].split("月")[0] in list_time[1] and c.split("\n")[0].split("月")[1].split("日")[0] in list_time[2]:
                print("就诊记录时间匹配成功")
                diagnostic = driver.get_text("css", f"#timeline > div:nth-child({index+1}) > div.timeline-content > div.timeline-heading.clearfix.timeBox > table > tbody > tr > td:nth-child(1) > h3 > strong")

    dc_name = driver.get_text("css", "#timeline > div:nth-child(1) > div.timeline-content > div.timeline-body > ul > li:nth-child(2) > span:nth-child(1) > strong")
    project = driver.get_text("css", "#timeline > div:nth-child(1) > div.timeline-content > div.timeline-body > ul > li.ng-scope > span > strong")
    time.sleep(0.3)
    driver.click("css", "#patientContainer > div.patient-content-container.k-pane > div:nth-child(1) > div:nth-child(2) > div.patient-menu-bar-view > div > ul > li:nth-child(3) > span")
    # chargeorderPaging > table > tbody > tr:nth-child(1)
    # 消费时间对应
    els = driver.locateElements("css", "#chargeorderPaging > table > tbody > tr")
    order_cost = 0
    note = ""
    if els:
        for index, value in enumerate(els):
            content = value.text
            if starttime in content:
                print("消费时间匹配成功。。。")
                order_cost += float(driver.get_text("css", f"#chargeorderPaging > table > tbody > tr:nth-child({index+1}) > td:nth-child(9)"))
                note += driver.get_text("css", f"#chargeorderPaging > table > tbody > tr:nth-child({index+1}) > td:nth-child(12) > span")

    return [i, date, diagnostic, dc_name, pt_num, pt_name, project, order_cost, note]

regex = re.compile(".诊")
def clean_info(patientInfo):
    # [1, '7月17日', '14:30 - 16:00 复诊预约 预约 【合众齿科】', '朴珍荣(未知科室)', '22061215', '陈尚林', '[根管治疗]  ', '810.00', '']
    try:
        patientInfo[2] = regex.search(patientInfo[2]).group()
    except Exception as e:
        print("ignore error", e)
        patientInfo[2] = ""
    patientInfo[3] = patientInfo[3].split("(")[0]
    print(patientInfo)
    return patientInfo

def writeCSV(data:list):
    header = ['index', 'date', 'diagnostic', 'dc_name', 'pt_num', 'pt_name', 'project', 'order_cost', 'note']
    with open("result.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

if __name__ == '__main__':
    url_logon = "https://bjhzck.linkedcare.cn/LogOn"
    name = "蔡有菊"
    passwd = "a123456"
    logon(url_logon, name, passwd)
    eventIDs = get_eventID()
    patientIDs = get_patientID(eventIDs)

    # 请求每一个patient 页面，获取详细信息
    i = 1
    for pid in patientIDs:
        url_patient_detail = f"https://bjhzck.linkedcare.cn/ares3/#/patient/info/{pid['patientID']}/record"
        print(url_patient_detail)
        patientInfo = get_patientInfo(i, url_patient_detail, starttime=pid["startTime"] )
        patientInfo_clean = clean_info(patientInfo)
        i += 1
        patient_infos.append(patientInfo_clean)
    # 保存数据到CSV
    writeCSV(patient_infos)
    print("main routine exit ...")
