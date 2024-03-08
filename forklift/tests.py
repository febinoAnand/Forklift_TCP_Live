from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

try:
    driver.get("http://localhost:8000") 

    username_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "username")))
    password_field = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.TAG_NAME, "button")

    username_field.send_keys("admin")
    password_field.send_keys("admin")
    submit_button.click()

    WebDriverWait(driver, 10).until(EC.url_contains("devicedashboard"))

    print("Login successful!")
except Exception as e:
    print("An error occurred during login:", e)
finally:
    driver.quit()
