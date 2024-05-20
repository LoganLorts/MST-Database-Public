# S&T-Database-Project
Database for class rating system for MST.

Use SQLite
sudo apt-get install sqlite3
sudo apt-get install sqlitebrowser

INSERT INTO Class VALUES(
"Engineering ethics, examines major ethical issues facing engineers in the practice of their profession: the problem of professionalism and a code of ethics; the process of ethical decision-making in different working environments; the rights, duties, and conflicting responsibilities of engineers. Prerequisite: Sophomore standing or above. ",
3225,
"Engineering Ethics",
"Arts, Languages & Philosophy"
);

INSERT INTO Teacher VALUES(
"Michael Peterson",
"mpeterson@mst.edu"
);

INSERT INTO TaughtBy VALUES(
3225,
"Arts, Languages & Philosophy",
"Michael Peterson"
);


INSERT INTO Class VALUES(
"Desc",
ClassCode,
"ClassName",
"ClassSubject"
);

INSERT OR IGNORE INTO Teacher (Name, Email) VALUES ("TeacherName", "TeacherEmail");

INSERT INTO TaughtBy VALUES(
ClassCode,
"ClassSubject",
"TeacherName"
);

INSERT INTO Review VALUES ( Review, Teacher taken with, Class Code, Department, Class Rating, Teacher Rating, Workload Rating, User Email, Mandatory Attendance(T/F) );

INSERT INTO Review VALUES ( "", "", 0000, "", 0.00, 0.00 , 0.00, "", True/False );
