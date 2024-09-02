#to output information to the screen
import streamlit as st

#to connect to the openai resource
import openai

#to facilitate SQL calls
import sqlalchemy
from sqlalchemy import create_engine,text

#to facilitate diplaying of tabular data
import plotly.figure_factory as ff

#assign key info from Streamlit private variables
OPENAI_API_KEY=st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY
db_string=st.secrets["DB_STRING"]

#make tha page width wide
st.set_page_config(layout="wide")


#------------------------------------------
#provide prompt instructions as well as some sample database structure to draw on
multiline_str1 = """

given the following database table structure:

Table name: Volunteer

Description: 
Indicates that a constituent is a volunteer and contains volunteer-specific fields.

Fields:

Primary Key:
ID						uniqueidentifier

Fields:
Field			Field Type	Null		Notes	Description
EMERGENCYCONTACTNAME	nvarchar(255)	Default = ''	
EMERGENCYCONTACTPHONE	nvarchar(100)	Default = ''	
AVAILABILITYCOMMENT	nvarchar(4000)	Default = ''	
UNAVAILABLEFROM	datetime	yes	When a volunteer is not available
UNAVAILABLETO	datetime	yes	When a volunteer is not available
DATEADDED	datetime		Default = getdate()	Indicates the date this record was added.
DATECHANGED	datetime		Default = getdate()	Indicates the date this record was last changed.
TS	timestamp			Timestamp.
TSLONG	bigint (Computed)	yes	CONVERT(bigint, TS)	Numeric representation of the timestamp.


Foreign Keys:

Foreign Key	Field Type	Null	Notes	Description
ID	uniqueidentifier		CONSTITUENT.LOCALID	Primary Key.
SPONSORID	uniqueidentifier	yes	CONSTITUENT.LOCALID	Sponsoring Organization
ADDEDBYID	uniqueidentifier		CHANGEAGENT.ID	FK to CHANGEAGENT.
CHANGEDBYID	uniqueidentifier		CHANGEAGENT.ID	FK to CHANGEAGENT.

---------

Table name: Constituent

Description:
Every individual or organization, constituent or non-constituent, is represented by a row in the CONSTITUENT table. Each row in the CONSTITUENT table identifies that entity as an individual or organization, a constituent or non-constituent, and contains that entity's name and its various properties, such as gender or matching gift limits.

Primary Key:
ID						uniqueidentifier

Fields:
Field	Field Type	Null	Notes	Description
KEYNAME	nvarchar(100)		Default = ''	Last name for individuals, Org name for organizations.
KEYNAMEPREFIX	nvarchar(50)		Default = ''	For organizations, stores the name contents before the sort break slash.
FIRSTNAME	nvarchar(50)		Default = ''	For individuals, stores the first name.
MIDDLENAME	nvarchar(50)		Default = ''	For individuals, stores the middle name.
MAIDENNAME	nvarchar(100)		Default = ''	For individuals, stores the maiden name.
NICKNAME	nvarchar(50)		Default = ''	For individuals, stores the nickname.
SSN	nvarchar(4000)		Default = ''	For individuals, stores the SSN or other government ID.
SSNINDEX	nvarchar(24)	yes		
GENDERCODE	tinyint		Default = 0	0=Unknown, 1=Male, 2=Female
BIRTHDATE	UDT_FUZZYDATE		Default = '00000000'	For individuals, stores the date of birth.
ISINACTIVE	bit		Default = 0	Indicates whether or not the record is inactive.
GIVESANONYMOUSLY	bit		Default = 0	Indicates whether or not the record gives anonymously.
WEBADDRESS	UDT_WEBADDRESS		Default = ''	The constituent's web address.
PICTURE	varbinary	yes		A photo or emblem for this constituent.
PICTURETHUMBNAIL	varbinary	yes		
ISORGANIZATION	bit		Default = 0	Indicates whether a record is an organization.
NETCOMMUNITYMEMBER	bit		Default = 0	Indicates whether a record is a member of our online community.
DONOTMAIL	bit		Default = 0	Indicates whether a constituent does not want to be mailed at any address.
DONOTEMAIL	bit		Default = 0	Indicates whether a constituent does not want to be emailed at any email address.
DONOTPHONE	bit		Default = 0	Indicates whether a constituent does not want to be called at any phone number.
CUSTOMIDENTIFIER	nvarchar(100)		Default = ''	User-definable custom identifier.
SEQUENCEID	int			Identity column used to increment the default lookupid.
DATEADDED	datetime		Default = getdate()	Indicates the date this record was added.
DATECHANGED	datetime		Default = getdate()	Indicates the date this record was last changed.
TS	timestamp			Timestamp.
TSLONG	bigint (Computed)	yes	CONVERT(bigint, TS)	Numeric representation of the timestamp.
ISGROUP	bit		Default = 0	Indicates whether a record is a group
DISPLAYNAME	nvarchar(100)		Default = ''	Display name for households.
LOOKUPID	nvarchar(100) (Computed)	yes	(CASE LEN(CUSTOMIDENTIFIER) WHEN 0 THEN '8-' + CAST(SEQUENCEID AS nvarchar(20)) ELSE CUSTOMIDENTIFIER END)	Unique identifier that supports user defined values as well as system generated values.
ISCONSTITUENT	bit		Default = 1	Indicates if the record is a constituent for fundraising purposes.
AGE	int (Computed)	yes	dbo.UFN_AGEFROMFUZZYDATE(CONSTITUENT.BIRTHDATE, getdate())	For individuals, returns the age.
KEYNAMESOUNDEX	varchar(5) (Computed)	yes	soundex(KEYNAME)	The soundex value of the keyname field.
NAME	nvarchar(154) (Computed)	yes	CASE ISORGANIZATION WHEN 1 THEN CASE KEYNAMEPREFIX WHEN '' THEN KEYNAME ELSE KEYNAMEPREFIX + ' ' + KEYNAME END ELSE CASE ISGROUP WHEN 1 THEN CASE DISPLAYNAME WHEN '' THEN KEYNAME ELSE DISPLAYNAME END ELSE CASE FIRSTNAME WHEN '' THEN '' ELSE FIRSTNAME + ' ' END + CASE MIDDLENAME WHEN '' THEN '' ELSE LEFT(MIDDLENAME,1) + '. ' END + KEYNAME END END	Returns the constituent name (First + Middle Initial + Last (individuals), Prefix + Org name (orgs)).
GENDER	nvarchar(7) (Computed)	yes	CASE [GENDERCODE] WHEN 0 THEN N'Unknown' WHEN 1 THEN N'Male' WHEN 2 THEN N'Female' WHEN 3 THEN N'Other' END	
Foreign Keys
Foreign Key	Field Type	Null	Notes	Description
TITLECODEID	uniqueidentifier	yes	TITLECODE.LOCALID	FK to TITLECODE
SUFFIXCODEID	uniqueidentifier	yes	SUFFIXCODE.LOCALID	FK to SUFFIXCODE
MARITALSTATUSCODEID	uniqueidentifier	yes	MARITALSTATUSCODE.LOCALID	FK to MARITALSTATUSCODE
ADDEDBYID	uniqueidentifier		CHANGEAGENT.ID	FK to CHANGEAGENT.
CHANGEDBYID	uniqueidentifier		CHANGEAGENT.ID	FK to CHANGEAGENT.
TITLE2CODEID	uniqueidentifier	yes	TITLECODE.LOCALID	FK to TITLECODE
SUFFIX2CODEID	uniqueidentifier	yes	SUFFIXCODE.LOCALID	FK to SUFFIXCODE
GENDERCODEID	uniqueidentifier	yes	GENDERCODE.ID	

---------

Table name: ADDRESS

Primary Key	
ID					uniqueidentifier

Fields:

Field	Field Type	Null	Notes	Description
ISPRIMARY	bit		Default = 0	Indicates this address is the primary address.
DONOTMAIL	bit		Default = 0	Indicates this address should not receive mailings.
STARTDATE	UDT_MONTHDAY		Default = '0000'	For seasonal address types only; DD/MM start date of when this address should be considered for mailings.
ENDDATE	UDT_MONTHDAY		Default = '0000'	For seasonal address types only; DD/MM end date of when this address should be considered for mailings.
ADDRESSBLOCK	nvarchar(150)		Default = ''	Contains the address lines.
CITY	nvarchar(50)		Default = ''	Contains the address city.
POSTCODE	nvarchar(12)		Default = ''	Contains the address post code.
CART	nvarchar(10)		Default = ''	Contains the address carrier route (CART).
DPC	nvarchar(8)		Default = ''	Contains the address delivery point code
LOT	nvarchar(5)		Default = ''	Contains the address LOT.
SEQUENCE	int		Default = 0	Stores the user-defined sequence for addresses on a constituent.
DATEADDED	datetime		Default = getdate()	Indicates the date this record was added.
DATECHANGED	datetime		Default = getdate()	Indicates the date this record was last changed.
TS	timestamp			Timestamp.
TSLONG	bigint (Computed)	yes	CONVERT(bigint, TS)	Numeric representation of the timestamp.
DESCRIPTION	nvarchar(300) (Computed)	yes	dbo.UFN_ADDRESS_TRANSLATE(ID)	Provides a translation field for the address record
HISTORICALSTARTDATE	date	yes		Indicates the date that the constituent started using this address.
HISTORICALENDDATE	date	yes		Indicates the date that the constituent stopped using this address.
ISCONFIDENTIAL	bit		Default = 0	Indicates this address is confidential.
Foreign Keys
Foreign Key	Field Type	Null	Notes	Description
CONSTITUENTID	uniqueidentifier		CONSTITUENT.LOCALID	FK to CONSTITUENT
ADDRESSTYPECODEID	uniqueidentifier	yes	ADDRESSTYPECODE.ID	FK to ADDRESSTYPECODE
COUNTRYID	uniqueidentifier		COUNTRY.LOCALID	FK to COUNTRY
STATEID	uniqueidentifier	yes	STATE.LOCALID	FK to STATE
ADDEDBYID	uniqueidentifier		CHANGEAGENT.ID	FK to CHANGEAGENT.
CHANGEDBYID	uniqueidentifier		CHANGEAGENT.ID	FK to CHANGEAGENT.
RELATIONSHIPID	uniqueidentifier	yes	RELATIONSHIP.ID	FK to RELATIONSHIP
DONOTMAILREASONCODEID	uniqueidentifier	yes	DONOTMAILREASONCODE.ID	FK to DONOTMAILREASONCODE

---------

Table name: DESIGNATION

Primary Key	
ID	uniqueidentifier

Fields:

Field	Field Type	Null	Notes	Description
PROJECTCODE	nvarchar(100)		Default = ''	GL project code
ISACTIVE	bit		Default = 1	Indicates whether or not the designation is active.
USERID	nvarchar(512)		Default = ''	The lookup ID used for searching for this designation.
VANITYNAME	nvarchar(512)		Default = ''	User entered field for a friendly name.
DATEADDED	datetime		Default = getdate()	Indicates the date this record was added.
DATECHANGED	datetime		Default = getdate()	Indicates the date this record was last changed.
TS	timestamp			Timestamp.
TSLONG	bigint (Computed)	yes	CONVERT(bigint, TS)	Numeric representation of the timestamp.
ACCOUNTNUMBER	nvarchar(100)		Default = ''	GL account number
STARTDATE	datetime	yes		Start date associated with this designation
ENDDATE	datetime	yes		End date associated with this designation
ISREVENUEDESIGNATION	bit		Default = 1	Indicates if this designation is accepting revenue.
SYSTEMGENERATED	bit		Default = 0	
NAME	nvarchar(512)		Default = ''

---------

create the sql to for the following question - 
limit prose


"""
#------------------------------------------
#provide heading:
st.header("Automated Report Generator (beta)")


table_collection = st.radio(
    "Select a primary data source:",
    ["Constituents", "Revenue", "Prospects", "Campaigns", "Designations", "Volunteers"]
)

#-------------------------------------------

#if there's a prompt then process it
if prompt := st.chat_input(placeholder="Enter your prompt here..."):
    st.chat_message("user").write(prompt)

    messages = [{"role": "system", "content":
        """
        You are an sql command writer. You only produce answers in the form of sql commands that can be executed on a database. 
        Do not use the LIMIT command to limit any results.
        Do not provide any explanations of how you came up with the result. 
        Only provide the sql statement inself.
        """}]



    #--------------------------------
    #OPENAI - translate the user's prompt to SQL statement using model: chatGPT 3.5 model

    messages.append(
        {"role": "user", "content": multiline_str1 + prompt},
    )

    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    #store the SQL response
    reply = chat.choices[0].message.content

    #print the response to the terminal for debugging
    print(f"<<<{reply}>>>")

    st.write(reply)

    # --------------------------------

    # # --------------------------------------------
    # # SQL CONNECTION METHOD using SQLAlchemy 
    # my_conn = create_engine(db_string)
    # my_conn = my_conn.connect()

    # #attempt at executing the SQL on the database
    # try:
    #     my_data = list(my_conn.execute(text(reply)))

    # #if the SQL was unsuccessful for any reason
    # except:
    #     print("some error happened")
    #     st.write("Sorry, I was unable to generate results for this query. Please rephrase.")

    #     #close the database connection
    #     my_conn.close()

    # else:

    #     #provide the option to show/hide the SQL statement 
    #     with st.expander("Show/hide SQL"):
    #         st.write(reply)

    #     # Store the result in a multidimensional array
    #     table_data = [list(row) for row in my_data]

    #     #now that we have the data inside table_data, we can close the connection
    #     my_conn.close()

    #     data_length = len(table_data)

    #     if data_length > 0:

    #         #display results in terminal for debugging purposes
    #         print("This is the array:")
    #         for row in table_data:
    #             print(row)

    #         #----------------------------------------------------
    #         #create and display the table from the returned SQL results
    #         fig = ff.create_table(table_data, height_constant=60)
    #         fig.layout.margin.update({'t': 50, 'b': 100})
    #         st.plotly_chart(fig, use_container_width=True)

    #     else:
    #         print("No results were found for that query.")
    #         st.write("No results were found for that query.")

    #     my_conn.close()

