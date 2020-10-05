from flask import Flask
from flask import request
from flask import render_template
from flask_pymongo import PyMongo
from datetime import timedelta
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
from datetime import datetime
from mongoengine import connect
import os
import urllib.request
from werkzeug.utils import secure_filename
import cv2
import face_recognition
import pickle
import encoding

app = Flask(__name__)
#MONGO_URI에는 본인의 mongodb atlas의 클러스터 주소를 생성하여 넣으면 된다.
app.config["MONGO_URI"]="mongodb+srv://jiyulLee:sh032418@cluster0.tsie7.mongodb.net/faceid?retryWrites=true&w=majority"
app.config["PERMANENT_SESSION_LIFETIME"]=timedelta(minutes=30)
mongo=PyMongo(app)

UPLOAD_FOLDER='static/uploads'

ALLOWED_EXTENSIONS=set(['jpg'])

Encodename=''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return redirect('/login')

#회원가입
@app.route("/sign_up", methods=["GET", "POST"])
def member_join():
    if request.method == "POST":
        name = request.form.get("name", type=str)
        userid = request.form.get("userid",type=str)
        email = request.form.get("email", type=str)
        pw = request.form.get("pw", type=str)
       
        #하나라도 입력되지 않은 값이 있으면 다시 화면으로 돌아감.
        if name == "" or userid=="" or email == "" or pw == "":
            flash("입력되지 않은 값이 있습니다!")
            return  render_template("sign_up.html")
        #파일이 첨부되지 않으면 
        if 'file[]' not in request.files:
            flash('No file part')
            return render_template("sign_up.html")

        members = mongo.db.test
        cnt = members.find({"userid": userid}).count()
        if cnt > 0:
            flash("중복된 id값이 있습니다!")
            return render_template("sign_up.html")


        files = request.files.getlist('file[]')
        
        #static/upload 폴더 안에 user id가 이름인 폴더를 생성하고, 사용자의 사진을 저장한다.
        UPLOAD_FOLDER2=UPLOAD_FOLDER+'/'+userid
        if(os.path.isdir(UPLOAD_FOLDER2)==False):
            os.mkdir(UPLOAD_FOLDER2)
        
        # 허용된 확장자인 jpg만 폴더에 저장한다
        for file in files:
            if file and allowed_file(file.filename):
                filename= secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER2,filename))
            
      
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        post = {
            "name": name,
            "userid":userid,
            "email": email,
            "pw": pw,
            "joindate": current_utc_time,
            "logintime": "",
            "logincount": 0,
        }

        members.insert_one(post)
        #execute file encoding
        Encodename=userid
        encoding.encoding_file(userid)
        
        return redirect('/login')

    else:
        return render_template("sign_up.html")
    

@app.route("/login", methods=["GET", "POST"])
def member_login():
    #1차인증 : 아이디, 비밀번호로 진행한다.
    if request.method == "POST":
        userid = request.form.get("userid")
        pass1 = request.form.get("pw")

        members = mongo.db.test
        #pdata는 2차 인증에서도 사용되기 때문에 전역변수로 지정한다.
        global pdata
        pdata = members.find_one({"userid": userid})

        if pdata is None:
            flash("회원 정보가 없습니다!!")
            return redirect(url_for("member_login"))
        else:
            #아이디, 비밀번호가 모두 일치하면 2차 인증페이지로 넘어간다.
            if pdata.get("pw") == pass1:
                session["userid"] = userid
                session["name"] = pdata.get("name")
                session.permanent = True
                return redirect(url_for("member_2nd_auth"))
            else:
                flash("비밀번호가 일치하지 않습니다.")
                return redirect(url_for("member_login"))

    else:
        return render_template("./login.html")


@app.route("/auth", methods=["GET", "POST"])
def member_2nd_auth():
                # 2차 인증 - faceid
                encoding_file = "encodings.pickle"
                  
                # Starts here
                data = pickle.loads(open(encoding_file, "rb").read())
                cnt = 0
                # 웹캠 읽어오기
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                while True:
                    # 비디오 캡쳐 시작
                    ret, frame = cap.read()
                    if frame is None:
                        print("No more captured frames!")
                        break
                    flipped = cv2.flip(frame, 1)
                    
                    # 얼굴이 위치한 영역 찾기
                    rgb = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
                    boxes = face_recognition.face_locations(rgb, model="HOG")

                    # 해당 영역에서 얼굴의 특징을 수치로 인코딩
                    encodings = face_recognition.face_encodings(rgb, boxes)
                    names = []
                    counts = {}

                    # 얼굴이 인식되었다면, 인식된 얼굴의 인코딩 수치를 encodings.pickle 파일에 있는 수치와 비교
                    if encodings:
                        print("encodings exist")
                        for encoding in encodings:
                            matches = face_recognition.compare_faces(
                                data["encodings"], encoding, tolerance=0.5
                            )
                            name = "unknown"
                            print(matches)

                            if True in matches:
                                # 비교해서 일치한 값(match)이 있다면, database 에서 이름을 가져와 match 에 붙여주기
                                print("True in matches!")
                                matchedIndxs = []
                                for (i, b) in enumerate(matches):
                                    if b == True:
                                        matchedIndxs.append(i)

                                # 두 명 이상과 일치한 값이 있다면, 더 많이 일치한 사람으로 인식
                                for items in matchedIndxs:
                                    name = data["names"][items]
                                    counts[name] = 0
                                for items in matchedIndxs:
                                    counts[data["names"][items]] = (
                                        counts.get(data["names"][items]) + 1
                                    )
                                name = max(counts, key=counts.get)
                                print()
                                names.append(name)
                                print(name)
                                print(counts)
                            else:
                                print("something not right!")
                      
                        # 웹캠에 인식된 얼굴에 박스 그려주기
                        for ((top, right, bottom, left), name) in zip(boxes, names):
                            y = top - 15
                            color = (255, 255, 0)
                            line = 1
                            if name == "unknown":
                                color = (255, 255, 255)
                                line = 1
                                name = ""
                            cv2.rectangle(
                                flipped, (left, top), (right, bottom), color, line
                            )
                            cv2.putText(
                                flipped,
                                name,
                                (left, y),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.75,
                                color,
                                line,
                            )

                        cv2.imshow("Recognition", flipped)
                       
                        # 회원 데이터베이스의 userid 값과 캡처 정보가 일치한 값이 있다면,
                        if pdata["userid"] in counts:
                             # 캡처 프레임 5개의 정보와 비교해 5번 이상 연속으로 일치하는지 확인
                            if counts[pdata["userid"]] > 4:
                                print("it's " + pdata["userid"] + "!")
                                cnt += 1
                                print(cnt)
                               # 5번 미만이라면 다시 로그인 페이지를 렌더링   
                            else:
                                cnt = 0
                                flash("인식에 실패하였습니다.")
                                print("cnt=0")
                                return redirect(url_for("member_login"))  
                        # 캡쳐에 일치한 값이 없다면 다시 로그인 페이지를 렌더링
                        else:
                            flash("인식에 실패하였습니다.")
                            cnt = 0
                            cap.release()
                            cv2.destroyAllWindows()
                            return redirect(url_for("member_login"))  
                    # 웹캠에 어떤 얼굴도 인식되지 않거나, 인코딩 정보가 없다면 다시 로그인 페이지를 렌더링
                    else:
                        print("encoding doesn't exist")
                        flash("카메라에 얼굴을 인식시켜주세요.")
                        cnt = 0
                        cap.release()
                        cv2.destroyAllWindows()
                        return redirect(url_for("member_login"))  

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
                    #캡처가 일치하고, 인식이 완료되었다면 성공 페이지를 렌더링한다.
                    if cnt == 5:
                        print("by 5")
                        cap.release()
                        cv2.destroyAllWindows()
                        cnt = 0
                        return render_template("./success.html")

                cap.release()
                cv2.destroyAllWindows()
                cnt = 0
                return redirect(url_for("member_login"))                
                # 여기까지


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host="0.0.0.0", debug=True, port=9000)
