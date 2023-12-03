import streamlit as st
import openai
# import mysql.connector

import sqlalchemy
from sqlalchemy import create_engine

# import plotly.express as px
# import pandas as pd


OPENAI_API_KEY=st.secrets["OPENAI_API_KEY"]
db_string=st.secrets["DB_STRING"]

openai.api_key = OPENAI_API_KEY

#------------------------------------------
# engine = sqlalchemy.create_engine(db_string)

#------------------------------------------
#TESTING

# IMPORT THE SQALCHEMY LIBRARY's CREATE_ENGINE METHOD
# from sqlalchemy import create_engine

# DEFINE THE DATABASE CREDENTIALS
user = 'u848738634_gbuser1'
password = '8DfU%#7gNbFf$U-'
host = '31.170.160.103'
port = 3306
database = 'u848738634_aitest1'


# PYTHON FUNCTION TO CONNECT TO THE MYSQL DATABASE AND
# RETURN THE SQLACHEMY ENGINE OBJECT
def get_connection():
    return create_engine(
        url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            user, password, host, port, database
        )
    )


if __name__ == '__main__':

    try:

        # GET THE CONNECTION OBJECT (ENGINE) FOR THE DATABASE
        engine = get_connection()
        print(
            f"Connection to the {host} for user {user} created successfully.")
    except Exception as ex:
        print("Connection could not be made due to the following error: \n", ex)






#-------------------------------------------


#-------------------------------------------

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
# TESTING




#------------------------------------------

st.header("Table Output Report Generator 1.0 (beta)")

st.chat_input(placeholder="Enter your prompt here...")

#-------------------------------------------

#--------------------------------------------

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)

    messages = [{"role": "system", "content":
        """
        You are an sql command writer. You only produce answers in the form of sql commands that can be executed on a database. 
        Do not use the LIMIT command to limit any results.
        Do not provide any explanations of how you came up with the result. 
        Only provide the sql statement inself.
        """}]



    #--------------------------------
    # messages.append(
    #     {"role": "user", "content": multiline_str1 + prompt},
    # )

    # chat = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo", messages=messages
    # )

    # reply = chat.choices[0].message.content
    # # print(f"ChatGPT: {reply}")
    # print(f"<<<{reply}>>>")
    # --------------------------------


    cnx = mysql.connector.connect(user='u848738634_gbuser1', password='8DfU%#7gNbFf$U-',
                                  host='31.170.160.103',
                                  database='u848738634_aitest1')

    output = ""



    if cnx and cnx.is_connected():


        with cnx.cursor() as cursor:

            reply = cursor.execute("SELECT * FROM orders limit 10")



            # reply = """
            #
            # SELECT qwe p.productLine, SUM(od.quantityOrdered) AS totalQuantitySold
            # FROM products p
            # JOIN orderdetails od ON p.productCode = od.productCode
            # GROUP BY p.productLine
            # ORDER BY totalQuantitySold DESC;
            #
            # """


            st.write(reply)

            try:
                result = cursor.execute(reply)

            except:
                print("some error happened")
                st.write("Sorry, I was unable to generate results for this query. Please rephrase.")

            else:
                rows = cursor.fetchall()


                # Store the result in a multidimensional array
                table_data = [list(row) for row in rows]


                cnx.close()

                #----------------------------------------------------

                data_length = len(table_data)

                if data_length > 0:

                    print("This is the array:")
                    for row in table_data:
                        print(row)

                    #----------------------------------------------------

                    import plotly.figure_factory as ff

                    # table_data = [['Team', 'Wins', 'Losses', 'Ties', 'xxx'],
                    #               ['Montréal<br>Canadiens', 18, 4, 0, 9],
                    #               ['Dallas Stars', 18, 5, 0, 9],
                    #               ['NY Rangers', 16, 5, 0, 9],
                    #               ['Boston<br>Bruins', 13, 8, 0, 9],
                    #               ['Chicago<br>Blackhawks', 13, 8, 0, 9],
                    #               ['LA Kings', 13, 8, 0, 9],
                    #               ['Ottawa<br>Senators', 12, 5, 0, 9]]

                    fig = ff.create_table(table_data, height_constant=60)


                    fig.layout.margin.update({'t': 50, 'b': 100})

                    st.plotly_chart(fig, use_container_width=True)

                else:
                    print("No results were found for that query.")
                    st.write("No results were found for that query.")


    else:


        print("Could not connect")


    cnx.close()


#------------------------------------------
