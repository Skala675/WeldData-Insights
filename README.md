# WeldData Insights
## Description:

This project aims to address common issues encountered when utilizing SKS controllers. One major challenge is that relying solely on the SKS tools does not provide sufficient traceability throughout the process or allow for observation of parameter behaviors across all welding points.
The project utilizes the SKS tool Q8Log to generate excel worksheets containing welding data for each robot in every cell. Subsequently, the worksheets are saved in a file. However, this approach consumes a significant amount of computer memory, making it infeasible for traceability purposes. Using Python and the Pandas libraries, we monitor the file where all the Excel spreadsheets are created. Once a spreadsheet is created, the program extracts the most critical information from it and exports it to an SQLite database. The program continuously monitors the file. Then, on the website, you can effortlessly search for the welding data you require and filter it by weld part, cell, robot, weld point, dates, and alarms. And you can view the parameter behavior of each weld point through a graph.
You will first notice the most critical weldpoints, which are the ones with more alarms. Finally, you will have the option to set your own limits for each parameter. However, it is expected to change this in another model where you create a parameter reference with all the weldpoints marked as OK. You will then set upper and lower limits within which the parameters must fall to be considered OK.

## How the web works

1.- Once you access the website, the first thing you will encounter is a login form. To access the page's content, you will need to have an account. Ensure that you provide you login credentials to authenticate your account.

2.- After logging in, you will have access to the entire page's content and all its features.

3.- At the top of the page, you can use the search bar to filter your search for welding points by weldpart, weldpoint, cell, robot, dates, and alarms to quickly find the information you need.

4.- Under the search bar, you will find two frames. The first frame displays the graph behavior once you have selected the parameter and weld points that you wish to observe. The right hand side frame shows all the weldpoints that meet the search criteria you set in the search bar. You can view information and select the parameter and weldpoints you want to display in the first frame from this side frame.

5.- Finally, on the last row of the page, you will find three sections. The left-hand side section displays the main information about the first four most critical weld points in the entire database. This allows for easy tracking of weldpoints with the highest number of alarms and problems.

6.- Set up your own limits in the midsection according to the selected parameter. At present, you can only establish upper and lower limits. However, this feature is expected to be replaced by another that will allow you to active a sampling model. This model will provide the average behavior of multiple acceptable weld points, giving you a reference to select a range within which any new weldpoints must fall to be deemed acceptable.

7.- Finally, in the last section of this row, select the parameters and limits you want to view in your graph. Keep in mind that applying a different parameter than the one currently selected in your graph will prevent you from applying the limits. Below this, you will find two buttons. The first one is labed SIGN UP, and it is where you can register to access the page. It is important to be logged in to access this function, as otherwise, anyone could register and gain access to the private information. You can log out by clicking the LOG OUT button.

## About programs 

### Templates 
Among the templates files are four HTML files: index.html, login.html, register.html and main.html. Index.html serves as my primary template which includes the HTML body, necessary headers, and Bootstrap framework. This eliminates the need to individually add them to every HTML file. Then, on the login.html page, you can only access the main page by loggin in. Registering is a similar proccess, with the only difference being that you will need to create a new user in order to access the page content. Once registeres, you will have access to the main.html page, which contains additional features. Here, you can track welding parameters and set up graph limits.

### Static
At statics, there are only two files: styles.css and script.js. In styles.css, we designed our web page and made it adaptative to all types of devices, including phones, laptops, and computers. On the other hand, we utilize the jQuery library called in index.html within script.js to employ AJAX and eliminate the need to constantly refresh the page when submitting a form. This allows us to track all the choices made by the user in real time while continuosly displaying the established weld points, parameters and limits.

### App.py
This is where we work on the main programming portion of our project. We use the Flask framework to create various types of functions to establish our functionalities. Aditionally, we constructed the primary function, which differs from the web functions with Flask. Our process involves tracking a file that contains all the excels, extracting information, and transmitting it to a SQL database.

### Helpers.py
This is where we wrote all our helper functions. I considered these functions not important enough to keep in the app.py file. For example, we created the "login required" function here, as well as all the procedures for exporting and extracting information from Excel files to the SQL database.

### WORK.db
This is the database where information is stored to track and achieve traceability.
Here we have several tables including users, data, parameters, relation and limits. Users holds the records of registered individuals while data stores the primary information of each weld point. Each data set has multiple parameters recorded every 100 milliseconds. On average, each set of data covers a 6-second period. To access the complete set of parameters for each weld point, the main IDs  from the data and parameters databases are related in the relation table.
And we have stored the limits set by the users in the Limits Table.

### Sqlite3.sql
Here we created databases and tables and wrote code to perform tests.
