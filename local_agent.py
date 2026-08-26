import time
import re
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

app = Flask(__name__)

def execute_panel_credit_action(agent_name, target_username, amount_str, action_type="dp"):
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        original_window = driver.current_window_handle
        target_tab_found = False
        
        # 1. Cari tab browser berdasarkan nama agen
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            time.sleep(1)
            try:
                agent_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{agent_name}')]")
                if agent_element:
                    target_tab_found = True
                    break
            except:
                continue
                
        if not target_tab_found:
            driver.switch_to.window(original_window)
            return {"status": False, "error": f"Tab dengan agen {agent_name} tidak ditemukan!"}

        # Pastikan berada di halaman Credit (1.6 Credit) terlebih dahulu
        try:
            credit_menu = driver.find_element(By.XPATH, "//*[contains(text(), '1.6 Credit')]")
            driver.execute_script("arguments[0].click();", credit_menu)
            time.sleep(1)
        except:
            pass

        # 2. Masukkan username target ke kotak pencarian
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username/First/Last Name']"))
        )
        search_box.clear()
        search_box.send_keys(target_username)
        time.sleep(2)

        # 3. Ambil nilai credit lama
        credit_cell_xpath = "//td[contains(@id, '-credit')]//span[contains(@class, 'cursor-pointer')]"
        try:
            credit_cell = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, credit_cell_xpath))
            )
            old_credit_str = credit_cell.text.strip()
        except:
            old_credit_str = "0"

        input_val = float(amount_str) if amount_str else 0.0

        # === JIKA DP ===
        if action_type == "dp":
            driver.execute_script("arguments[0].click();", credit_cell)
            time.sleep(1)
            
            current_credit_val = float(old_credit_str) if old_credit_str else 0.0
            final_val = current_credit_val + input_val
            final_input_value = f"{final_val:.2f}" if "." in str(final_val) else str(int(final_val))
            
            input_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'dialog')]//input[@type='text']"))
            )
            driver.execute_script("arguments[0].value = '';", input_box)
            input_box.click()
            input_box.send_keys(Keys.CONTROL + "a")
            input_box.send_keys(Keys.BACK_SPACE)
            
            driver.execute_script(f"arguments[0].value = '{final_input_value}';", input_box)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", input_box)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", input_box)
            time.sleep(1)
            
            save_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Save']"))
            )
            driver.execute_script("arguments[0].click();", save_button)
            time.sleep(3)
            
            updated_cell = driver.find_element(By.XPATH, credit_cell_xpath)
            new_credit = updated_cell.text.strip()
            
            search_box.click()
            search_box.clear()
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.BACK_SPACE)
            time.sleep(1)

            return {
                "status": True,
                "method": "Credit",
                "old_credit": old_credit_str,
                "processed_amount": amount_str,
                "new_credit": new_credit
            }

        # === JIKA WD ===
        elif action_type == "wd":
            success_wd_credit = False
            current_credit_val = float(old_credit_str) if old_credit_str else 0.0

            if current_credit_val > 0 and current_credit_val >= input_val:
                try:
                    driver.execute_script("arguments[0].click();", credit_cell)
                    time.sleep(1)
                    
                    final_val = current_credit_val - input_val
                    final_input_value = f"{final_val:.2f}" if "." in str(final_val) else str(int(final_val))
                    
                    input_box = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'dialog')]//input[@type='text']"))
                    )
                    driver.execute_script("arguments[0].value = '';", input_box)
                    input_box.click()
                    input_box.send_keys(Keys.CONTROL + "a")
                    input_box.send_keys(Keys.BACK_SPACE)
                    
                    driver.execute_script(f"arguments[0].value = '{final_input_value}';", input_box)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", input_box)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", input_box)
                    time.sleep(1)
                    
                    save_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Save']"))
                    )
                    driver.execute_script("arguments[0].click();", save_button)
                    time.sleep(3)
                    
                    error_msg = driver.find_elements(By.XPATH, "//*[contains(@class, 'error') or contains(text(), 'not able')]")
                    if not error_msg:
                        success_wd_credit = True
                    else:
                        try:
                            cancel_btn = driver.find_element(By.XPATH, "//button[normalize-space()='Cancel']")
                            driver.execute_script("arguments[0].click();", cancel_btn)
                        except:
                            pass
                except:
                    success_wd_credit = False

            if not success_wd_credit:
                try:
                    transfer_menu = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '3.1 Transfer')]"))
                    )
                    driver.execute_script("arguments[0].click();", transfer_menu)
                    time.sleep(2)

                    tf_search_box = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username/First/Last Name']"))
                    )
                    tf_search_box.clear()
                    tf_search_box.send_keys(target_username)
                    time.sleep(2)

                    total_balance_cell = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//td[contains(@id, 'totalBalance') or @aria-describedby*='totalBalance']//span[contains(@class, 'cursor-pointer')] | //tr[1]/td[5]//span[contains(@class, 'cursor-pointer')] | //tr[1]/td[6]//span[contains(@class, 'cursor-pointer')] | //td//span[contains(@class, 'cursor-pointer')]"))
                    )
                    driver.execute_script("arguments[0].click();", total_balance_cell)
                    time.sleep(1)

                    tf_input_box = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'dialog')]//input[@type='text']"))
                    )
                    
                    minus_amount = f"-{amount_str}"
                    driver.execute_script("arguments[0].value = '';", tf_input_box)
                    tf_input_box.click()
                    tf_input_box.send_keys(Keys.CONTROL + "a")
                    tf_input_box.send_keys(Keys.BACK_SPACE)
                    
                    driver.execute_script(f"arguments[0].value = '{minus_amount}';", tf_input_box)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", tf_input_box)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", tf_input_box)
                    time.sleep(1)

                    tf_transfer_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Transfer' or normalize-space()='Save']"))
                    )
                    driver.execute_script("arguments[0].click();", tf_transfer_button)
                    time.sleep(3)

                    transfer_error = driver.find_elements(By.XPATH, "//*[contains(@class, 'error') or contains(text(), 'not able') or contains(text(), 'insufficient') or contains(text(), 'fail')]")
                    if transfer_error:
                        try:
                            tf_cancel_btn = driver.find_element(By.XPATH, "//button[normalize-space()='Cancel']")
                            driver.execute_script("arguments[0].click();", tf_cancel_btn)
                        except:
                            pass
                        
                        credit_menu_back = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '1.6 Credit')]"))
                        )
                        driver.execute_script("arguments[0].click();", credit_menu_back)
                        time.sleep(2)
                        return {"status": False, "error": "Target tidak memiliki cukup credit untuk withdraw!"}

                except Exception as ex:
                    try:
                        credit_menu_back = driver.find_element(By.XPATH, "//*[contains(text(), '1.6 Credit')]")
                        driver.execute_script("arguments[0].click();", credit_menu_back)
                    except:
                        pass
                    return {"status": False, "error": "Target tidak memiliki cukup credit untuk withdraw!"}

                credit_menu_back = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '1.6 Credit')]"))
                )
                driver.execute_script("arguments[0].click();", credit_menu_back)
                time.sleep(2)

                return {
                    "status": True,
                    "method": "Transfer (Auto Minus)",
                    "old_credit": old_credit_str,
                    "processed_amount": f"-{amount_str}",
                    "new_credit": "Berhasil via Transfer"
                }

            updated_cell = driver.find_element(By.XPATH, credit_cell_xpath)
            new_credit = updated_cell.text.strip()
            
            search_box.click()
            search_box.clear()
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.BACK_SPACE)
            time.sleep(1)

            return {
                "status": True,
                "method": "Credit",
                "old_credit": old_credit_str,
                "processed_amount": amount_str,
                "new_credit": new_credit
            }

    except Exception as e:
        return {"status": False, "error": str(e)}

@app.route('/run-selenium', methods=['POST'])
def run_selenium_endpoint():
    data = request.json
    action_type = data.get("action_type")
    agent_name = data.get("agent_name")
    target_username = data.get("target_username")
    amount = data.get("amount")
    
    print(f"📥 Menerima Perintah dari Cloud: {action_type.upper()} | Agen: {agent_name} | Target: {target_username} | Jumlah: {amount}")
    
    # Eksekusi fungsi Selenium lokal Anda
    result = execute_panel_credit_action(agent_name, target_username, amount, action_type=action_type)
    return jsonify(result)

if __name__ == '__main__':
    print("🤖 LOCAL AGENT SIAP MENERIMA PERINTAH DARI CLOUD!")
    app.run(host='0.0.0.0', port=5000)
