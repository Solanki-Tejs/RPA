*** Settings ***
Documentation     RPA Bot to Automatically List Properties in Bulk from a CSV file
Library           SeleniumLibrary
Library           OperatingSystem
Library           String
Library           ../libraries/ReadCsv.py

*** Variables ***
${SERVER}             http://127.0.0.1:5000
${BROWSER}            Chrome
${DELAY}              0.5
${USER_EMAIL}         user@gamil.com
${USER_PASS}          user123
${CSV_FILE}           
${S_OWNER}            Seller
${S_PHONE}            +91 9999999999
${S_EMAIL}            seller@example.com

*** Test Cases ***
Bulk List Properties
    [Documentation]    Bot logs in as a seller and posts multiple property listings from a CSV file.
    
    # Check if CSV file is provided
    Run Keyword If    '${CSV_FILE}' == ''    Fail    No CSV file provided!
    
    # Read CSV Data
    ${data}=    Read Csv File    ${CSV_FILE}
    
    # Login
    ${options}=    Set Variable    add_argument("--disable-popup-blocking"); add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "profile.password_manager_leak_detection": False})
    Open Browser    ${SERVER}/login    ${BROWSER}    options=${options}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    
    Wait Until Page Contains Element    name=email
    Input Text    name=email    ${USER_EMAIL}
    Input Text    name=password    ${USER_PASS}
    Submit Form
    
    # Wait for login to complete (redirect to home/dashboard)
    Wait Until Page Contains Element    xpath=//a[@href='/logout']
    
    # Loop over CSV rows
    FOR    ${row}    IN    @{data}
        Go To    ${SERVER}/sell
        
        Wait Until Page Contains Element    name=title
        
        # Fill Application Form using CSV columns dynamically
        ${title}=    Set Variable If    'Title' in ${row}    ${row['Title']}    Bulk Property
        ${price}=    Set Variable If    'Price' in ${row}    ${row['Price']}    10000
        ${cat}=      Set Variable If    'Category' in ${row}    ${row['Category']}    Rent
        ${loc}=      Set Variable If    'Location' in ${row}    ${row['Location']}    City
        ${desc}=     Set Variable If    'Description' in ${row}    ${row['Description']}    Good property
        ${beds}=     Set Variable If    'Bedrooms' in ${row}    ${row['Bedrooms']}    2
        ${baths}=    Set Variable If    'Bathrooms' in ${row}    ${row['Bathrooms']}    2
        ${area}=     Set Variable If    'Area' in ${row}    ${row['Area']}    1000
        ${type}=     Set Variable If    'Type' in ${row}    ${row['Type']}    Apartment
        ${floor}=    Set Variable If    'Floor' in ${row}    ${row['Floor']}    1
        ${tfloors}=  Set Variable If    'TotalFloors' in ${row}    ${row['TotalFloors']}    5
        ${furn}=     Set Variable If    'Furnishing' in ${row}    ${row['Furnishing']}    Semi Furnished
        ${facing}=   Set Variable If    'Facing' in ${row}    ${row['Facing']}    North
        ${am}=       Set Variable If    'Amenities' in ${row}    ${row['Amenities']}    Parking
        ${map_link}=    Set Variable If    'MapLink' in ${row}      ${row['MapLink']}      
        ${img}=         Set Variable If    'ImagePath' in ${row}    ${row['ImagePath']}    
        ${own}=         Set Variable If    'OwnershipProof' in ${row}   ${row['OwnershipProof']}   
        Input Text    name=title             ${title}
        Input Text    name=price             ${price}
        Select From List By Label    name=category    ${cat}
        Input Text    name=location          ${loc}
        Input Text    name=description       ${desc}
        Input Text    name=bedrooms          ${beds}
        Input Text    name=bathrooms         ${baths}
        Input Text    name=area              ${area}
        Select From List By Label    name=type    ${type}
        Input Text    name=map_link          ${map_link}
        
        Input Text    name=owner_name        ${S_OWNER}
        Input Text    name=phone             ${S_PHONE}
        Input Text    name=email             ${S_EMAIL}
        
        Input Text    name=floor             ${floor}
        Input Text    name=total_floors      ${tfloors}
        Select From List By Label    name=furnishing    ${furn}
        Select From List By Label    name=facing    ${facing}
        
        # Amenities (Handle checkboxes if they are named 'amenities')
        @{AM_LIST}=    Split String    ${am}    ,
        FOR    ${a}    IN    @{AM_LIST}
            ${a_stripped}=    Strip String    ${a}
            Run Keyword If    '${a_stripped}' != ''    Run Keyword And Ignore Error    Select Checkbox    xpath=//input[@name='amenities' and @value='${a_stripped}']
        END
        
        # Upload Real Files from Local Computer if path is provided
        Run Keyword If    '${img}' != ''    Run Keyword And Ignore Error    Choose File    name=images    ${img}
        Run Keyword If    '${own}' != ''    Run Keyword And Ignore Error    Choose File    name=ownership_doc    ${own}
        
        # Upload Identity Doc from static profile data
        Run Keyword If    '${S_ID}' != ''    Run Keyword And Ignore Error    Choose File    name=identity_doc    ${S_ID}
        
        # Submit Application
        Submit Form
        
        # Wait for redirect back to sell page (meaning success)
        Wait Until Page Contains Element    xpath=//button[@type='submit' and contains(text(), 'Post Property for Review')]
    END
    
    Close Browser
