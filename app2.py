import os
import json
from tempfile import NamedTemporaryFile
import streamlit as st
from pyresparser import ResumeParser
import pandas as pd

from courses import android_course,ds_course,interview_videos,ios_course,resume_videos,uiux_course,web_course
import base64
import time
import nltk
import spacy  # Import spaCy
import io,random
nltk.download('stopwords')

import pdfplumber  # Import pdfplumber
from streamlit_tags import st_tags
import io, random
import warnings

def show_pdf(file):
    pdf_data = file.read()
    base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def pdf_reader(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def courserecommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    c=0
    rec_course = []
    no_of_rec = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name,c_link in course_list:
        c+=1
        st.markdown(f"({c}) ({c_name}) ({c_link})")
        rec_course.append(c_name)
        if c==no_of_rec:
            break
    return rec_course



def parse_resume(resume_path):
    try:
        data = ResumeParser(resume_path).get_extracted_data()
        return data
    except Exception as e:
        return {"error": str(e)}

def check_eligibility(resume_data, required_skills):
    if "skills" not in resume_data or resume_data["skills"] is None:
        return False, []
    
    extracted_skills = [skill.lower() for skill in resume_data["skills"]]
    required_skills_list = [skill.lower().strip() for skill in required_skills.split(",")]
    matched_skills = list(set(required_skills_list) & set(extracted_skills))
    is_eligible = len(matched_skills) > 0
    
    return is_eligible, matched_skills

# Streamlit UI
choice = st.sidebar.radio("Welcome,", options=["Resume Analyzer", "Check Eligibility"])

if choice == "Check Eligibility":
    st.title("Resume Eligibility Checker")
    uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    job_role = st.text_input("Enter Job Role")
    required_skills = st.text_area("Enter Required Skills (comma-separated)")

    if uploaded_file and job_role and required_skills:
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name

        st.write("### Parsing Resume...")
        resume_data = parse_resume(temp_file_path)
        os.remove(temp_file_path)

        if "error" in resume_data:
            st.error("Error parsing resume: " + resume_data["error"])
        else:
            # Convert resume data to a table-friendly format
            resume_table = {
                "Field": ["Name", "Email", "Contact", "Skills", "Total Experience", "No. of Pages"],
                "Value": [
                    resume_data.get("name", "Not Available"),
                    resume_data.get("email", "Not Available"),
                    resume_data.get("mobile_number", "Not Available"),
                    ", ".join(resume_data.get("skills", [])) if resume_data.get("skills") else "None",
                    resume_data.get("total_experience", "Not Available"),
                    str(resume_data.get("no_of_pages", "Not Available"))
                ]
            }
            df = pd.DataFrame(resume_table)
            
            eligibility, matched_skills = check_eligibility(resume_data, required_skills)
            
            st.write("### Resume Data")
            st.table(df)  # Display resume data as a table

            if eligibility:
                st.success(f"✅ The resume is eligible for the role: {job_role}!")
                st.write("**Matched Skills:**", ", ".join(matched_skills) if matched_skills else "None")
            else:
                st.error(f"❌ The resume does not meet the required skills for {job_role}.")
                st.write("**Matched Skills:**", ", ".join(matched_skills) if matched_skills else "None")

elif choice == "Resume Analyzer":
    st.title("Resume Analyzer")

    st.markdown("""### Upload your resume and get smart recommendations""")
    file = st.file_uploader("Upload your resume here:", type="pdf")
    if file is not None:
        with st.spinner("Uploading your resume...."):
            time.sleep(2)

            # Save file to path
            save_path = f"./uploaded_resume/{file.name}"
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())

            # Display uploaded PDF
            show_pdf(file)
            st.success("Uploaded successfully")

        # Proceed with resume parsing after the file is uploaded
        try:
            # Attempt to parse the resume
            resume_data = ResumeParser(save_path).get_extracted_data()
            if resume_data:
                warnings.filterwarnings("ignore", message="[W094]")
                resume_text=pdf_reader(save_path)
                
                st.header("Resume Analysis:")
                st.success(f"Hello {resume_data.get('name', 'User')}")
                st.subheader("Your Basic Info:")
                try:
                    print(resume_data)
                    print(resume_text)
                    name = resume_data.get('name', 'Not available')
                    email = resume_data.get('email', 'Not available')
                    contact = resume_data.get('mobile_number', 'Not available')
                    no_of_pages = resume_data.get('no_of_pages', 'Not available')
                    skills = resume_data.get('skills', [])

                    st.markdown(f'**Name**: {name}')
                    st.markdown(f'**Email**: {email}')
                    st.markdown(f'**Contact**: {contact}')
                    st.markdown(f'**Resume Pages**: {no_of_pages}')
                    
                    level = ""
                    if no_of_pages == 1:
                        level="fresher"
                    elif no_of_pages == 2:
                        level ="intermediate"
                    elif no_of_pages >=3:
                        level = "Experienced"
                            
                    st.markdown(f"you are at {level} level")

                    st.subheader("**Skills Recommendation💡**")

                    keywords = st_tags(label="Your Current Skills",text="See our skills recommendation below",value=resume_data['skills'])

                    #recommedtions:
                    ds_keyword = [
                        'tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 
                        'flask', 'streamlit', 'scikit-learn', 'matplotlib', 'seaborn', 'numpy', 
                        'pandas', 'data visualization', 'big data', 'hadoop', 'spark', 'sql', 
                        'data analysis', 'data cleaning', 'feature engineering', 'ai', 
                        'nlp', 'opencv', 'time series analysis', 'recommender systems', 
                        'data mining', 'bayesian statistics', 'statistics', 'tableau', 'power bi'
                    ]

                    web_keyword = [
                        'react', 'django', 'node.js', 'react.js', 'php', 'laravel', 
                        'magento', 'wordpress', 'javascript', 'angular.js', 'c#', 'flask', 
                        'html', 'css', 'bootstrap', 'tailwind css', 'vue.js', 'next.js', 
                        'svelte', 'web sockets', 'graphql', 'api development', 'web scraping', 
                        'json', 'xml', 'sass', 'less', 'typescript', 'jquery', 
                        'backend development', 'frontend development', 'progressive web apps'
                    ]                   

                    android_keyword = [
                        'android', 'android development', 'flutter', 'kotlin', 'xml', 
                        'kivy', 'java', 'android studio', 'jetpack compose', 'sqlite', 
                        'mvvm architecture', 'rxjava', 'dagger', 'hilt', 'firebase', 
                        'material design', 'gradle', 'android ndk', 'coroutines', 'livedata', 
                        'databinding', 'retrofit', 'okhttp', 'room database'
                    ]

                    ios_keyword = [
                        'ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode', 
                        'objective-c', 'swiftui', 'core data', 'core animation', 
                        'ui kit', 'app store', 'apple developer', 'metal', 'cloudkit', 
                        'mvvm architecture', 'ar kit', 'core ml', 'firebase', 'storyboard', 
                        'auto layout', 'push notifications', 'in-app purchases'
                    ]

                    uiux_keyword = [
    'ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 
    'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 
    'photoshop', 'editing', 'adobe illustrator', 'illustrator', 
    'adobe after effects', 'after effects', 'adobe premiere pro', 
    'premiere pro', 'adobe indesign', 'indesign', 'wireframe', 
    'solid', 'grasp', 'user research', 'user experience', 'design thinking', 
    'motion design', 'interaction design', 'service design', 
    'persona development', 'journey mapping', 'usability testing', 
    'a/b testing', 'responsive design', 'accessibility', 'mobile-first design', 
    'material design', 'human-centered design', 'storyboarding'
]


                    recommended_skills = []
                    reco_field = ""
                    reco_course = ''
                    for i in resume_data['skills']:
                        if i.lower() in ds_keyword:
                            print(i.lower())
                            reco_field = "Data Science or AI/ML"
                            st.success("** Our analysis says you are looking for Data Science or AI/ML Jobs.**")
                            recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                            recommended_keywords = st_tags(label="### Recommended skills for you.",text="Recommended skills generated from System",value=recommended_skills)
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h4>''',unsafe_allow_html=True)
                            rec_course = courserecommender(ds_course)
                    
                            break
                        elif i.lower() in uiux_keyword:
                            print(i.lower())
                            reco_field="Ui/UX Designer"
                            st.success("** Our analysis says you are looking for UI/UX Jobs.**")
                            recommended_skills_ui = ['Adobe XD', 'Figma', 'Sketch', 'InVision', 'Zeplin', 'Wireframing', 'Prototyping', 'Adobe Photoshop',
    'Adobe Illustrator', 'Balsamiq', 'User Research', 'User Experience (UX) Design', 'Interaction Design',
    'Usability Testing', 'Storyboarding', 'User Interface (UI) Design', 'Responsive Design', 'Mobile-First Design',
    'Design Systems', 'Typography', 'Color Theory', 'Branding', 'User Journey Mapping', 'Information Architecture',
    'A/B Testing', 'User Testing', 'Visual Design', 'Motion Design', 'Animations (UI)', 'Accessibility Design',
    'Design Thinking', 'Figma Prototyping', 'High-Fidelity Mockups', 'Iconography', 'Material Design Principles',
    'Microinteractions']
                            recommended_keywords = st_tags(label="### Recommended skills for you.",text="Recommended skills generated from System",value=recommended_skills_ui)
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h4>''',unsafe_allow_html=True)
                            rec_course = courserecommender(uiux_course)
                            break
                        elif i.lower() in android_keyword:
                            print(i.lower())
                            reco_field="Android/flutter app development"
                            st.success("** Our analysis says you are looking for Android/flutter Development Jobs.**")
                            recommended_skills_app = ['Android SDK', 'Flutter', 'Kotlin', 'Java', 'Dart', 'Android Studio', 'Jetpack Compose', 'MVVM Architecture',
    'Firebase', 'SQLite', 'Retrofit', 'Room Database', 'Material Design', 'Coroutines', 'LiveData',
    'Dependency Injection (Dagger, Hilt)', 'RxJava', 'Push Notifications', 'Gradle', 'NDK',
    'Flutter Widgets', 'Flutter Animations', 'Cloud Functions', 'RESTful API', 'Google Maps SDK',
    'Google Play Services', 'Bluetooth Integration', 'Camera API', 'App Debugging and Optimization',
    'Continuous Integration (CI)', 'App Store Deployment', 'Cross-platform development (for Android/iOS)',
    'Custom Views', 'Reactive Programming']
                            recommended_keywords = st_tags(label="### Recommended skills for you.",text="Recommended skills generated from System",value=recommended_skills_app)
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h4>''',unsafe_allow_html=True)
                            rec_course = courserecommender(android_course)

                            break

                        elif i.lower() in ios_keyword:
                            print(i.lower())
                            reco_field="IOS app development"
                            st.success("** Our analysis says you are looking for IOS App Development Jobs.**")
                            recommended_skills_ios = ['Swift', 'Objective-C', 'Xcode', 'SwiftUI', 'UIKit', 'CoreData', 'CoreAnimation', 'AutoLayout', 
    'Push Notifications', 'Firebase', 'iCloud', 'CloudKit', 'MVVM Architecture', 'ARKit', 'Metal', 
    'CoreML', 'Storyboard', 'In-App Purchases', 'Git', 'RESTful APIs', 'UI Testing', 'Unit Testing (XCTest)',
    'Reactive Programming (RxSwift)', 'Debugging in Xcode', 'Apple Push Notification Service (APNS)',
    'App Store Deployment', 'CoreBluetooth', 'SpriteKit', 'SceneKit', 'WatchOS Development', 'SiriKit',
    'MapKit', 'HealthKit', 'Cloud Functions']
                            recommended_keywords = st_tags(label="### Recommended skills for you.",text="Recommended skills generated from System",value=recommended_skills_ios)
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h4>''',unsafe_allow_html=True)
                            rec_course = courserecommender(ios_course)
                            break

                        elif i.lower() in web_keyword:
                            print(i.lower())
                            reco_field="Web development"
                            st.success("** Our analysis says you are looking for Web Development Jobs.**")
                            recommended_skills_web = ['HTML5', 'CSS3', 'JavaScript', 'React.js', 'Angular.js', 'Vue.js', 'Node.js', 'Express.js', 'PHP',
    'Laravel', 'Django', 'Ruby on Rails', 'RESTful APIs', 'GraphQL', 'Bootstrap', 'Tailwind CSS', 'SASS/LESS',
    'WebSockets', 'jQuery', 'AJAX', 'TypeScript', 'Next.js', 'Webpack', 'Git', 'Docker', 'Nginx', 'MongoDB',
    'PostgreSQL', 'MySQL', 'Firebase', 'Firebase Authentication', 'Cloud Storage', 'Web Scraping', 'OAuth',
    'SEO Optimization', 'Content Management Systems (WordPress, Joomla)', 'Cross-Browser Compatibility',
    'Server-Side Rendering (SSR)', 'Progressive Web Apps (PWA)', 'Responsive Design', 'UI/UX Principles for Web',
    'Test-Driven Development (TDD)']
                            recommended_keywords = st_tags(label="### Recommended skills for you.",text="Recommended skills generated from System",value=recommended_skills_web)
                            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h4>''',unsafe_allow_html=True)
                            rec_course = courserecommender(web_course)
                            break
                    
                    st.subheader("**Resume Tips & Ideas💡**")
                    res_score = 0
                    res_text_lower = resume_text.lower()

                    if "objectives" in res_text_lower:
                        res_score+=20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h5>''', unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h5>''', unsafe_allow_html=True)
                    if "declaration" in res_text_lower:
                        resume_score = res_score + 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration/h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Declaration. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',unsafe_allow_html=True)
                    if 'hobbies' in res_text_lower or 'interests' in res_text_lower:
                        res_score += 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h5>''', unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Hobbies or Interests. This shows your personality and fitness for the role.</h5>''', unsafe_allow_html=True)

                    # Achievements
                    if 'achievements' in res_text_lower:
                        res_score += 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements</h5>''', unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. This shows your capability for the required position.</h5>''', unsafe_allow_html=True)

                    if 'projects' in res_text_lower:
                        res_score += 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h5>''', unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It shows your work experience related to the required position.</h5>''', unsafe_allow_html=True)

                    if "skills" in res_text_lower or "technical skills" in res_text_lower:
                        res_score += 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have listed your Skills</h5>''', unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add a Skills section. This shows your technical or soft skills relevant to the job.</h5>''', unsafe_allow_html=True)
                    if  res_text_lower or "experience" in res_text_lower or "work experience" in res_text_lower or "professional experience" in res_text_lower or "internship" in res_text_lower or res_text_lower or "internships" in res_text_lower:
                        res_score += 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Work Experience</h5>''', unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Work Experience. This shows your practical knowledge and past contributions.</h5>''', unsafe_allow_html=True)
                    if "certification" in res_text_lower or "certifications" in res_text_lower or res_text_lower or "courses" in res_text_lower or res_text_lower or "course" in res_text_lower:
                        res_score += 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Certifications</h5>''', unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Certifications. This adds credibility to your expertise.</h5>''', unsafe_allow_html=True)
                    if "linkedin" in res_text_lower or "linkedin.com" in res_text_lower:
                        res_score += 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added a LinkedIn profile</h5>''', unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add a LinkedIn profile. It provides professional credibility and helps recruiters learn more about your background.</h5>''', unsafe_allow_html=True)
                    if "github" in res_text_lower or "github.com" in res_text_lower:
                        res_score += 20
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added a GitHub profile</h5>''', unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add a GitHub profile. It showcases your projects, contributions, and coding skills to potential employers.</h5>''', unsafe_allow_html=True)
                    
                    st.subheader("**Resume Score📝**")
                    st.markdown(
                        """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                    )
        
                    my_bar = st.progress(0)
                    score = 0
                    for i in range(res_score):
                        score+=1
                        time.sleep(0.1)
                        my_bar.progress(i+1)
                    score=(100*score)/200
                    st.success('** Your Resume Writing Score: ' + str(score)+'**')
                    st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")
                    st.balloons()

                except:
                    pass

        except Exception as e:
            st.error(f"Error during resume parsing: {e}")


else:
    print("Streamlit is not available. Install it using 'pip install streamlit'")