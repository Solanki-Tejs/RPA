*** Settings ***
Documentation     Dedicated RPA Bot to scrape and export processed/approved rental applications and their properties to CSV
Library           SeleniumLibrary
Library           ../libraries/RentalAnalyzer.py

*** Variables ***
${SERVER}         http://127.0.0.1:5000
${BROWSER}        Chrome
${DELAY}          0.5
${USER_EMAIL}     user@gamil.com
${USER_PASS}      user123
${TASK_PARAM}     Approved Only

*** Test Cases ***
Seller Export Applications To CSV
    [Documentation]    Bot logs into Seller Dashboard, navigates to Processed Applications, extracts candidate and property info, and exports to CSV.
    ${options}=    Set Variable    add_argument("--disable-popup-blocking"); add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "profile.password_manager_leak_detection": False})
    Open Browser    ${SERVER}/login    ${BROWSER}    options=${options}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    
    # Seller Login
    Wait Until Page Contains Element    name=email
    Input Text    name=email    ${USER_EMAIL}
    Input Text    name=password    ${USER_PASS}
    Submit Form
    
    # Navigate to Seller Dashboard
    Go To    ${SERVER}/dashboard/seller
    
    # Switch to Processed Applications Tab
    Wait Until Page Contains Element    xpath=//*[self::a or self::button][contains(text(), 'Processed Applications')]
    Click Element    xpath=//*[self::a or self::button][contains(text(), 'Processed Applications')]
    Wait Until Element Is Visible    xpath=//div[@id='tab-processed']
    
    # Initialize the CSV export file
    Initialize Export Csv
    
    # Count rows in Processed Applications table
    ${rows}=    Get Element Count    xpath=//div[@id='tab-processed']//tbody/tr
    Run Keyword If    ${rows} == 0    Log    No processed applications found to export.
    
    # Iterate and scrape each row
    FOR    ${i}    IN RANGE    1    ${rows} + 1
        ${row_xpath}=    Set Variable    xpath=(//div[@id='tab-processed']//tbody/tr)[${i}]
        Scrape Row And Export    ${row_xpath}
    END
    
    Log    Exported processed applications successfully to CSV.
    Close Browser

*** Keywords ***
Scrape Row And Export
    [Arguments]    ${row_xpath}
    ${applicant_name}=    Get Text    ${row_xpath}//td[1]//strong
    ${applicant_cell}=    Get Text    ${row_xpath}//td[1]
    ${property_title}=    Get Text    ${row_xpath}//td[2]//strong
    ${rent_amount}=       Get Text    ${row_xpath}//span[@class='rent-amount']
    ${emp_status}=        Get Text    ${row_xpath}//span[@class='app-emp-status']
    ${monthly_income}=    Get Text    ${row_xpath}//span[@class='app-income']
    ${status_cell}=       Get Text    ${row_xpath}//td[4]
    
    Append Scraped Application    ${applicant_name}    ${applicant_cell}    ${property_title}    ${rent_amount}    ${emp_status}    ${monthly_income}    ${status_cell}    ${TASK_PARAM}
