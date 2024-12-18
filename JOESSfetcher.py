# currently not functional due to JOESS dynamic loading
import requests
from bs4 import BeautifulSoup as soup

# specify the API URL without the offset
target_url = "https://joess.mst.edu/psc/csprdr/EMPLOYEE/SA/c/NUI_FRAMEWORK.PT_AGSTARTPAGE_NUI.GBL?CONTEXTIDPARAMS=TEMPLATE_ID%3aPTPPNAVCOL&scname=ADMN_STUDENT_MANAGE_CLASSES&PanelCollapsible=Y&PTPPB_GROUPLET_ID=UM_STDNT_MANAGE_CLASSES&CRefName=ADMN_NAVCOLL_6&AJAXTransfer=Y"

from selenium import webdriver
import pandas as pd
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
geckodriver_path = "/snap/bin/geckodriver"
driver_service = webdriver.FirefoxService(executable_path=geckodriver_path)
options = Options()
options.add_argument('--headless')
driver = webdriver.Firefox(service=driver_service, options=options)

driver.get(target_url)
btn = driver.find_element(By.CLASS_NAME, "PSGROUPBOXLABEL").click()
btn = driver.find_element(By.CSS_SELECTOR, "#PTGP_STEP_DVW_PTGP_STEP_LABEL\$1").click()
btn = driver.find_element(By.ID, "PTGP_STEP_DVW_PTGP_STEP_LABEL$1").click()
df = pd.read_html(driver.page_source)[0]
print(df)
classes = soup.find_all("div", id=soup.findAll('div', id=lambda x: x and str(x).startswith('CRSE')))

df.to_csv("data.csv", index=False)
driver.quit()

