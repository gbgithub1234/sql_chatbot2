#to output information to the screen
import streamlit as st

#to connect to the openai resource
import openai

#to facilitate SQL calls
import sqlalchemy
from sqlalchemy import create_engine,text

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

/* Create the tables */
CREATE TABLE productlines (
  productLine varchar(50),
  textDescription varchar(4000) DEFAULT NULL,
  htmlDescription mediumtext,
  image mediumblob,
  PRIMARY KEY (productLine)
);

CREATE TABLE products (
  productCode varchar(15),
  productName varchar(70) NOT NULL,
  productLine varchar(50) NOT NULL,
  productScale varchar(10) NOT NULL,
  productVendor varchar(50) NOT NULL,
  productDescription text NOT NULL,
  quantityInStock smallint(6) NOT NULL,
  buyPrice decimal(10,2) NOT NULL,
  MSRP decimal(10,2) NOT NULL,
  PRIMARY KEY (productCode),
  FOREIGN KEY (productLine) REFERENCES productlines (productLine)
);

CREATE TABLE offices (
  officeCode varchar(10),
  city varchar(50) NOT NULL,
  phone varchar(50) NOT NULL,
  addressLine1 varchar(50) NOT NULL,
  addressLine2 varchar(50) DEFAULT NULL,
  state varchar(50) DEFAULT NULL,
  country varchar(50) NOT NULL,
  postalCode varchar(15) NOT NULL,
  territory varchar(10) NOT NULL,
  PRIMARY KEY (officeCode)
);

CREATE TABLE employees (
  employeeNumber int,
  lastName varchar(50) NOT NULL,
  firstName varchar(50) NOT NULL,
  extension varchar(10) NOT NULL,
  email varchar(100) NOT NULL,
  officeCode varchar(10) NOT NULL,
  reportsTo int DEFAULT NULL,
  jobTitle varchar(50) NOT NULL,
  PRIMARY KEY (employeeNumber),
  FOREIGN KEY (reportsTo) REFERENCES employees (employeeNumber),
  FOREIGN KEY (officeCode) REFERENCES offices (officeCode)
);

CREATE TABLE customers (
  customerNumber int,
  customerName varchar(50) NOT NULL,
  contactLastName varchar(50) NOT NULL,
  contactFirstName varchar(50) NOT NULL,
  phone varchar(50) NOT NULL,
  addressLine1 varchar(50) NOT NULL,
  addressLine2 varchar(50) DEFAULT NULL,
  city varchar(50) NOT NULL,
  state varchar(50) DEFAULT NULL,
  postalCode varchar(15) DEFAULT NULL,
  country varchar(50) NOT NULL,
  salesRepEmployeeNumber int DEFAULT NULL,
  creditLimit decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (customerNumber),
  FOREIGN KEY (salesRepEmployeeNumber) REFERENCES employees (employeeNumber)
);

CREATE TABLE payments (
  customerNumber int,
  checkNumber varchar(50) NOT NULL,
  paymentDate date NOT NULL,
  amount decimal(10,2) NOT NULL,
  PRIMARY KEY (customerNumber,checkNumber),
  FOREIGN KEY (customerNumber) REFERENCES customers (customerNumber)
);

CREATE TABLE orders (
  orderNumber int,
  orderDate date NOT NULL,
  requiredDate date NOT NULL,
  shippedDate date DEFAULT NULL,
  status varchar(15) NOT NULL,
  comments text,
  customerNumber int NOT NULL,
  PRIMARY KEY (orderNumber),
  FOREIGN KEY (customerNumber) REFERENCES customers (customerNumber)
);

CREATE TABLE orderdetails (
  orderNumber int,
  productCode varchar(15) NOT NULL,
  quantityOrdered int NOT NULL,
  priceEach decimal(10,2) NOT NULL,
  orderLineNumber smallint(6) NOT NULL,
  PRIMARY KEY (orderNumber,productCode),
  FOREIGN KEY (orderNumber) REFERENCES orders (orderNumber),
  FOREIGN KEY (productCode) REFERENCES products (productCode)
);


create the sql to for the following question - 
limit prose


"""
#------------------------------------------
#provide heading:
st.header("AI-powered Report Generator (Tabular)")

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
    # --------------------------------


    # --------------------------------------------
    # SQL CONNECTION METHOD using SQLAlchemy 
    my_conn = create_engine(db_string)
    my_conn = my_conn.connect()

    #attempt at executing the SQL on the database
    try:
        my_data = list(my_conn.execute(text(reply)))

    #if the SQL was unsuccessful for any reason
    except:
        print("some error happened")
        st.write("Sorry, I was unable to generate results for this query. Please rephrase.")

        my_conn.close()

    else:

        with st.expander("Show/hide SQL"):
            st.write(reply)


        # Store the result in a multidimensional array
        table_data = [list(row) for row in my_data]

        # now that we have the data inside table_data, we can close the connection
        my_conn.close()

        data_length = len(table_data)

        if data_length > 0:

            print("This is the array:")
            for row in table_data:
                print(row)

            #----------------------------------------------------
            import plotly.figure_factory as ff
            fig = ff.create_table(table_data, height_constant=60)
            fig.layout.margin.update({'t': 50, 'b': 100})
            st.plotly_chart(fig, use_container_width=True)

        else:
            print("No results were found for that query.")
            st.write("No results were found for that query.")

        my_conn.close()

