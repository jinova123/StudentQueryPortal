from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import uuid


# =========================================================
# APPLICATION SETUP
# =========================================================

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///student_query_portal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "student-query-portal-secret-key"

# Keep the login session stable while navigating between pages.
# These settings are suitable for local development and deployment behind HTTPS.
app.config["SESSION_COOKIE_NAME"] = "student_query_portal_session"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=12)

db = SQLAlchemy(app)


# =========================================================
# INDIA STANDARD TIME
# =========================================================

INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


def ist_now():
    """
    Return current Indian Standard Time.
    Stored as timezone-naive datetime for SQLite compatibility.
    """
    return datetime.now(INDIA_TIMEZONE).replace(tzinfo=None)


# =========================================================
# COMPLAINT CATEGORIES
# =========================================================

CATEGORY_OPTIONS = {

    "Academic": [
        "Attendance",
        "Faculty",
        "Timetable",
        "Course Registration",
        "Study Materials",
        "Classroom"
    ],

    "Accounts": [
        "Fee Payment",
        "Fee Receipt",
        "Refund",
        "Scholarship",
        "Fine",
        "Payment Issue"
    ],

    "Administration": [
        "ID Card",
        "Certificates",
        "Documents",
        "Campus Services",
        "General Administration"
    ],

    "Examination Cell": [
        "Exam Schedule",
        "Hall Ticket",
        "Internal Marks",
        "Results",
        "Revaluation",
        "Supplementary Exam"
    ],

    "Hostel": [
        "Room Allocation",
        "Mess",
        "Maintenance",
        "Water Supply",
        "Electricity",
        "Hostel Rules"
    ],

    "IT Support": [
        "Wi-Fi",
        "Student Portal",
        "Login Issue",
        "Email Account",
        "Software",
        "Computer / Lab"
    ],

    "Library": [
        "Book Issue",
        "Book Return",
        "Lost Book",
        "Library Access",
        "E-Resources"
    ],

    "Placement": [
        "Placement Registration",
        "Company Visit",
        "Aptitude Test",
        "Interview",
        "Internship"
    ],

    "Transport": [
        "Bus Route",
        "Bus Timing",
        "Bus Pass",
        "Driver / Conductor",
        "Transport Fee"
    ],

    "Student Clubs": [
        "Compile Crew",
        "Harmony",
        "Wisdom",
        "EngageX",
        "VistaraX",
        "Club Membership",
        "Club Events",
        "Club Coordination",
        "Club General Query"
    ]
}


# =========================================================
# USER MODEL
# =========================================================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    user_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    department = db.Column(
        db.String(100),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=ist_now
    )


# =========================================================
# DEPARTMENT MODEL
# =========================================================

class Department(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )


# =========================================================
# QUERY / COMPLAINT MODEL
# =========================================================

class Query(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ticket_id = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("department.id"),
        nullable=True
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    subject = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        default="Normal"
    )

    status = db.Column(
        db.String(50),
        default="Submitted"
    )

    assigned_admin = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=ist_now
    )

    updated_at = db.Column(
        db.DateTime,
        default=ist_now,
        onupdate=ist_now
    )

    sla_deadline = db.Column(
        db.DateTime,
        nullable=True
    )


# =========================================================
# MESSAGE MODEL
# =========================================================

class Message(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    query_id = db.Column(
        db.Integer,
        db.ForeignKey("query.id"),
        nullable=False
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=ist_now
    )

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id]
    )
# =========================================================
# NOTIFICATION MODEL
# =========================================================

class Notification(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    query_id = db.Column(
        db.Integer,
        db.ForeignKey("query.id"),
        nullable=True
    )

    message = db.Column(
        db.String(255),
        nullable=False
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=ist_now
    )


# =========================================================
# FEEDBACK MODEL
# =========================================================

class Feedback(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    query_id = db.Column(
        db.Integer,
        db.ForeignKey("query.id"),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=ist_now
    )


# =========================================================
# SYSTEM SETTINGS
# =========================================================

class SystemSetting(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    key = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    value = db.Column(
        db.String(100),
        nullable=False
    )


# =========================================================
# REGISTERED STUDENTS
# =========================================================
# College-provided student records.
#
# Password rule:
# first 3 letters of first name + last 3 digits
# of register number, converted to lowercase.
#
# Example:
# JINOVA R + 11524100040
# = jin + 040
# = jin040
# =========================================================

REGISTERED_STUDENTS = [
    ('11152310053', 'JANAPRIYAN. R'),
    ('11523100001', 'ABAYA D'),
    ('11523100002', 'ABDUL DHALHA A'),
    ('11523100004', 'ABISHEK.S.S'),
    ('11523100005', 'AHAMED MYDEEN'),
    ('11523100006', 'AKSHAYA S'),
    ('11523100007', 'AKSHAYA D'),
    ('11523100008', 'ANU G'),
    ('11523100009', 'ANUSIYA V'),
    ('11523100010', 'ARAVINTH G'),
    ('11523100011', 'ARJUN M'),
    ('11523100012', 'ARULARAVINDAN K'),
    ('11523100013', 'ARUNKUMAR L'),
    ('11523100014', 'ARUN KUMAR A'),
    ('11523100015', 'ARUN PRASATH S'),
    ('11523100016', 'ASHIKA JENIFER L'),
    ('11523100017', 'ASHWIN R'),
    ('11523100018', 'ATHIBAR C'),
    ('11523100019', 'BALAJI S'),
    ('11523100020', 'BALAJI K'),
    ('11523100021', 'BALAJI R'),
    ('11523100022', 'BARRATH K'),
    ('11523100023', 'BOOMIKA S'),
    ('11523100024', 'BRINDHADEVI S'),
    ('11523100025', 'DEVADHARSHINI B'),
    ('11523100026', 'DHANUSRI P'),
    ('11523100028', 'DHARUN AKASH M'),
    ('11523100029', 'DHIVYA DHARSHINI T'),
    ('11523100030', 'DINESH M'),
    ('11523100031', 'DHINESH R'),
    ('11523100032', 'B.DINESH KUMAR'),
    ('11523100033', 'DINESHKUMAR'),
    ('11523100034', 'DINESH KUMAR S'),
    ('11523100035', 'DINESH KUMAR J'),
    ('11523100036', 'DINESH KUMAR M'),
    ('11523100037', 'DINESH KUMAR C'),
    ('11523100038', 'DHIVAKARAN B'),
    ('11523100040', 'GEJASRI A'),
    ('11523100041', 'GIRIVARAN C'),
    ('11523100042', 'GOKULAKANNAN.M'),
    ('11523100043', 'HARIHARAN T'),
    ('11523100044', 'HARIHARASUDHAN P'),
    ('11523100045', 'HARINI'),
    ('11523100046', 'HARINI S'),
    ('11523100047', 'HARISH K'),
    ('11523100048', 'HARITHA R'),
    ('11523100049', 'JAGANATHAN A'),
    ('11523100050', 'H.JAIDEV'),
    ('11523100051', 'JAISON'),
    ('11523100052', 'R JANANI'),
    ('11523100054', 'JAYASWETHA S'),
    ('11523100055', 'JAYASHREE R'),
    ('11523100056', 'JAYASOORYA S'),
    ('11523100057', 'JEEVALAKSHMI S'),
    ('11523100058', 'JEEVASARATHY S'),
    ('11523100060', 'JOSHIGA R'),
    ('11523100061', 'KALAIYARASAN R'),
    ('11523100062', 'KANAGARAJ G'),
    ('11523100063', 'KANNAN S'),
    ('11523100064', 'KARISHMA B'),
    ('11523100065', 'KARTHIKA A'),
    ('11523100066', 'KAILASH'),
    ('11523100067', 'KARUNYA T'),
    ('11523100068', 'KAVALI MANAV'),
    ('11523100069', 'KAVIYASREE B'),
    ('11523100070', 'KAVIYASRI P'),
    ('11523100071', 'KAYALVIZHI K'),
    ('11523100072', 'KISHORE S'),
    ('11523100073', 'KISHORE R'),
    ('11523100074', 'KISHORE KUMAR'),
    ('11523100075', 'KRISHNADEVA K'),
    ('11523100076', 'KRISHNAGANTH R'),
    ('11523100077', 'N.LAKSHMI DURGA'),
    ('11523100078', 'LAWANYA R'),
    ('11523100080', 'MAHALAKSHMI'),
    ('11523100081', 'MANIKANDAN'),
    ('11523100082', 'MANIRETHINAM'),
    ('11523100083', 'MOHAMMED AMSATH'),
    ('11523100084', 'MOHAMED KAJAH MOHAIDEEN'),
    ('11523100086', 'MUKESH KANNA'),
    ('11523100087', 'MUKHUNDHAN'),
    ('11523100088', 'MURUGAN'),
    ('11523100089', 'NAVINRAJ'),
    ('11523100090', 'NITHISH'),
    ('11523100091', 'PADMANATHAN'),
    ('11523100092', 'PANNEERSELVAM'),
    ('11523100093', 'PIRADEEP'),
    ('11523100094', 'PRADEEP S'),
    ('11523100095', 'PRASANNA KUMAR'),
    ('11523100096', 'PRAVIN'),
    ('11523100097', 'RAASIKA N'),
    ('11523100098', 'RAGAVI'),
    ('11523100099', 'RAGHUL'),
    ('11523100101', 'RAJ GAUTHAM'),
    ('11523100102', 'RAJALAKSHMI'),
    ('11523100103', 'RAKSHITHA'),
    ('11523100104', 'RANJITH'),
    ('11523100105', 'RAVIKUMAR'),
    ('11523100106', 'RENITH'),
    ('11523100108', 'RISHI KUMAR'),
    ('11523100109', 'RISHIMA'),
    ('11523100110', 'RIZWANA BAGAM'),
    ('11523100112', 'ROOPAN'),
    ('11523100113', 'SAKTHI DEVI'),
    ('11523100114', 'SAKTHI PERUMAL'),
    ('11523100115', 'SAMJEGAN'),
    ('11523100116', 'SANJAYKUMAR'),
    ('11523100117', 'SATHYA'),
    ('11523100118', 'SELVAGANESAN'),
    ('11523100119', 'SHAHANA BEGUM'),
    ('11523100120', 'SHARMILABANU'),
    ('11523100121', 'SIBIRAJ'),
    ('11523100122', 'SIVARANJANI'),
    ('11523100123', 'SOPIKA'),
    ('11523100124', 'SOWNDHARYAN'),
    ('11523100125', 'SRI JANANI'),
    ('11523100126', 'SRI SARAN'),
    ('11523100127', 'SRIPRIYADHARSHAN'),
    ('11523100128', 'SRITHAR'),
    ('11523100130', 'SUDHARSAN'),
    ('11523100131', 'SUDHARSAN R'),
    ('11523100132', 'SUNISH RAJ'),
    ('11523100134', 'SURIYA'),
    ('11523100135', 'SURYA'),
    ('11523100136', 'SUSHIL NERAN'),
    ('11523100137', 'THARANI'),
    ('11523100138', 'THARUN'),
    ('11523100141', 'SUMITHA'),
    ('11523100142', 'THEYANESVAR'),
    ('11523100144', 'VARADHARAJAN'),
    ('11523100145', 'VARSHA'),
    ('11523100146', 'VASANTH RUBAN'),
    ('11523100148', 'VIJAY'),
    ('11523100150', 'VISHAL M'),
    ('11523100151', 'VISHAL'),
    ('11523100152', 'VISHAL BARATH'),
    ('11523100153', 'VISHVA'),
    ('11523100154', 'VISWANATH'),
    ('11523100155', 'YOGESHWARAN'),
    ('11523100156', 'YOGESHWARAN P'),
    ('11523108001', 'ARUNKUMAR'),
    ('11524100001', 'AASHIKA A'),
    ('11524100002', 'ABDUL RASHAD R'),
    ('11524100003', 'ABDUR RAHEEF A.J'),
    ('11524100004', 'ABINAYA D'),
    ('11524100005', 'ABINAYA M'),
    ('11524100006', 'AKALYA R'),
    ('11524100007', 'AKSHITHA A'),
    ('11524100008', 'ARJUN S'),
    ('11524100009', 'ARUL SHINY A'),
    ('11524100010', 'ARYA A'),
    ('11524100011', 'ASHWIN P'),
    ('11524100012', 'ATCHAYA M'),
    ('11524100013', 'AURTHAR X'),
    ('11524100014', 'DEEPIKA CHRISTY S'),
    ('11524100015', 'DEEPIKA R'),
    ('11524100016', 'DESIKA M'),
    ('11524100017', 'DEVADHARSHINI T'),
    ('11524100018', 'DHANALAKSHMI M'),
    ('11524100019', 'DHANALAKSHMI S'),
    ('11524100020', 'DHISHANTH R'),
    ('11524100021', 'DHIYAN S'),
    ('11524100022', 'DINESH A'),
    ('11524100023', 'DINESHKUMAR R'),
    ('11524100024', 'ELAVARASAN M'),
    ('11524100026', 'GAYATHRI A'),
    ('11524100027', 'GAYATHRI G'),
    ('11524100028', 'GIRI PRASATH A'),
    ('11524100030', 'HAKKEEM ALI M'),
    ('11524100031', 'HARI PRASAD A'),
    ('11524100032', 'HARIHARAN N'),
    ('11524100033', 'HARIKRISHNAN T'),
    ('11524100034', 'HIRUTHICK P'),
    ('11524100035', 'JANANI PRIYA S'),
    ('11524100036', 'JEFFRY D'),
    ('11524100037', 'JEFRIN A'),
    ('11524100038', 'JESUDOSS S'),
    ('11524100039', 'JHANANI B'),
    ('11524100040', 'JINOVA R'),
    ('11524100041', 'JOHNU A'),
    ('11524100042', 'JOSHUA SAMUEL S'),
    ('11524100044', 'KEERTHANAN K'),
    ('11524100045', 'KEM KUMAR K'),
    ('11524100046', 'KESAVA KUMAR S'),
    ('11524100047', 'LATHIGA SHREE K'),
    ('11524100048', 'MAHADHARSHINI G'),
    ('11524100049', 'MAHALAKSHMI K'),
    ('11524100051', 'MANOJKUMAR P'),
    ('11524100052', 'MATHUMITHA A'),
    ('11524100053', 'MOHAMED AASIM S'),
    ('11524100054', 'MOHAMED HAIF K'),
    ('11524100055', 'MOHAMED HANIFA S'),
    ('11524100056', 'MOHAMED NABEEL T'),
    ('11524100057', 'MOHAMED SHAFIL J'),
    ('11524100058', 'MOHAMEED ANAS P A'),
    ('11524100059', 'NAVEEN R'),
    ('11524100060', 'NEHASRI B C'),
    ('11524100061', 'NIVASHINI S'),
    ('11524100062', 'PRADEESHWARAN V'),
    ('11524100063', 'PRAGADEESHWARAN S'),
    ('11524100064', 'PRIYANKA A'),
    ('11524100065', 'RAGAVAN B'),
    ('11524100066', 'RENGADURAI A'),
    ('11524100067', 'RIJO EZRA A'),
    ('11524100068', 'RITHISH D'),
    ('11524100069', 'ROKESH ADAIKKALAM S'),
    ('11524100070', 'SANTHIYA M'),
    ('11524100071', 'SANTHOSH G'),
    ('11524100072', 'SARANKUMAR S'),
    ('11524100073', 'SARUMATHI G'),
    ('11524100074', 'SATHIYA S'),
    ('11524100075', 'SHALINI E'),
    ('11524100076', 'SHARU BELLA S'),
    ('11524100077', 'SHARUK RITHWAN S'),
    ('11524100078', 'SHEETHAL NIRANJANI S'),
    ('11524100079', 'SOUNDHARYA S'),
    ('11524100080', 'SRI SOWMIYA NARAYANAN B'),
    ('11524100081', 'SRIMADHAVAN A K'),
    ('11524100082', 'SRINATHI P'),
    ('11524100083', 'SRINIDHI S'),
    ('11524100084', 'SUDALAI S'),
    ('11524100085', 'SURYA A'),
    ('11524100086', 'SURYAPRAKASH S'),
    ('11524100087', 'SUSIKUMAR S'),
    ('11524100088', 'TERANCE REGAN A'),
    ('11524100089', 'THANUSHREE N'),
    ('11524100090', 'VIGNESH V'),
    ('11524100091', 'VISHAL K'),
    ('11524100092', 'YASHICA S'),
    ('11524100093', 'YOGESHWARAN S'),
    ('11524100094', 'YUVARAJ K'),
    ('11524100095', 'JEEVABHARATHI P'),
    ('11524108001', 'GIRIDHAR SHAKTHI R G'),
    ('11525100001', 'AAFRIN BANU A'),
    ('11525100002', 'AARIHARAN A'),
    ('11525100003', 'AATHIKESAVAN N'),
    ('11525100004', 'ABISHEK A'),
    ('11525100005', 'ABISHEK S'),
    ('11525100006', 'ADHITHYAN S'),
    ('11525100007', 'AHAMED KABEER A'),
    ('11525100008', 'AHMED A'),
    ('11525100009', 'AISHWARYA I'),
    ('11525100010', 'AJMAL AHMED R'),
    ('11525100011', 'AKASH E'),
    ('11525100012', 'AKASH S'),
    ('11525100013', 'AKSHAYA E B'),
    ('11525100014', 'AMJATH AHAMED U'),
    ('11525100015', 'AMUTHAN K'),
    ('11525100016', 'ANJUGAM A'),
    ('11525100017', 'APSARA A'),
    ('11525100019', 'ARULMOZHI VARMAN T'),
    ('11525100020', 'ASHIFA BANU N'),
    ('11525100021', 'ASWIN B'),
    ('11525100022', 'AYESHA SITHIKA M'),
    ('11525100023', 'BALASURYA T'),
    ('11525100024', 'BARANI M'),
    ('11525100025', 'BHARATH P'),
    ('11525100026', 'BHAVANA K'),
    ('11525100027', 'BOOMIKA T'),
    ('11525100028', 'BRINDHA A'),
    ('11525100029', 'DAKSHIN K J'),
    ('11525100030', 'DEVADHARSHAN S'),
    ('11525100031', 'DHANISH S'),
    ('11525100032', 'DHANIYA S'),
    ('11525100033', 'DHANUSH A'),
    ('11525100034', 'DHANUSH R'),
    ('11525100035', 'DHARSHAN K'),
    ('11525100036', 'DHAYASHANKAR R'),
    ('11525100037', 'DHIVIYAN A'),
    ('11525100038', 'DHIVYA T'),
    ('11525100039', 'ELIYA IMMANUVEL J'),
    ('11525100040', 'ESALI R'),
    ('11525100041', 'FRANKLIN A'),
    ('11525100042', 'GAYATHRI S'),
    ('11525100043', 'GIRIDHARAN C'),
    ('11525100044', 'GOKULAKRISHNAN N'),
    ('11525100045', 'GOKULAVASAN M'),
    ('11525100046', 'HARINI V'),
    ('11525100047', 'HARISH A'),
    ('11525100048', 'HARISH R'),
    ('11525100049', 'HARISH S'),
    ('11525100050', 'HARSHINI S'),
    ('11525100051', 'HEMAYUTHIKA G P'),
    ('11525100052', 'JAI HARISH JESTIN J'),
    ('11525100053', 'JANANI M'),
    ('11525100054', 'JANANI V'),
    ('11525100055', 'JAYASRI R'),
    ('11525100056', 'JENIS BRISKILLA S'),
    ('11525100057', 'KAMALIKA K'),
    ('11525100058', 'KANISHKA K'),
    ('11525100059', 'KARTHIKA S'),
    ('11525100060', 'KAVIN B'),
    ('11525100061', 'KAVIRAJ V'),
    ('11525100062', 'KAVIYA K'),
    ('11525100063', 'KAVIYARASAN A'),
    ('11525100064', 'KAVIYASRI J'),
    ('11525100065', 'KEERTHIKA M'),
    ('11525100067', 'KEERTHIVASAN M'),
    ('11525100068', 'KESAVAN R'),
    ('11525100069', 'KESHINI M'),
    ('11525100070', 'KIRUBAKARAN B'),
    ('11525100071', 'KISHODHARAN R'),
    ('11525100072', 'KISHORE KUMAR R'),
    ('11525100073', 'KOWTHAM S'),
    ('11525100074', 'LISHAKINI MUTHU'),
    ('11525100075', 'MADHUMITHA R'),
    ('11525100076', 'MAGESHWARAN R'),
    ('11525100077', 'MAHA DHARSHINI M'),
    ('11525100078', 'MAHALAKSHMI R'),
    ('11525100079', 'MAHENDIRAN P'),
    ('11525100080', 'MAHESWARAN N.V'),
    ('11525100081', 'MALINI P'),
    ('11525100082', 'MANIMARAN DHIVYABHARATHI'),
    ('11525100084', 'MATHUMITHA V'),
    ('11525100085', 'MELVIN J'),
    ('11525100086', 'MITHRA R'),
    ('11525100087', 'MOHAMED AMAAN M'),
    ('11525100088', 'MOHAMED ARIF M'),
    ('11525100089', 'MOHAMED AZARUDEEN R'),
    ('11525100090', 'MOHAMED SHAFEEK A'),
    ('11525100091', 'MOHANRAJ K'),
    ('11525100092', 'NANDHA KISHORE S'),
    ('11525100093', 'NANDHINI N'),
    ('11525100094', 'NANTHINI S'),
    ('11525100095', 'NARMATHA S'),
    ('11525100097', 'NEATHRA LAKSHMI S'),
    ('11525100098', 'NIROSHA T'),
    ('11525100099', 'NITHISH KRISHNAN B'),
    ('11525100100', 'NITHYA SRI N'),
    ('11525100101', 'NIVASH S'),
    ('11525100102', 'NOWDIDH R'),
    ('11525100103', 'PANDI SATHAIAH P'),
    ('11525100104', 'PANDIPRIYAN M'),
    ('11525100105', 'PAVAI M'),
    ('11525100107', 'PAVITHRA S'),
    ('11525100108', 'PAVITHRAVARSINI M'),
    ('11525100109', 'PERARASU S'),
    ('11525100110', 'PON RITHIK M'),
    ('11525100111', 'POOVARAGAVAN T'),
    ('11525100112', 'PRAKASH G'),
    ('11525100113', 'PRASANNA S'),
    ('11525100114', 'PRASANNA R'),
    ('11525100115', 'PRASATH V'),
    ('11525100116', 'PRAVEENA M'),
    ('11525100117', 'RAGUL S'),
    ('11525100118', 'RAJARAJAN P S'),
    ('11525100119', 'RAJESHKUMAR S'),
    ('11525100120', 'RAM P'),
    ('11525100121', 'RAMAN D'),
    ('11525100122', 'ROBIN RUFFUS P'),
    ('11525100123', 'ROGESH PANDI K'),
    ('11525100124', 'ROHITH R'),
    ('11525100125', 'RUHINA SHARINE S'),
    ('11525100126', 'SABARISH LAKSHMANAN'),
    ('11525100127', 'SAHANA P'),
    ('11525100128', 'SAI SANJAY R'),
    ('11525100129', 'SANJAI A'),
    ('11525100130', 'SANJAY S'),
    ('11525100131', 'SANJAY V'),
    ('11525100132', 'SANJAY J'),
    ('11525100133', 'SANJEEV SARAN S'),
    ('11525100134', 'SANTHANA BHARATHI S'),
    ('11525100135', 'SANTHANA K'),
    ('11525100136', 'SANTHOSH M'),
    ('11525100137', 'SANTHOSH V'),
    ('11525100138', 'SANTHOSH N'),
    ('11525100139', 'SANTHOSH T'),
    ('11525100140', 'SARANYA M'),
    ('11525100141', 'SARANYA K'),
    ('11525100142', 'SARAVANAN B'),
    ('11525100143', 'SARULATHA T'),
    ('11525100144', 'SATHIYA PRIYAN S'),
    ('11525100145', 'SHANKARAN N'),
    ('11525100146', 'SHARAN S'),
    ('11525100147', 'SHARUKESH R'),
    ('11525100148', 'SHASWANTHKAR B'),
    ('11525100149', 'SHIVANI S'),
    ('11525100150', 'SHIVESH BAASU P'),
    ('11525100151', 'SHRI HARSHINI V'),
    ('11525100152', 'SILAMBARASAN S'),
    ('11525100153', 'SINDHUJA B'),
    ('11525100154', 'SIVAVARSHINI M'),
    ('11525100155', 'SONAKSHITHA M'),
    ('11525100156', 'SOWNDHARYA S'),
    ('11525100157', 'SRI MATHAVAN P'),
    ('11525100158', 'SRI VISHNU SUDHARSAN N'),
    ('11525100159', 'SRIKARAN R'),
    ('11525100160', 'SRINITHI S'),
    ('11525100161', 'SRISANTH R'),
    ('11525100162', 'SUBALAKSHMI S S'),
    ('11525100163', 'SUBASRI S'),
    ('11525100164', 'SUBATHRA M'),
    ('11525100165', 'SUBHA SHRI A'),
    ('11525100166', 'SURENDAR S'),
    ('11525100167', 'SUTHISH S'),
    ('11525100168', 'SWETHA A'),
    ('11525100169', 'SWETHASRI S'),
    ('11525100170', 'THANANCHEYAN E'),
    ('11525100171', 'THIVAKAR R'),
    ('11525100172', 'UDDESH S'),
    ('11525100173', 'UGANRAJ P'),
    ('11525100174', 'UPENDRA P'),
    ('11525100175', 'VAIRAMAREESWARAN R'),
    ('11525100176', 'VAVUNIYA G'),
    ('11525100177', 'VETRILINGAM S'),
    ('11525100178', 'VETRIVEL T'),
    ('11525100179', 'VIGNESH N'),
    ('11525100180', 'VIJAY M'),
    ('11525100181', 'VIJAYAN M'),
    ('11525100182', 'VINOTH V'),
    ('11525100183', 'VISHALINI D'),
    ('11525100184', 'VISWANTH M'),
    ('11525100185', 'YOGA MUTHU KALEESH M N'),
    ('11525100186', 'YOGESHWARI I'),
    ('11525100187', 'YOHA NARASIMMAA V')
]


# =========================================================
# PASSWORD GENERATOR
# =========================================================

def generate_student_password(name, register_number):
    """
    Password format:
    first 3 letters of first name + last 3 digits
    of register number.

    Example:
    JINOVA R
    11524100040

    Result:
    jin040
    """

    cleaned_name = " ".join(name.strip().split())

    name_parts = cleaned_name.split()

    if not name_parts:
        return register_number[-6:]

    first_name = name_parts[0]

    first_three_letters = first_name[:3].lower()

    last_three_digits = register_number[-3:]

    return first_three_letters + last_three_digits


# =========================================================
# DEPARTMENT ADMIN CONFIGURATION
# =========================================================
# Department administrators log in with their name in ALL CAPS
# (without spaces) and their DOB in DD/MM/YYYY as password.
# The overall administrator remains ADMIN001 and is not reset here.

DEPARTMENT_ADMIN_CONFIG = {
    "SASIKUMAR": {
        "password": "22/09/1999",
        "departments": ["Examination Cell", "Placement"]
    },
    "JAYAPRADHA": {
        "password": "24/08/2000",
        "departments": ["Academic", "Accounts", "Hostel"]
    },
    "GOWTHAMI": {
        "password": "22/06/2000",
        "departments": ["IT Support", "Library"]
    },
    "RADHIKA": {
        "password": "15/05/1999",
        "departments": ["Administration", "Transport"]
    },
    "VISHVA": {
        "password": "12/09/2004",
        "departments": ["Student Clubs"]
    }
}

OVERALL_ADMIN_ID = "ADMIN001"


def is_overall_admin(admin):
    return bool(admin and admin.role == "admin" and admin.user_id == OVERALL_ADMIN_ID)


def get_admin_department_names(admin):
    if not admin or admin.role != "admin":
        return []
    if is_overall_admin(admin):
        return [name for name in CATEGORY_OPTIONS.keys()]
    config = DEPARTMENT_ADMIN_CONFIG.get(admin.user_id.upper())
    if config:
        return config["departments"]
    if admin.department:
        return [item.strip() for item in admin.department.split("|") if item.strip()]
    return []


def get_department_admin(department_name):
    for admin_id, config in DEPARTMENT_ADMIN_CONFIG.items():
        if department_name in config["departments"]:
            return User.query.filter_by(user_id=admin_id, role="admin").first()
    return None


def ensure_query_assignment(query):
    if not query:
        return None

    department = db.session.get(Department, query.department_id)
    if not department:
        return None

    current_admin = db.session.get(User, query.assigned_admin) if query.assigned_admin else None
    if current_admin and current_admin.role == "admin":
        allowed_departments = get_admin_department_names(current_admin)
        if is_overall_admin(current_admin) or department.name in allowed_departments:
            return current_admin

    department_admin = get_department_admin(department.name)
    if not department_admin:
        return None

    query.assigned_admin = department_admin.id
    if query.status == "Submitted":
        query.status = "Assigned"
    query.updated_at = ist_now()
    return department_admin


def admin_can_access_query(admin, query):
    if not admin or admin.role != "admin" or not query:
        return False
    if is_overall_admin(admin):
        return True
    assigned = db.session.get(User, query.assigned_admin) if query.assigned_admin else None
    if assigned and assigned.id == admin.id:
        return True
    department = db.session.get(Department, query.department_id)
    return bool(department and department.name in get_admin_department_names(admin))


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():

    db.create_all()

    # -----------------------------------------------------
    # CONVERT OLD UTC TIMES TO IST
    # -----------------------------------------------------

    migration = SystemSetting.query.filter_by(
        key="ist_time_migration_v1"
    ).first()

    if not migration:

        users = User.query.all()

        for user in users:

            if user.created_at:

                user.created_at += timedelta(
                    hours=5,
                    minutes=30
                )

        queries = Query.query.all()

        for query in queries:

            if query.created_at:

                query.created_at += timedelta(
                    hours=5,
                    minutes=30
                )

            if query.updated_at:

                query.updated_at += timedelta(
                    hours=5,
                    minutes=30
                )

            if query.sla_deadline:

                query.sla_deadline += timedelta(
                    hours=5,
                    minutes=30
                )

        messages = Message.query.all()

        for message in messages:

            if message.created_at:

                message.created_at += timedelta(
                    hours=5,
                    minutes=30
                )

        notifications = Notification.query.all()

        for notification in notifications:

            if notification.created_at:

                notification.created_at += timedelta(
                    hours=5,
                    minutes=30
                )

        feedbacks = Feedback.query.all()

        for feedback in feedbacks:

            if feedback.created_at:

                feedback.created_at += timedelta(
                    hours=5,
                    minutes=30
                )

        db.session.add(
            SystemSetting(
                key="ist_time_migration_v1",
                value="completed"
            )
        )

        db.session.commit()

    # -----------------------------------------------------
    # DEMO STUDENT
    # -----------------------------------------------------
    # Kept so existing portal data is not broken.
    # Your college students are added separately below.
    # -----------------------------------------------------

    demo_student = User.query.filter_by(
        user_id="STU001"
    ).first()

    if not demo_student:

        demo_student = User(

            name="Demo Student",

            email="student@college.edu",

            user_id="STU001",

            password=generate_password_hash(
                "student123"
            ),

            role="student"

        )

        db.session.add(
            demo_student
        )

    # -----------------------------------------------------
    # DEMO ADMIN
    # -----------------------------------------------------

    demo_admin = User.query.filter_by(
        user_id="ADMIN001"
    ).first()

    if not demo_admin:

        demo_admin = User(

            name="Portal Administrator",

            email="admin@college.edu",

            user_id="ADMIN001",

            password=generate_password_hash(
                "admin123"
            ),

            role="admin"

        )

        db.session.add(
            demo_admin
        )

    db.session.commit()

    # -----------------------------------------------------
    # ADD COLLEGE REGISTERED STUDENTS
    # -----------------------------------------------------

    for register_number, student_name in REGISTERED_STUDENTS:

        existing_student = User.query.filter_by(
            user_id=register_number,
            role="student"
        ).first()

        generated_password = generate_student_password(
            student_name,
            register_number
        )

        generated_email = (
            register_number.lower()
            + "@college.edu"
        )

        if not existing_student:

            new_student = User(

                name=student_name,

                email=generated_email,

                user_id=register_number,

                password=generate_password_hash(
                    generated_password
                ),

                role="student",

                created_at=ist_now()

            )

            db.session.add(
                new_student
            )

        else:

            # Keep the existing student's database ID
            # so previous complaints are not affected.
            existing_student.name = student_name

            existing_student.password = generate_password_hash(
                generated_password
            )

            existing_student.role = "student"

    db.session.commit()

    # -----------------------------------------------------
    # DEFAULT DEPARTMENTS
    # -----------------------------------------------------

    departments = [

        (
            "Academic",
            "Academic related queries and concerns"
        ),

        (
            "Examination Cell",
            "Examination, results and assessment related queries"
        ),

        (
            "Accounts",
            "Fee payment and financial related queries"
        ),

        (
            "Hostel",
            "Hostel and accommodation related queries"
        ),

        (
            "Transport",
            "College transport related queries"
        ),

        (
            "IT Support",
            "Technical and IT related queries"
        ),

        (
            "Library",
            "Library and book related queries"
        ),

        (
            "Placement",
            "Placement and career related queries"
        ),

        (
            "Administration",
            "General administrative queries"
        ),

        (
            "Student Clubs",
            "Student club activities, membership, events and coordination related queries"
        )
    ]

    for department_name, description in departments:

        existing_department = Department.query.filter_by(
            name=department_name
        ).first()

        if not existing_department:

            db.session.add(
                Department(
                    name=department_name,
                    description=description
                )
            )

    db.session.commit()

    # -----------------------------------------------------
    # DEPARTMENT ADMINISTRATORS
    # -----------------------------------------------------
    for admin_id, config in DEPARTMENT_ADMIN_CONFIG.items():
        admin = User.query.filter_by(
            user_id=admin_id,
            role="admin"
        ).first()

        department_value = "|".join(config["departments"])
        generated_email = f"{admin_id.lower()}@department-admin.college.local"

        if not admin:
            admin = User(
                name=admin_id,
                email=generated_email,
                user_id=admin_id,
                password=generate_password_hash(config["password"]),
                role="admin",
                department=department_value,
                created_at=ist_now()
            )
            db.session.add(admin)
        else:
            admin.name = admin_id
            admin.role = "admin"
            admin.department = department_value
            admin.password = generate_password_hash(config["password"])

    db.session.commit()

    # -----------------------------------------------------
    # AUTOMATICALLY ASSIGN EXISTING UNASSIGNED COMPLAINTS
    # -----------------------------------------------------
    assignment_changed = False
    for existing_query in Query.query.filter(
        Query.assigned_admin.is_(None)
    ).all():
        if ensure_query_assignment(existing_query):
            assignment_changed = True

    if assignment_changed:
        db.session.commit()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# STUDENT LOGIN
# =========================================================

@app.route(
    "/student-login",
    methods=["GET", "POST"]
)
def student_login():

    if request.method == "POST":

        # -------------------------------------------------
        # GET LOGIN DETAILS
        # -------------------------------------------------

        student_id = request.form.get(
            "student_id",
            ""
        ).strip().upper()

        password = request.form.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # VALIDATE STUDENT ID
        # -------------------------------------------------

        if not student_id:

            flash(
                "Please enter your Register Number.",
                "error"
            )

            return render_template(
                "student_login.html"
            )

        # -------------------------------------------------
        # FIND REGISTERED STUDENT
        # -------------------------------------------------

        student = User.query.filter_by(
            user_id=student_id,
            role="student"
        ).first()

        if not student:

            flash(
                "Invalid Register Number.",
                "error"
            )

            return render_template(
                "student_login.html"
            )

        # -------------------------------------------------
        # VALIDATE PASSWORD
        # -------------------------------------------------

        if not password:

            flash(
                "Please enter your password.",
                "error"
            )

            return render_template(
                "student_login.html"
            )

        if not check_password_hash(
            student.password,
            password
        ):

            flash(
                "Invalid Register Number or Password.",
                "error"
            )

            return render_template(
                "student_login.html"
            )

        # -------------------------------------------------
        # CREATE LOGIN SESSION
        # -------------------------------------------------

        # Do not clear the session here. Clearing the whole session can
        # unexpectedly remove other session state while navigating.
        session.permanent = True
        session["user_id"] = student.id
        session["user_role"] = "student"
        session["user_name"] = student.name

        return redirect(
            url_for(
                "student_dashboard"
            )
        )

    return render_template(
        "student_login.html"
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route(
    "/student-dashboard"
)
def student_dashboard():

    if session.get("user_role") != "student":

        return redirect(
            url_for(
                "student_login"
            )
        )

    student = db.session.get(User, session.get("user_id"))

    if not student:

        session.clear()

        return redirect(
            url_for(
                "student_login"
            )
        )

    # -----------------------------------------------------
    # GET STUDENT COMPLAINTS
    # -----------------------------------------------------

    queries = Query.query.filter_by(
        student_id=student.id
    ).order_by(
        Query.created_at.desc()
    ).all()

    # -----------------------------------------------------
    # ACTIVE COMPLAINT COUNT
    # -----------------------------------------------------

    active_count = Query.query.filter(

        Query.student_id == student.id,

        Query.status.in_([
            "Submitted",
            "Assigned",
            "Under Review",
            "In Progress"
        ])

    ).count()

    # -----------------------------------------------------
    # PENDING COMPLAINT COUNT
    # -----------------------------------------------------

    pending_count = Query.query.filter(

        Query.student_id == student.id,

        Query.status.in_([
            "Submitted",
            "Assigned",
            "Under Review"
        ])

    ).count()

    # -----------------------------------------------------
    # RESOLVED COMPLAINT COUNT
    # -----------------------------------------------------

    resolved_count = Query.query.filter(

        Query.student_id == student.id,

        Query.status == "Resolved"

    ).count()

    # -----------------------------------------------------
    # UNREAD STUDENT NOTIFICATIONS
    # -----------------------------------------------------

    unread_notifications = Notification.query.filter_by(

        user_id=student.id,

        is_read=False

    ).count()

    return render_template(

        "student_dashboard.html",

        student=student,

        queries=queries,

        active_count=active_count,

        pending_count=pending_count,

        resolved_count=resolved_count,

        unread_notifications=unread_notifications

    )


# =========================================================
# RAISE COMPLAINT
# =========================================================

@app.route(
    "/raise-complaint",
    methods=["GET", "POST"]
)
def raise_complaint():

    if session.get("user_role") != "student":

        return redirect(
            url_for(
                "student_login"
            )
        )

    student = db.session.get(User, session.get("user_id"))

    if not student:

        session.clear()

        return redirect(
            url_for(
                "student_login"
            )
        )

    departments = Department.query.order_by(
        Department.name
    ).all()

    if request.method == "POST":

        department_id = request.form.get(
            "department_id"
        )

        category = request.form.get(
            "category",
            ""
        ).strip()

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        priority = request.form.get(
            "priority",
            "Normal"
        ).strip()

        # -------------------------------------------------
        # VALIDATE DEPARTMENT
        # -------------------------------------------------

        if not department_id:

            flash(
                "Please select a department.",
                "complaint_error"
            )

            return render_template(
                "raise_complaint.html",
                departments=departments,
                category_options=CATEGORY_OPTIONS
            )

        department = db.session.get(
            Department,
            int(department_id)
        )

        if not department:

            flash(
                "Invalid department selected.",
                "complaint_error"
            )

            return render_template(
                "raise_complaint.html",
                departments=departments,
                category_options=CATEGORY_OPTIONS
            )

        # -------------------------------------------------
        # VALIDATE CATEGORY
        # -------------------------------------------------

        if not category:

            flash(
                "Please select a category.",
                "complaint_error"
            )

            return render_template(
                "raise_complaint.html",
                departments=departments,
                category_options=CATEGORY_OPTIONS
            )

        valid_categories = CATEGORY_OPTIONS.get(
            department.name,
            []
        )

        if category not in valid_categories:

            flash(
                "Please select a valid category for the selected department.",
                "complaint_error"
            )

            return render_template(
                "raise_complaint.html",
                departments=departments,
                category_options=CATEGORY_OPTIONS
            )

        # -------------------------------------------------
        # VALIDATE SUBJECT
        # -------------------------------------------------

        if not subject:

            flash(
                "Please enter a subject.",
                "complaint_error"
            )

            return render_template(
                "raise_complaint.html",
                departments=departments,
                category_options=CATEGORY_OPTIONS
            )

        # -------------------------------------------------
        # VALIDATE DESCRIPTION
        # -------------------------------------------------

        if not description:

            flash(
                "Please describe your complaint.",
                "complaint_error"
            )

            return render_template(
                "raise_complaint.html",
                departments=departments,
                category_options=CATEGORY_OPTIONS
            )

        # -------------------------------------------------
        # VALIDATE PRIORITY
        # -------------------------------------------------

        allowed_priorities = [
            "Low",
            "Normal",
            "High",
            "Urgent"
        ]

        if priority not in allowed_priorities:

            priority = "Normal"

        # -------------------------------------------------
        # GENERATE TICKET ID
        # -------------------------------------------------

        ticket_id = (

            "QRY-"

            + ist_now().strftime(
                "%Y%m%d"
            )

            + "-"

            + uuid.uuid4().hex[:6].upper()

        )

        # -------------------------------------------------
        # CREATE COMPLAINT
        # -------------------------------------------------

        current_time = ist_now()

        new_query = Query(

            ticket_id=ticket_id,

            student_id=student.id,

            department_id=department.id,

            category=category,

            subject=subject,

            description=description,

            priority=priority,

            status="Submitted",

            created_at=current_time,

            updated_at=current_time

        )

        db.session.add(
            new_query
        )

        db.session.commit()

        # -------------------------------------------------
        # AUTOMATIC DEPARTMENT ASSIGNMENT
        # -------------------------------------------------
        assigned_admin = ensure_query_assignment(new_query)
        db.session.commit()

        # -------------------------------------------------
        # NOTIFY RESPONSIBLE ADMINISTRATORS
        # -------------------------------------------------
        notify_admins = []

        if assigned_admin:
            notify_admins.append(assigned_admin)

        overall_admin = User.query.filter_by(
            user_id=OVERALL_ADMIN_ID,
            role="admin"
        ).first()

        if overall_admin and all(admin.id != overall_admin.id for admin in notify_admins):
            notify_admins.append(overall_admin)

        for admin in notify_admins:
            db.session.add(
                Notification(
                    user_id=admin.id,
                    query_id=new_query.id,
                    message=(
                        f"New complaint {ticket_id} "
                        f"has been submitted by {student.name}."
                    ),
                    is_read=False,
                    created_at=ist_now()
                )
            )

        db.session.commit()

        # -------------------------------------------------
        # REDIRECT TO SUCCESS PAGE
        # -------------------------------------------------

        return redirect(

            url_for(

                "complaint_success",

                ticket_id=ticket_id

            )

        )

    return render_template(

        "raise_complaint.html",

        departments=departments,

        category_options=CATEGORY_OPTIONS

    )


# =========================================================
# COMPLAINT SUCCESS
# =========================================================

@app.route(
    "/complaint-success/<ticket_id>"
)
def complaint_success(ticket_id):

    if session.get("user_role") != "student":

        return redirect(
            url_for(
                "student_login"
            )
        )

    query = Query.query.filter_by(
        ticket_id=ticket_id
    ).first()

    if not query:

        return redirect(
            url_for(
                "student_dashboard"
            )
        )

    return render_template(

        "complaint_success.html",

        query=query

    )


# =========================================================
# TRACK COMPLAINT
# =========================================================

@app.route(
    "/track-query/<ticket_id>"
)
def track_query(ticket_id):

    if session.get("user_role") != "student":

        return redirect(
            url_for(
                "student_login"
            )
        )

    student = db.session.get(User, session.get("user_id"))

    if not student:

        session.clear()

        return redirect(
            url_for(
                "student_login"
            )
        )

    query = Query.query.filter_by(

        ticket_id=ticket_id,

        student_id=student.id

    ).first()

    if not query:

        flash(
            "The requested complaint could not be found.",
            "error"
        )

        return redirect(
            url_for(
                "student_dashboard"
            )
        )

    department = db.session.get(
        Department,
        query.department_id
    )

    messages = Message.query.filter_by(

        query_id=query.id

    ).order_by(

        Message.created_at.asc()

    ).all()

    feedback = Feedback.query.filter_by(

        query_id=query.id

    ).first()

    return render_template(

        "track_query.html",

        query=query,

        department=department,

        messages=messages,

        feedback=feedback

    )


# =========================================================
# STUDENT SUBMIT FEEDBACK
# =========================================================

@app.route(
    "/submit-feedback/<ticket_id>",
    methods=["POST"]
)
def submit_feedback(ticket_id):

    if session.get("user_role") != "student":
        return redirect(
            url_for("student_login")
        )

    student_id = session.get("user_id")

    query = Query.query.filter_by(
        ticket_id=ticket_id,
        student_id=student_id
    ).first()

    if not query:
        flash("Complaint not found.", "feedback_error")
        return redirect(url_for("student_dashboard"))

    if query.status != "Resolved":
        flash(
            "Feedback can be submitted only after the complaint is resolved.",
            "feedback_error"
        )
        return redirect(url_for("track_query", ticket_id=ticket_id))

    existing_feedback = Feedback.query.filter_by(
        query_id=query.id
    ).first()

    if existing_feedback:
        flash(
            "Feedback has already been submitted for this complaint.",
            "feedback_error"
        )
        return redirect(url_for("track_query", ticket_id=ticket_id))

    rating_value = request.form.get("rating", "").strip()

    try:
        rating = int(rating_value)
    except (TypeError, ValueError):
        flash("Please select a valid rating.", "feedback_error")
        return redirect(url_for("track_query", ticket_id=ticket_id))

    if rating < 1 or rating > 5:
        flash("Please select a rating between 1 and 5.", "feedback_error")
        return redirect(url_for("track_query", ticket_id=ticket_id))

    comment = request.form.get("comment", "").strip()

    if len(comment) > 1000:
        flash("Feedback comment is too long.", "feedback_error")
        return redirect(url_for("track_query", ticket_id=ticket_id))

    new_feedback = Feedback(
        query_id=query.id,
        rating=rating,
        comment=comment if comment else None,
        created_at=ist_now()
    )

    db.session.add(new_feedback)
    db.session.commit()

    flash(
        "Thank you! Your feedback has been submitted successfully.",
        "feedback_success"
    )

    return redirect(
        url_for(
            "track_query",
            ticket_id=ticket_id
        )
    )


# =========================================================
# STUDENT LOGOUT
# =========================================================

@app.route(
    "/student-logout"
)
def student_logout():

    session.clear()

    return redirect(
        url_for(
            "home"
        )
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin-login",
    methods=["GET", "POST"]
)
def admin_login():
    if request.method == "POST":
        admin_id = request.form.get("admin_id", "").strip().upper().replace(" ", "")
        password = request.form.get("password", "")

        admin = User.query.filter_by(
            user_id=admin_id,
            role="admin"
        ).first()

        if admin and check_password_hash(admin.password, password):
            session.permanent = True
            session["user_id"] = admin.id
            session["user_role"] = "admin"
            session["user_name"] = admin.name
            return redirect(url_for("admin_dashboard"))

        flash("Invalid Admin ID or Password.", "error")

    return render_template("admin_login.html")

# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route(
    "/admin-dashboard"
)
def admin_dashboard():
    if session.get("user_role") != "admin":
        return redirect(url_for("admin_login"))

    admin = db.session.get(User, session.get("user_id"))
    if not admin or admin.role != "admin":
        session.clear()
        return redirect(url_for("admin_login"))

    # Ensure old records are assigned before displaying the dashboard.
    assignment_changed = False
    for query in Query.query.filter(Query.assigned_admin.is_(None)).all():
        if ensure_query_assignment(query):
            assignment_changed = True
    if assignment_changed:
        db.session.commit()

    if is_overall_admin(admin):
        queries = Query.query.order_by(Query.created_at.desc()).all()
        departments = Department.query.order_by(Department.name).all()
    else:
        allowed_names = get_admin_department_names(admin)
        allowed_departments = Department.query.filter(
            Department.name.in_(allowed_names)
        ).order_by(Department.name).all()
        allowed_ids = [department.id for department in allowed_departments]
        queries = Query.query.filter(
            Query.department_id.in_(allowed_ids)
        ).order_by(Query.created_at.desc()).all() if allowed_ids else []
        departments = allowed_departments

    total_count = len(queries)
    pending_count = sum(
        query.status in ["Submitted", "Assigned", "Under Review"]
        for query in queries
    )
    progress_count = sum(query.status == "In Progress" for query in queries)
    resolved_count = sum(query.status == "Resolved" for query in queries)

    students_list = User.query.filter_by(role="student").all()
    students = {student.id: student for student in students_list}
    department_map = {department.id: department for department in departments}

    feedback_query_ids = {query.id for query in queries}

    feedbacks = (
        Feedback.query
        .filter(Feedback.query_id.in_(feedback_query_ids))
        .order_by(Feedback.created_at.desc())
        .all()
    ) if feedback_query_ids else []

    feedback_map = {
        feedback.query_id: feedback
        for feedback in feedbacks
    }

    feedback_count = len(feedbacks)

    average_rating = (
        round(
            sum(feedback.rating for feedback in feedbacks) / feedback_count,
            1
        )
        if feedback_count
        else 0
    )

    awaiting_feedback = sum(
        query.status == "Resolved"
        and query.id not in feedback_map
        for query in queries
    )

    unread_admin_notifications = Notification.query.filter_by(
        user_id=admin.id,
        is_read=False
    ).count()

    return render_template(
        "admin_dashboard.html",
        admin=admin,
        queries=queries,
        total_count=total_count,
        pending_count=pending_count,
        progress_count=progress_count,
        resolved_count=resolved_count,
        students=students,
        departments=departments,
        department_map=department_map,
        unread_admin_notifications=unread_admin_notifications,
        average_rating=average_rating,
        feedback_count=feedback_count,
        awaiting_feedback=awaiting_feedback,
        feedbacks=feedbacks,
        feedback_map=feedback_map,
        admin_departments=get_admin_department_names(admin),
        is_overall_admin=is_overall_admin(admin)
    )

# =========================================================
# ADMIN VIEW COMPLAINT
# =========================================================

@app.route(
    "/admin-view-complaint/<ticket_id>"
)
def admin_view_complaint(ticket_id):
    if session.get("user_role") != "admin":
        return redirect(url_for("admin_login"))

    admin = db.session.get(User, session.get("user_id"))
    query = Query.query.filter_by(ticket_id=ticket_id).first()

    if not admin or admin.role != "admin":
        session.clear()
        return redirect(url_for("admin_login"))

    if not query:
        flash("Complaint not found.", "error")
        return redirect(url_for("admin_dashboard"))

    assigned_admin = ensure_query_assignment(query)
    db.session.commit()

    if not admin_can_access_query(admin, query):
        flash("You are not authorized to access this complaint.", "error")
        return redirect(url_for("admin_dashboard"))

    student = db.session.get(User, query.student_id)
    department = db.session.get(Department, query.department_id)
    messages = Message.query.filter_by(query_id=query.id).order_by(Message.created_at.asc()).all()

    unread_admin_notifications = Notification.query.filter_by(
        user_id=admin.id,
        is_read=False
    ).count()

    return render_template(
        "admin_view_complaint.html",
        admin=admin,
        query=query,
        student=student,
        department=department,
        assigned_admin=assigned_admin,
        messages=messages,
        unread_admin_notifications=unread_admin_notifications
    )

# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route(
    "/admin-logout"
)
def admin_logout():

    session.clear()

    return redirect(
        url_for(
            "home"
        )
    )


# =========================================================
# ADMIN REPLY TO COMPLAINT
# =========================================================

@app.route(
    "/admin-reply/<ticket_id>",
    methods=["POST"]
)
def admin_reply_complaint(ticket_id):
    if session.get("user_role") != "admin":
        return redirect(url_for("admin_login"))

    admin = db.session.get(User, session.get("user_id"))
    query = Query.query.filter_by(ticket_id=ticket_id).first()

    if not admin or admin.role != "admin":
        session.clear()
        return redirect(url_for("admin_login"))

    if not query:
        flash("Complaint not found.", "error")
        return redirect(url_for("admin_dashboard"))

    assigned_admin = ensure_query_assignment(query)
    db.session.commit()

    if not admin_can_access_query(admin, query):
        flash("You are not authorized to respond to this complaint.", "error")
        return redirect(url_for("admin_dashboard"))

    message_text = request.form.get("message", "").strip()
    if not message_text:
        flash("Please enter a response.", "error")
        return redirect(url_for("admin_view_complaint", ticket_id=ticket_id))

    db.session.add(
        Message(
            query_id=query.id,
            sender_id=admin.id,
            message=message_text,
            created_at=ist_now()
        )
    )
    query.updated_at = ist_now()
    db.session.add(
        Notification(
            user_id=query.student_id,
            query_id=query.id,
            message=f"Administrator has replied to your complaint {query.ticket_id}.",
            is_read=False,
            created_at=ist_now()
        )
    )
    db.session.commit()

    flash("Reply sent successfully.", "success")
    return redirect(url_for("admin_view_complaint", ticket_id=ticket_id))

# =========================================================
# ADMIN UPDATE COMPLAINT STATUS
# =========================================================

@app.route(
    "/admin-update-status/<ticket_id>",
    methods=["POST"]
)
def admin_update_status(ticket_id):
    if session.get("user_role") != "admin":
        return redirect(url_for("admin_login"))

    admin = db.session.get(User, session.get("user_id"))
    query = Query.query.filter_by(ticket_id=ticket_id).first()

    if not admin or admin.role != "admin":
        session.clear()
        return redirect(url_for("admin_login"))

    if not query:
        flash("Complaint not found.", "error")
        return redirect(url_for("admin_dashboard"))

    ensure_query_assignment(query)
    db.session.commit()

    if not admin_can_access_query(admin, query):
        flash("You are not authorized to update this complaint.", "error")
        return redirect(url_for("admin_dashboard"))

    new_status = request.form.get("status", "").strip()
    allowed_statuses = ["Submitted", "Assigned", "Under Review", "In Progress", "Resolved"]

    if new_status not in allowed_statuses:
        flash("Invalid complaint status.", "error")
        return redirect(url_for("admin_view_complaint", ticket_id=ticket_id))

    old_status = query.status
    if old_status == new_status:
        flash(f"Complaint is already marked as {new_status}.", "error")
        return redirect(url_for("admin_view_complaint", ticket_id=ticket_id))

    query.status = new_status
    query.updated_at = ist_now()
    db.session.add(
        Notification(
            user_id=query.student_id,
            query_id=query.id,
            message=f"Your complaint {query.ticket_id} has been updated from {old_status} to {new_status}.",
            is_read=False,
            created_at=ist_now()
        )
    )
    db.session.commit()

    flash(f"Complaint status updated to {new_status}.", "success")
    return redirect(url_for("admin_view_complaint", ticket_id=ticket_id))

# =========================================================
# STUDENT NOTIFICATIONS
# =========================================================

@app.route(
    "/notifications"
)
def notifications():

    if session.get("user_role") != "student":

        return redirect(
            url_for(
                "student_login"
            )
        )

    student_id = session.get(
        "user_id"
    )

    notifications_list = Notification.query.filter_by(

        user_id=student_id

    ).order_by(

        Notification.created_at.desc()

    ).all()

    # -----------------------------------------------------
    # MARK STUDENT NOTIFICATIONS AS READ
    # -----------------------------------------------------

    for notification in notifications_list:

        notification.is_read = True

    db.session.commit()

    return render_template(

        "notifications.html",

        notifications=notifications_list

    )


# =========================================================
# ADMIN NOTIFICATIONS
# =========================================================

@app.route(
    "/admin-notifications"
)
def admin_notifications():
    if session.get("user_role") != "admin":
        return redirect(url_for("admin_login"))

    admin = db.session.get(User, session.get("user_id"))
    if not admin or admin.role != "admin":
        session.clear()
        return redirect(url_for("admin_login"))

    notifications_list = Notification.query.filter_by(
        user_id=admin.id
    ).order_by(Notification.created_at.desc()).all()

    notification_tickets = {}
    for notification in notifications_list:
        if notification.query_id:
            query = db.session.get(Query, notification.query_id)
            if query:
                notification_tickets[notification.id] = query.ticket_id

    for notification in notifications_list:
        notification.is_read = True
    db.session.commit()

    return render_template(
        "admin_notifications.html",
        admin=admin,
        notifications=notifications_list,
        notification_tickets=notification_tickets
    )

# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    # Keep one stable Flask process during development so the browser
    # session is not affected by the debug auto-reloader.
    app.run(
        debug=True,
        use_reloader=False
    )