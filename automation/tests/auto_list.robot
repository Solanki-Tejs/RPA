*** Settings ***
Documentation     RPA Bot to Automatically List a Property on Plotify
Library           SeleniumLibrary
Library           OperatingSystem
Library           String

*** Variables ***
${SERVER}             http://127.0.0.1:5000
${BROWSER}            Chrome
${DELAY}              0.5
${USER_EMAIL}         user@gamil.com
${USER_PASS}          user123
${TASK_PARAM}         
${S_TITLE}            Beautiful Property
${S_PRICE}            25000
${S_CAT}              Rent
${S_LOC}              City Center
${S_DESC}             A great place.
${S_BEDS}             2
${S_BATHS}            2
${S_AREA}             1200 sqft
${S_TYPE}             Apartment
${S_OWNER}            Seller
${S_PHONE}            +91 9999999999
${S_EMAIL}            seller@example.com
${S_AM}               Parking, Security
${S_MAP}              
${S_FLOOR}            1
${S_TFLOORS}          5
${S_FURN}             Semi Furnished
${S_FACING}           North
${S_IMG}              
${S_ID}               
${S_OWN}              

*** Test Cases ***
Auto List Property
    [Documentation]    Bot logs in as a seller and posts a new property listing using the Seller Profile.
    ${options}=    Set Variable    add_argument("--disable-popup-blocking"); add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "profile.password_manager_leak_detection": False})
    Open Browser    ${SERVER}/login    ${BROWSER}    options=${options}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    
    # Login as seller using credentials saved in Plotify settings
    Wait Until Page Contains Element    name=email
    Input Text    name=email    ${USER_EMAIL}
    Input Text    name=password    ${USER_PASS}
    Submit Form
    
    # Wait for login to complete
    Wait Until Page Contains Element    xpath=//a[@href='/logout']
    
    # Go to sell page
    Go To    ${SERVER}/sell
    
    # Fill Application Form using our DB Profile Variables dynamically passed from the RPA Dashboard!
    Wait Until Page Contains Element    name=title
    Input Text    name=title             ${S_TITLE}
    Input Text    name=price             ${S_PRICE}
    Select From List By Label    name=category    ${S_CAT}
    Input Text    name=location          ${S_LOC}
    Input Text    name=description       ${S_DESC}
    Input Text    name=bedrooms          ${S_BEDS}
    Input Text    name=bathrooms         ${S_BATHS}
    Input Text    name=area              ${S_AREA}
    Select From List By Label    name=type    ${S_TYPE}
    
    Input Text    name=owner_name        ${S_OWNER}
    Input Text    name=phone             ${S_PHONE}
    Input Text    name=email             ${S_EMAIL}
    
    Input Text    name=map_link          ${S_MAP}
    Input Text    name=floor             ${S_FLOOR}
    Input Text    name=total_floors      ${S_TFLOORS}
    Select From List By Label    name=furnishing    ${S_FURN}
    Select From List By Label    name=facing    ${S_FACING}
    
    # Amenities (Handle checkboxes if they are named 'amenities')
    @{AM_LIST}=    Split String    ${S_AM}    ,
    FOR    ${am}    IN    @{AM_LIST}
        ${am_stripped}=    Strip String    ${am}
        Run Keyword If    '${am_stripped}' != ''    Run Keyword And Ignore Error    Select Checkbox    xpath=//input[@name='amenities' and @value='${am_stripped}']
    END
    
    # Upload Real Files from DB Paths
    Run Keyword If    '${S_IMG}' != ''    Choose File    name=images    ${S_IMG}
    Run Keyword If    '${S_ID}' != ''    Choose File    name=identity_doc    ${S_ID}
    Run Keyword If    '${S_OWN}' != ''    Choose File    name=ownership_doc    ${S_OWN}
    
    # Submit Application
    Submit Form
    
    # Wait for redirect back to sell page (meaning success)
    Wait Until Page Contains Element    xpath=//button[@type='submit' and contains(text(), 'Post Property for Review')]
    Close Browser
