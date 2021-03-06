DROP TABLE Log; 
DROP TABLE Departments; 
DROP TABLE Job_History;
DROP TABLE Employees;
DROP TABLE Locations; 
DROP TABLE Jobs;

CREATE TABLE Jobs(
JobID number(10) CONSTRAINT Job_ID_J_NN NOT NULL,
Job_Title varchar2(45) CONSTRAINT Job_title_J_NN NOT NULL,
Min_Salary number(10) CONSTRAINT Min_Salary_J_NN NOT NULL,
Max_Salary number(10) CONSTRAINT Max_Salary_J_NN NOT NULL,
CONSTRAINT Jobs_J_PK PRIMARY KEY (JobID)
); 

CREATE TABLE Locations(
LocationID number(10) CONSTRAINT LocationID_L_NN NOT NULL,
Address varchar2(50) CONSTRAINT Address_L_NN NOT NULL,
Postcode varchar2(8) CONSTRAINT Postcode_L_NN NOT NULL,
City varchar2(15) CONSTRAINT City_L_NN NOT NULL,
CONSTRAINT Locations_L_PK PRIMARY KEY (LocationID)
); 

CREATE TABLE Employees(
EmpID number(10) CONSTRAINT EmpID_E_NN NOT NULL, 
First_Name varchar2(30) CONSTRAINT First_Name_E_NN NOT NULL,
Last_Name varchar2(30) CONSTRAINT Last_Name_E_NN NOT NULL,
Email varchar2(40) CONSTRAINT Email_E_NN NOT NULL,
Phone number(11) CONSTRAINT Phone_E_NN NOT NULL,
Hire_Date date DEFAULT sysdate CONSTRAINT Hire_date_E_NN NOT NULL,
Salary number(10) CONSTRAINT Salary_E_NN NOT NULL,
Commission_PCT number(10),
ManagerID number(10),
CONSTRAINT ManagerID_E_FK FOREIGN KEY (ManagerID) REFERENCES Employees(EmpID),
JobID number(10), CONSTRAINT JobID_E_FK FOREIGN KEY (JobID) REFERENCES Jobs(JobID), 
DepartmentID number(10) CONSTRAINT DepartmentID_E_NN NOT NULL,
CONSTRAINT EmpID_E_PK PRIMARY KEY (EmpID) 
); 

CREATE TABLE Job_History(
EmpID number(10) CONSTRAINT EmpID_JH_NN NOT NULL,
JobID number(10) CONSTRAINT JobID_JH_NN NOT NULL,
Start_Date date CONSTRAINT Start_date_JH_NN NOT NULL,
End_Date date,
CONSTRAINT EmpID_JH_FK FOREIGN KEY (EmpID) REFERENCES Employees(EmpID),
CONSTRAINT JobID_JH_FK FOREIGN KEY (JobID) REFERENCES Jobs(JobID) 
); 

CREATE TABLE Departments(
DepartmentID number(10) CONSTRAINT DepartmentID_D_NN NOT NULL,
Dept_Name varchar2(30),
ManagerID number(10) CONSTRAINT ManagerID_D_NN NOT NULL,
LocationID number(10) CONSTRAINT LocationID_D_NN NOT NULL,
CONSTRAINT ManagerID_D_FK FOREIGN KEY (ManagerID) REFERENCES Employees(EmpID),
CONSTRAINT LocationID_D_FK FOREIGN KEY (LocationID) REFERENCES Locations(LocationID),
CONSTRAINT DepartmentID_P_PK PRIMARY KEY (DepartmentID)
); 

CREATE TABLE Log(
LogID number(10) CONSTRAINT LogID_NN NOT NULL,
OrigInput varchar2(100) CONSTRAINT OrigInput_NN NOT NULL,
QueryRan varchar2(100) CONSTRAINT QueryRan_NN NOT NULL,
UserConf varchar2(5) CONSTRAINT UserConf_NN NOT NULL,
CONSTRAINT LogID_PK PRIMARY KEY (LogID) 
); 

/* JOBS */
INSERT INTO Jobs 
VALUES (1, 'Executive', 79000, 84000);

INSERT INTO Jobs
VALUES (2, 'Secretary', 18000, 24000);

INSERT INTO Jobs
VALUES (3, 'Department Supervisor', 24000, 34000);

INSERT INTO Jobs
VALUES (4, 'Department Manager', 44000, 56000);

INSERT INTO Jobs
VALUES (5, 'Trial Staff', 16000, 18000);


/* LOCATIONS */
INSERT INTO Locations
VALUES (1, 'Fake Address 1, 230 Imaginary Street', 'M136FB', 'Manchester');

INSERT INTO Locations
VALUES (2, 'Site 2031, Oxford Boulevard', 'L15B12', 'London');

INSERT INTO Locations
VALUES (3, 'Denley Gardens', 'DD11 2ES', 'Arbroath');

INSERT INTO Locations 
VALUES (4, '24 Prescott Street', 'B26 3JZ', 'Birmingham');

/* EMPLOYEES */ 

INSERT INTO Employees
VALUES(1, 'Alasdair', 'Garrod', 'SampleEmail@email.com', 07529392502, '14-NOV-2010',
84000, null, 1, 1, 1); 

INSERT INTO Employees
VALUES(2, 'Annika', 'Kundert', 'AnnikaCoolGirl92@msn.co.uk', 07700900847, '26-SEP-1999',
24000, null, 1, 2, 1); 

INSERT INTO Employees
VALUES(3, 'Katsuo', 'Sato', 'sato@email.co.uk', 07700922731, '1-JAN-2002', 
52000, null, 1, 4, 2);

INSERT INTO Employees
VALUES(4, 'Eireen', 'McNeil', 'eMcN@mailer.com', 07700904620, '26-JUN-2005',
30000, null, 4, 3, 2);

INSERT INTO Employees
VALUES(5, 'Michael', 'Smith', 'MichaelEmail@email.com', 07982359201, '11-FEB-2016', 
17500, null, 5, 5, 2); 

/* Departments */ 
INSERT INTO Departments
VALUES(1, 'Head Office', 1, 1); 

INSERT INTO Departments
VALUES(2, 'IT Development', 3, 4);

INSERT INTO Departments
VALUES(3, 'HR', 1, 1);

INSERT INTO Departments
VALUES(4, 'Admin', 1, 1);

ALTER TABLE Employees
ADD CONSTRAINT DepartmentID_E_FK FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID); 
  
