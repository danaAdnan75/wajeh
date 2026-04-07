from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Add secret key for sessions

# Selection page template (now the main page)
SELECTION_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الخيارات التعليمية</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: #F5F5DC;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: #006C35;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            text-align: center;
            width: 320px;
            max-width: 90%;
        }
        .logo {
            font-size: 48px;
            font-weight: bold;
            color: #F5F5DC;
            margin-bottom: 20px;
            transition: all 0.5s ease;
        }
        .selection-title {
            font-size: 24px;
            font-weight: bold;
            color: #F5F5DC;
            margin-bottom: 30px;
        }
        .selection-btn {
            background: #F5F5DC;
            color: #006C35;
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            width: 100%;
            margin-bottom: 15px;
            transition: all 0.3s ease;
            font-weight: bold;
            transform: translateY(20px);
            opacity: 0;
        }
        .selection-btn:hover {
            background: #E6D7B8;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .selection-btn.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        /* Initial loading screen */
        .loading-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #F5F5DC;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            transition: opacity 0.8s ease;
        }
        
        .loading-logo {
            font-size: 80px;
            font-weight: bold;
            color: #006C35;
            animation: pulse 2s infinite, glow 2s infinite;
            text-shadow: 0 0 20px rgba(0, 108, 53, 0.3);
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        @keyframes glow {
            0%, 100% { text-shadow: 0 0 20px rgba(0, 108, 53, 0.3); }
            50% { text-shadow: 0 0 30px rgba(0, 108, 53, 0.8), 0 0 40px rgba(0, 108, 53, 0.6); }
        }
        
        .main-content {
            filter: blur(10px);
            transition: filter 0.8s ease;
        }
        
        .main-content.show {
            filter: blur(0);
        }
    </style>
</head>
<body>
    <!-- Loading screen -->
    <div class="loading-screen" id="loadingScreen">
        <div class="loading-logo">وجه</div>
    </div>
    
    <!-- Main content -->
    <div class="main-content" id="mainContent">
        <div class="container">
            <div class="logo">وجه</div>
            <div class="selection-title">الرجاء الاختيار</div>
            <button onclick="selectOption('first')" class="selection-btn" id="btn1">طلاب المدارس</button>
            <button onclick="selectOption('second')" class="selection-btn" id="btn2">طلاب الجامعة</button>
            <button onclick="selectOption('third')" class="selection-btn" id="btn3">قطاع التعليم</button>
        </div>
    </div>

    <script>
        function selectOption(option) {
            // Store the selected option and redirect to auth
            sessionStorage.setItem('selectedOption', option);
            window.location.href = '/auth';
        }
        
        // Initial loading animation
        window.addEventListener('load', function() {
            setTimeout(() => {
                // Hide loading screen
                document.getElementById('loadingScreen').style.opacity = '0';
                document.getElementById('mainContent').classList.add('show');
                
                setTimeout(() => {
                    document.getElementById('loadingScreen').style.display = 'none';
                    
                    // Animate buttons one by one
                    setTimeout(() => {
                        document.getElementById('btn1').classList.add('show');
                    }, 200);
                    setTimeout(() => {
                        document.getElementById('btn2').classList.add('show');
                    }, 400);
                    setTimeout(() => {
                        document.getElementById('btn3').classList.add('show');
                    }, 600);
                }, 800);
            }, 3000); // 3 seconds loading
        });
    </script>
</body>
</html>
'''

# Authorization template
AUTH_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: #F5F5DC;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: #006C35;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            text-align: center;
            width: 320px;
            max-width: 90%;
        }
        .logo {
            font-size: 48px;
            font-weight: bold;
            color: #F5F5DC;
            margin-bottom: 20px;
        }
        .subtitle {
            font-size: 18px;
            color: #F0F0F0;
            margin-bottom: 30px;
        }
        .input-field {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 20px;
            box-sizing: border-box;
            text-align: center;
            background: white;
            color: #333;
        }
        .input-field:focus {
            outline: none;
            border-color: #F5F5DC;
        }
        .btn {
            background: #F5F5DC;
            color: #333;
            border: 2px solid #D2B48C;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            margin-bottom: 10px;
            transition: all 0.2s;
        }
        .btn:hover {
            background: #E6D7B8;
            transform: translateY(-1px);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .hidden {
            display: none;
        }
        .phone-display {
            font-size: 18px;
            color: white;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .popup {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .popup:not(.hidden) {
            display: flex;
        }
        .popup-content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            max-width: 300px;
        }
        .success {
            color: #28a745;
            font-size: 20px;
            font-weight: bold;
        }
        .error {
            color: #FFB6C1;
            margin-top: 10px;
        }
        .back-to-home {
            background: #6c757d;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            margin-bottom: 20px;
            transition: all 0.2s;
        }
        .back-to-home:hover {
            background: #5a6268;
            transform: translateY(-1px);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Back to home button -->
        <button onclick="goToHome()" class="back-to-home">العودة الى الرئيسية</button>
        
        <!-- Step 1: ID Input -->
        <div id="step1">
            <div class="logo">وجه</div>
            <div class="subtitle">الرجاء ادخال رقم الهوية او الاقامة</div>
            <input type="text" id="idNumber" class="input-field" placeholder="رقم الهوية" maxlength="10">
            <button onclick="verifyId()" class="btn">التحقق</button>
            <div id="error1" class="error"></div>
        </div>

        <!-- Step 2: SMS Verification -->
        <div id="step2" class="hidden">
            <div class="logo">وجه</div>
            <div class="subtitle">تم إرسال رمز التحقق إلى</div>
            <div id="phoneDisplay" class="phone-display"></div>
            <input type="text" id="smsCode" class="input-field" placeholder="رمز التحقق" maxlength="4">
            <button onclick="verifySms()" class="btn">تأكيد</button>
            <button onclick="goBack()" class="btn" style="background: #6c757d;">رجوع</button>
            <div id="error2" class="error"></div>
        </div>
    </div>

    <!-- Success Popup -->
    <div id="successPopup" class="popup hidden">
        <div class="popup-content">
            <div class="success">تم تسجيل الدخول بنجاح</div>
            <button onclick="closePopup()" class="btn" style="margin-top: 20px; width: auto; padding: 10px 20px;">موافق</button>
        </div>
    </div>

    <script>
        function goToHome() {
            window.location.href = '/';
        }
        
        function verifyId() {
            const idNumber = document.getElementById('idNumber').value;
            const errorDiv = document.getElementById('error1');
            
            if (!idNumber || idNumber.length !== 10) {
                errorDiv.textContent = 'يرجى إدخال رقم هوية صحيح (10 أرقام)';
                return;
            }
            
            fetch('/verify_id', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id_number: idNumber})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('step1').classList.add('hidden');
                    document.getElementById('step2').classList.remove('hidden');
                    document.getElementById('phoneDisplay').textContent = data.masked_phone;
                    errorDiv.textContent = '';
                } else {
                    errorDiv.textContent = data.error;
                }
            });
        }
        
        function verifySms() {
            const smsCode = document.getElementById('smsCode').value.trim();
            const idNumber = document.getElementById('idNumber').value.trim();
            const errorDiv = document.getElementById('error2');
            
            errorDiv.textContent = '';
            
            if (!smsCode) {
                errorDiv.textContent = 'يرجى إدخال رمز التحقق';
                return;
            }
            
            if (smsCode.length !== 4) {
                errorDiv.textContent = 'رمز التحقق يجب أن يكون 4 أرقام';
                return;
            }
            
            if (!/^[0-9]+$/.test(smsCode)) {
                errorDiv.textContent = 'رمز التحقق يجب أن يحتوي على أرقام فقط';
                return;
            }
            
            fetch('/verify_sms', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id_number: idNumber, sms_code: smsCode})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('successPopup').classList.remove('hidden');
                    errorDiv.textContent = '';
                } else {
                    errorDiv.textContent = data.error;
                }
            })
            .catch(error => {
                errorDiv.textContent = 'حدث خطأ في الاتصال';
            });
        }
        
        function goBack() {
            document.getElementById('step2').classList.add('hidden');
            document.getElementById('step1').classList.remove('hidden');
            document.getElementById('smsCode').value = '';
            document.getElementById('error2').textContent = '';
        }
        
        function closePopup() {
            document.getElementById('successPopup').classList.add('hidden');
            // Get the selected option from sessionStorage and redirect
            const selectedOption = sessionStorage.getItem('selectedOption');
            if (selectedOption) {
                window.location.href = '/' + selectedOption;
            } else {
                window.location.href = '/';
            }
        }
        
        // Ensure popup is hidden when page loads
        window.addEventListener('load', function() {
            document.getElementById('successPopup').classList.add('hidden');
            document.getElementById('step2').classList.add('hidden');
            document.getElementById('step1').classList.remove('hidden');
        });
    </script>
</body>
</html>
'''

def init_database():
    """Initialize the SQLite database with sample data"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Drop existing table if it exists and create new one
    cursor.execute('DROP TABLE IF EXISTS users')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_number TEXT UNIQUE NOT NULL,
            phone_number TEXT NOT NULL,
            sms_code TEXT NOT NULL
        )
    ''')
    
    # Insert sample data
    sample_users = [
        ('1234567899', '0501234567', '8421'),
        ('9876543210', '0559876543', '8421'),
        ('1111222233', '0541112222', '8421'),
        ('5555666677', '0505556666', '8421')
    ]
    
    cursor.executemany('INSERT INTO users (id_number, phone_number, sms_code) VALUES (?, ?, ?)', sample_users)
    
    conn.commit()
    conn.close()

# School page template (enhanced with sidebar menu)
SCHOOL_PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>طلاب المدارس</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: #F5F5DC;
            min-height: 100vh;
        }
        
        /* Header with hamburger menu */
        .header {
            background: #006C35;
            padding: 15px 20px;
            position: relative;
        }
        
        /* Hamburger menu button */
        .hamburger {
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            z-index: 1001;
            transition: all 0.3s ease;
        }
        
        .hamburger:hover {
            transform: translateY(-50%) scale(1.1);
        }
        
        .hamburger span {
            display: block;
            width: 25px;
            height: 3px;
            background: white;
            margin: 5px 0;
            transition: 0.3s;
        }
        
        /* Page title */
        .page-title {
            text-align: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .page-title:hover {
            transform: scale(1.02);
        }
        
        /* Sidebar menu */
        .sidebar {
            position: fixed;
            left: -300px;
            top: 0;
            width: 300px;
            height: 100vh;
            background: white;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            transition: left 0.3s ease;
            z-index: 1000;
            overflow-y: auto;
        }
        
        .sidebar.open {
            left: 0;
        }
        
        .sidebar-header {
            background: #006C35;
            color: white;
            padding: 20px;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .sidebar-menu {
            list-style: none;
        }
        
        .sidebar-menu li {
            border-bottom: 1px solid #eee;
            transition: all 0.3s ease;
        }
        
        .sidebar-menu a {
            display: block;
            padding: 15px 20px;
            color: #333;
            text-decoration: none;
            transition: all 0.3s ease;
            transform: translateX(0);
        }
        
        .sidebar-menu a:hover {
            background: #f8f9fa;
            transform: translateX(10px);
            color: #006C35;
            font-weight: bold;
        }
        
        .sidebar-menu li:hover {
            background: linear-gradient(to right, #f8f9fa, transparent);
        }
        
        /* Overlay */
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 999;
            display: none;
        }
        
        .overlay.show {
            display: block;
        }
        
        /* Main content */
        .main-content {
            padding: 20px;
        }
        
        /* Profile section */
        .profile-section, .career-test-section, .grades-section, .ai-analysis-section, .suggested-paths-section {
            display: none;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        
        .ai-analysis-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .ai-title {
            font-size: 32px;
            color: #006C35;
            font-weight: bold;
            margin-bottom: 10px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .ai-title:hover {
            transform: scale(1.05);
        }
        
        .ai-subtitle {
            color: #666;
            font-size: 18px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .analysis-content {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid #17a2b8;
            transition: all 0.4s ease;
            transform: translateY(20px);
            opacity: 0;
            animation: slideInUp 0.8s ease forwards;
        }
        
        .analysis-content:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        @keyframes slideInUp {
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        .analysis-title {
            font-size: 26px;
            color: #17a2b8;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
            transition: color 0.3s ease;
        }
        
        .analysis-title:hover {
            color: #006C35;
        }
        
        .analysis-text {
            font-size: 18px;
            line-height: 1.8;
            color: #333;
            text-align: justify;
        }
        
        .analysis-text strong {
            font-size: 20px;
            color: #006C35;
            display: block;
            text-align: center;
            margin: 15px 0;
            transition: all 0.3s ease;
        }
        
        .analysis-text strong:hover {
            transform: scale(1.02);
            color: #17a2b8;
        }
        
        .strength-item, .field-item, .improvement-item {
            padding: 10px;
            margin: 8px 0;
            border-radius: 8px;
            transition: all 0.3s ease;
            background: rgba(0, 108, 53, 0.05);
        }
        
        .strength-item:hover, .field-item:hover, .improvement-item:hover {
            background: rgba(0, 108, 53, 0.1);
            transform: translateX(10px);
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        .coming-soon {
            text-align: center;
            color: #6c757d;
            font-size: 18px;
            margin: 50px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            border: 2px dashed #ddd;
        }
        
        /* Loading overlay */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        
        .loading-text {
            font-size: 24px;
            color: #006C35;
            font-weight: bold;
            margin-bottom: 20px;
        }
        
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #006C35;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .ai-content.blur {
            filter: blur(5px);
            pointer-events: none;
        }
        
        /* Suggested paths styles */
        .paths-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .paths-title {
            font-size: 32px;
            color: #006C35;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .paths-subtitle {
            color: #666;
            font-size: 18px;
        }
        
        .path-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid #17a2b8;
            transition: all 0.4s ease;
            transform: translateY(20px);
            opacity: 0;
            animation: slideInUp 0.8s ease forwards;
        }
        
        .path-card:nth-child(2) { animation-delay: 0.2s; }
        .path-card:nth-child(3) { animation-delay: 0.4s; }
        .path-card:nth-child(4) { animation-delay: 0.6s; }
        
        .path-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .path-header {
            font-size: 24px;
            color: #006C35;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .path-header:hover {
            color: #17a2b8;
            transform: scale(1.02);
        }
        
        .path-details {
            display: grid;
            gap: 20px;
        }
        
        .detail-section {
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 3px solid #006C35;
            transition: all 0.3s ease;
        }
        
        .detail-section:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .detail-title {
            font-size: 18px;
            font-weight: bold;
            color: #006C35;
            margin-bottom: 10px;
        }
        
        .detail-content {
            font-size: 16px;
            color: #333;
            line-height: 1.6;
        }
        
        .companies-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        
        .company-item {
            background: #e8f5e8;
            padding: 8px 12px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            color: #006C35;
            transition: all 0.3s ease;
        }
        
        .company-item:hover {
            background: #006C35;
            color: white;
            transform: scale(1.05);
        }
        
        .field-item-with-button {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 8px 0;
            border-radius: 8px;
            background: rgba(0, 108, 53, 0.05);
            transition: all 0.3s ease;
        }
        
        .field-item-with-button:hover {
            background: rgba(0, 108, 53, 0.1);
            transform: translateX(10px);
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        .field-text {
            flex: 1;
            font-size: 16px;
            color: #333;
        }
        
        .path-button {
            background: #17a2b8;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
        }
        
        .path-button:hover {
            background: #006C35;
            transform: scale(1.05);
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        }
        
        .grades-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .school-info {
            text-align: right;
        }
        
        .student-info {
            text-align: left;
        }
        
        .info-label {
            font-weight: bold;
            color: #006C35;
            font-size: 16px;
            margin-bottom: 5px;
        }
        
        .info-value {
            color: #666;
            font-size: 14px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 3px;
            min-width: 150px;
            display: inline-block;
        }
        
        .grades-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            animation: fadeInUp 0.8s ease;
        }
        
        .grades-table th {
            background: #006C35;
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .grades-table th:hover {
            background: #005028;
            transform: scale(1.02);
        }
        
        .grades-table td {
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #eee;
            transition: all 0.3s ease;
        }
        
        .grades-table tr {
            transition: all 0.3s ease;
        }
        
        .grades-table tr:hover {
            background: #f8f9fa;
            transform: scale(1.02);
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .grade-excellent {
            background: #d4edda;
            color: #155724;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .grade-excellent:hover {
            background: #c3e6cb;
            transform: scale(1.1);
        }
        
        .grade-very-good {
            background: #d1ecf1;
            color: #0c5460;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .grade-very-good:hover {
            background: #bee5eb;
            transform: scale(1.1);
        }
        
        .grade-good {
            background: #fff3cd;
            color: #856404;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .grade-good:hover {
            background: #ffeaa7;
            transform: scale(1.1);
        }
        
        .subject-name {
            text-align: right;
            font-weight: bold;
            color: #333;
            transition: all 0.3s ease;
        }
        
        .subject-name:hover {
            color: #006C35;
            transform: translateX(-5px);
        }
        
        .test-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .test-title {
            font-size: 24px;
            font-weight: bold;
            color: #006C35;
            margin-bottom: 10px;
        }
        
        .test-progress {
            background: #f0f0f0;
            border-radius: 10px;
            height: 8px;
            margin: 20px 0;
        }
        
        .test-progress-bar {
            background: #006C35;
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s;
        }
        
        .question-container {
            display: none;
            text-align: center;
        }
        
        .question-container.active {
            display: block;
        }
        
        .question-text {
            font-size: 18px;
            color: #333;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        
        .question-number {
            color: #006C35;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .answer-options {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .answer-option {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            padding: 15px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.4s ease;
            font-size: 16px;
            transform: translateX(0);
        }
        
        .answer-option:hover {
            background: #e9ecef;
            border-color: #006C35;
            transform: translateX(10px) scale(1.02);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .answer-option.selected {
            background: #006C35;
            color: white;
            border-color: #006C35;
            transform: translateX(15px) scale(1.05);
            box-shadow: 0 8px 20px rgba(0, 108, 53, 0.3);
        }
        
        .test-navigation {
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
        }
        
        .test-btn {
            background: #006C35;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            transform: translateY(0);
        }
        
        .test-btn:hover {
            background: #005028;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 108, 53, 0.4);
        }
        
        .test-btn:active {
            transform: translateY(-1px);
        }
        
        .test-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: translateY(0);
            box-shadow: none;
        }
        
        .results-container {
            display: none;
            text-align: center;
            animation: fadeInScale 0.8s ease;
        }
        
        @keyframes fadeInScale {
            from {
                opacity: 0;
                transform: scale(0.8);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        .result-category {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid #006C35;
            transition: all 0.4s ease;
            transform: translateY(20px);
            opacity: 0;
            animation: slideInUp 0.8s ease 0.3s forwards;
        }
        
        .result-category:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .result-title {
            font-size: 26px;
            color: #006C35;
            font-weight: bold;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        
        .result-title:hover {
            transform: scale(1.02);
            color: #17a2b8;
        }
        
        .result-description {
            font-size: 18px;
            line-height: 1.6;
            color: #333;
        }
        
        .restart-btn {
            background: #6c757d;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 20px;
            transition: all 0.3s ease;
        }
        
        .restart-btn:hover {
            background: #5a6268;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .profile-header {
            display: flex;
            align-items: flex-start;
            gap: 15px;
            margin-bottom: 20px;
            animation: slideInUp 0.8s ease;
        }
        
        .profile-picture {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #e9ecef;
            border: 2px solid #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
            color: #6c757d;
            flex-shrink: 0;
            transition: all 0.4s ease;
        }
        
        .profile-picture:hover {
            transform: scale(1.1) rotate(5deg);
            border-color: #006C35;
            box-shadow: 0 8px 20px rgba(0, 108, 53, 0.2);
        }
        
        .profile-info {
            flex: 1;
            transition: all 0.3s ease;
        }
        
        .profile-info:hover {
            transform: translateX(10px);
        }
        
        .student-name {
            font-size: 24px;
            font-weight: bold;
            color: #006C35;
            margin-bottom: 5px;
            transition: all 0.3s ease;
        }
        
        .student-name:hover {
            color: #17a2b8;
            transform: scale(1.02);
        }
        
        .academic-level {
            font-size: 18px;
            color: #666;
            transition: all 0.3s ease;
        }
        
        .academic-level:hover {
            color: #006C35;
        }
        
        /* Back button */
        .back-btn {
            background: #006C35;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-bottom: 20px;
        }
        
        .back-btn:hover {
            background: #005028;
        }
        
        /* Welcome message */
        .welcome-message {
            text-align: center;
            color: #666;
            font-size: 20px;
            margin-top: 100px;
            transition: all 0.4s ease;
            animation: fadeInUp 1s ease;
        }
        
        .welcome-message:hover {
            color: #006C35;
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <!-- Hamburger menu -->
        <div class="hamburger" onclick="toggleSidebar()">
            <span></span>
            <span></span>
            <span></span>
        </div>
        
        <div class="page-title">طلاب المدارس</div>
    </div>
    
    <!-- Sidebar -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">القائمة</div>
        <ul class="sidebar-menu">
            <li><a href="#" onclick="showProfile()">الملف الشخصي</a></li>
            <li><a href="#" onclick="showCareerTest()">اختبار الميول المهني</a></li>
            <li><a href="#" onclick="showAIAnalysis()">تحليل الذكاء الاصطناعي</a></li>
            <li><a href="#" onclick="showSuggestedPaths()">المسارات المقترحة</a></li>
            <li><a href="#" onclick="showGrades()">درجات الطالب</a></li>
            <li><a href="#" onclick="closeMenu()">الاعدادات</a></li>
        </ul>
    </div>
    
    <!-- Overlay -->
    <div class="overlay" id="overlay" onclick="closeSidebar()"></div>
    
    <!-- Main content -->
    <div class="main-content">
        <!-- Welcome message -->
        <div class="welcome-message" id="welcomeMessage">
            مرحباً بك في صفحة طلاب المدارس<br>
            اضغط على القائمة أعلى اليسار للبدء
        </div>
        
        <!-- Profile section -->
        <div class="profile-section" id="profileSection">
            <div class="profile-header">
                <div class="profile-picture">
                    👤
                </div>
                <div class="profile-info">
                    <div class="student-name">اسم الطالب</div>
                    <div class="academic-level">المرحلة الدراسية</div>
                </div>
            </div>
            <!-- Rest of the content area left empty as requested -->
        </div>
        
        <!-- Career Test section -->
        <div class="career-test-section" id="careerTestSection">
            <div class="test-header">
                <div class="test-title">اختبار الميول المهني</div>
                <div style="color: #666;">اكتشف ميولك المهني من خلال الإجابة على الأسئلة التالية</div>
                <div class="test-progress">
                    <div class="test-progress-bar" id="progressBar"></div>
                </div>
                <div id="progressText">السؤال 1 من 12</div>
            </div>
            
            <!-- Question 1 -->
            <div class="question-container active" id="question1">
                <div class="question-number">السؤال 1</div>
                <div class="question-text">هل تستمتع بحل المسائل الرياضية أو الألغاز التي تحتاج تفكير منطقي؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(1, 'نعم', 2)">نعم</div>
                    <div class="answer-option" onclick="selectAnswer(1, 'أحيانًا', 1)">أحيانًا</div>
                    <div class="answer-option" onclick="selectAnswer(1, 'لا', 0)">لا</div>
                </div>
            </div>
            
            <!-- Question 2 -->
            <div class="question-container" id="question2">
                <div class="question-number">السؤال 2</div>
                <div class="question-text">هل تفضل القيام بأنشطة عملية بيديك (مثل التصليح، الرسم، أو التجارب العلمية)؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(2, 'نعم', 2)">نعم</div>
                    <div class="answer-option" onclick="selectAnswer(2, 'أحيانًا', 1)">أحيانًا</div>
                    <div class="answer-option" onclick="selectAnswer(2, 'لا', 0)">لا</div>
                </div>
            </div>
            
            <!-- Question 3 -->
            <div class="question-container" id="question3">
                <div class="question-number">السؤال 3</div>
                <div class="question-text">هل تشعر بالراحة عند التحدث أمام مجموعة من الناس أو إلقاء عرض؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(3, 'نعم', 2)">نعم</div>
                    <div class="answer-option" onclick="selectAnswer(3, 'أحيانًا', 1)">أحيانًا</div>
                    <div class="answer-option" onclick="selectAnswer(3, 'لا', 0)">لا</div>
                </div>
            </div>
            
            <!-- Question 4 -->
            <div class="question-container" id="question4">
                <div class="question-number">السؤال 4</div>
                <div class="question-text">هل تحب مساعدة الآخرين وحل مشكلاتهم أو تقديم النصائح لهم؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(4, 'نعم', 2)">نعم</div>
                    <div class="answer-option" onclick="selectAnswer(4, 'أحيانًا', 1)">أحيانًا</div>
                    <div class="answer-option" onclick="selectAnswer(4, 'لا', 0)">لا</div>
                </div>
            </div>
            
            <!-- Question 5 -->
            <div class="question-container" id="question5">
                <div class="question-number">السؤال 5</div>
                <div class="question-text">هل تستمتع بالعمل على الكمبيوتر أو استخدام البرامج والتقنيات الجديدة؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(5, 'نعم', 2)">نعم</div>
                    <div class="answer-option" onclick="selectAnswer(5, 'أحيانًا', 1)">أحيانًا</div>
                    <div class="answer-option" onclick="selectAnswer(5, 'لا', 0)">لا</div>
                </div>
            </div>
            
            <!-- Question 6 -->
            <div class="question-container" id="question6">
                <div class="question-number">السؤال 6</div>
                <div class="question-text">هل لديك خيال واسع وتحب كتابة القصص أو رسم لوحات أو إنتاج أفكار إبداعية؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(6, 'نعم', 2)">نعم</div>
                    <div class="answer-option" onclick="selectAnswer(6, 'أحيانًا', 1)">أحيانًا</div>
                    <div class="answer-option" onclick="selectAnswer(6, 'لا', 0)">لا</div>
                </div>
            </div>
            
            <!-- Question 7 -->
            <div class="question-container" id="question7">
                <div class="question-number">السؤال 7</div>
                <div class="question-text">هل تميل أكثر إلى العمل ضمن فريق والتعاون مع الآخرين، أم تفضل العمل لوحدك؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(7, 'مع الفريق', 2)">مع الفريق</div>
                    <div class="answer-option" onclick="selectAnswer(7, 'حسب الموقف', 1)">حسب الموقف</div>
                    <div class="answer-option" onclick="selectAnswer(7, 'لوحدي', 0)">لوحدي</div>
                </div>
            </div>
            
            <!-- Question 8 -->
            <div class="question-container" id="question8">
                <div class="question-number">السؤال 8</div>
                <div class="question-text">هل تهتم بكيفية عمل الأشياء (مثل الآلات، الأجهزة، السيارات) وتحاول فهمها؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(8, 'نعم', 2)">نعم</div>
                    <div class="answer-option" onclick="selectAnswer(8, 'أحيانًا', 1)">أحيانًا</div>
                    <div class="answer-option" onclick="selectAnswer(8, 'لا', 0)">لا</div>
                </div>
            </div>
            
            <!-- Question 9 -->
            <div class="question-container" id="question9">
                <div class="question-number">السؤال 9</div>
                <div class="question-text">هل تستمتع بقراءة الكتب أو البحث عن معلومات جديدة لاكتساب معرفة أوسع؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(9, 'نعم', 2)">نعم</div>
                    <div class="answer-option" onclick="selectAnswer(9, 'أحيانًا', 1)">أحيانًا</div>
                    <div class="answer-option" onclick="selectAnswer(9, 'لا', 0)">لا</div>
                </div>
            </div>
            
            <!-- Question 10 -->
            <div class="question-container" id="question10">
                <div class="question-number">السؤال 10</div>
                <div class="question-text">هل تحب الأنشطة التي تتعلق بالتخطيط والتنظيم، مثل ترتيب جدول أو قيادة مجموعة؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(10, 'نعم', 2)">نعم</div>
                    <div class="answer-option" onclick="selectAnswer(10, 'أحيانًا', 1)">أحيانًا</div>
                    <div class="answer-option" onclick="selectAnswer(10, 'لا', 0)">لا</div>
                </div>
            </div>
            
            <!-- Question 11 -->
            <div class="question-container" id="question11">
                <div class="question-number">السؤال 11</div>
                <div class="question-text">هل تهتم بالبيئة والطبيعة وتحب الأنشطة الخارجية مثل الزراعة أو الرحلات؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(11, 'نعم', 2)">نعم</div>
                    <div class="answer-option" onclick="selectAnswer(11, 'أحيانًا', 1)">أحيانًا</div>
                    <div class="answer-option" onclick="selectAnswer(11, 'لا', 0)">لا</div>
                </div>
            </div>
            
            <!-- Question 12 -->
            <div class="question-container" id="question12">
                <div class="question-number">السؤال 12</div>
                <div class="question-text">إذا خُيّرت بين أن تصنع شيئًا بيدك أو أن تكتب تقريرًا عنه، ماذا تختار؟</div>
                <div class="answer-options">
                    <div class="answer-option" onclick="selectAnswer(12, 'أصنع بيدي', 2)">أصنع بيدي</div>
                    <div class="answer-option" onclick="selectAnswer(12, 'كلاهما', 1)">كلاهما</div>
                    <div class="answer-option" onclick="selectAnswer(12, 'أكتب تقريرًا', 0)">أكتب تقريرًا</div>
                </div>
            </div>
            
            <!-- Results -->
            <div class="results-container" id="resultsContainer">
                <div class="test-title">نتائج اختبار الميول المهني</div>
                <div id="testResults"></div>
                <div style="text-align: center; margin-top: 30px;">
                    <button class="test-btn" onclick="showAIAnalysis()" style="background: #17a2b8; font-size: 18px; padding: 15px 30px; margin-left: 15px;">
                        لتحليل أعمق اضغط هنا
                    </button>
                    <button class="restart-btn" onclick="restartTest()">إعادة الاختبار</button>
                </div>
            </div>
            
            <div class="test-navigation">
                <button class="test-btn" id="prevBtn" onclick="previousQuestion()" disabled>السابق</button>
                <button class="test-btn" id="nextBtn" onclick="nextQuestion()" disabled>التالي</button>
                <button class="test-btn" id="finishBtn" onclick="finishTest()" style="display: none;">إنهاء الاختبار</button>
            </div>
        </div>
        
        <!-- Suggested Paths section -->
        <div class="suggested-paths-section" id="suggestedPathsSection">
            <div class="paths-header">
                <div class="paths-title">🎯 المسارات المقترحة</div>
                <div class="paths-subtitle">خطط دراسية ومسارات مهنية مُصممة خصيصاً لك</div>
            </div>
            
            <!-- Computer Engineering and Programming Path -->
            <div class="path-card">
                <div class="path-header">💻 هندسة الحاسب والبرمجة</div>
                <div class="path-details">
                    <div class="detail-section">
                        <div class="detail-title">📚 ما تدرسه في الجامعة</div>
                        <div class="detail-content">
                            • بكالوريوس هندسة الحاسب أو علوم الحاسب<br>
                            • البرمجة بلغات مختلفة (Python, Java, C++)<br>
                            • هندسة البرمجيات وقواعد البيانات<br>
                            • الشبكات والأمن السيبراني<br>
                            • تطوير التطبيقات والمواقع
                        </div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-title">⏰ مدة الدراسة</div>
                        <div class="detail-content">4 سنوات للحصول على درجة البكالوريوس</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-title">🏢 شركات سعودية للعمل بها</div>
                        <div class="detail-content">
                            <div class="companies-grid">
                                <div class="company-item">STC</div>
                                <div class="company-item">شركة علم</div>
                                <div class="company-item">كريم</div>
                                <div class="company-item">جاهز</div>
                                <div class="company-item">مرسول</div>
                                <div class="company-item">تمارا</div>
                                <div class="company-item">تابي</div>
                                <div class="company-item">نيوم</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- AI and Data Science Path -->
            <div class="path-card">
                <div class="path-header">🤖 الذكاء الاصطناعي وعلوم البيانات</div>
                <div class="path-details">
                    <div class="detail-section">
                        <div class="detail-title">📚 ما تدرسه في الجامعة</div>
                        <div class="detail-content">
                            • بكالوريوس علوم البيانات أو الذكاء الاصطناعي<br>
                            • الرياضيات المتقدمة والإحصاء<br>
                            • تعلم الآلة والتعلم العميق<br>
                            • تحليل البيانات والتصور<br>
                            • البرمجة بـ Python و R<br>
                            • الخوارزميات والشبكات العصبية
                        </div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-title">⏰ مدة الدراسة</div>
                        <div class="detail-content">4 سنوات للبكالوريوس + سنتان للماجستير (مُوصى به)</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-title">🏢 شركات سعودية للعمل بها</div>
                        <div class="detail-content">
                            <div class="companies-grid">
                                <div class="company-item">أرامكو السعودية</div>
                                <div class="company-item">نيوم</div>
                                <div class="company-item">تقنية</div>
                                <div class="company-item">سدايا</div>
                                <div class="company-item">STC</div>
                                <div class="company-item">البنك الأهلي</div>
                                <div class="company-item">شركة علم</div>
                                <div class="company-item">Lean Technologies</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Biomedical Engineering Path -->
            <div class="path-card">
                <div class="path-header">🔬 الهندسة الطبية الحيوية</div>
                <div class="path-details">
                    <div class="detail-section">
                        <div class="detail-title">📚 ما تدرسه في الجامعة</div>
                        <div class="detail-content">
                            • بكالوريوس الهندسة الطبية الحيوية<br>
                            • علوم الحياة والتشريح<br>
                            • الفيزياء الطبية والكيمياء الحيوية<br>
                            • هندسة الأجهزة الطبية<br>
                            • معالجة الإشارات الطبية<br>
                            • التصوير الطبي والذكاء الاصطناعي الطبي
                        </div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-title">⏰ مدة الدراسة</div>
                        <div class="detail-content">5 سنوات للبكالوريوس (تشمل سنة تحضيرية)</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-title">🏢 شركات سعودية للعمل بها</div>
                        <div class="detail-content">
                            <div class="companies-grid">
                                <div class="company-item">أرامكو السعودية</div>
                                <div class="company-item">مدينة الملك عبدالعزيز</div>
                                <div class="company-item">تقنية</div>
                                <div class="company-item">نيوم</div>
                                <div class="company-item">مستشفى الملك فيصل</div>
                                <div class="company-item">شركة علم</div>
                                <div class="company-item">المستشفيات الجامعية</div>
                                <div class="company-item">صيدليات النهدي</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Grades section -->
        <div class="grades-section" id="gradesSection">
            <div class="grades-header">
                <div class="school-info">
                    <div class="info-label">اسم المدرسة</div>
                    <div class="info-value">_________________</div>
                    <br><br>
                    <div class="info-label">المرحلة الدراسية</div>
                    <div class="info-value">_________________</div>
                </div>
                <div class="student-info">
                    <div class="info-label">اسم الطالب</div>
                    <div class="info-value">_________________</div>
                    <br><br>
                    <div class="info-label">رقم الهوية</div>
                    <div class="info-value">_________________</div>
                </div>
            </div>
            
            <table class="grades-table">
                <thead>
                    <tr>
                        <th>المادة</th>
                        <th>الدرجة</th>
                        <th>من</th>
                        <th>التقدير</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="subject-name">التقنية الرقمية</td>
                        <td class="grade-excellent">98</td>
                        <td>100</td>
                        <td class="grade-excellent">ممتاز</td>
                    </tr>
                    <tr>
                        <td class="subject-name">رياضيات</td>
                        <td class="grade-excellent">95</td>
                        <td>100</td>
                        <td class="grade-excellent">ممتاز</td>
                    </tr>
                    <tr>
                        <td class="subject-name">فيزياء</td>
                        <td class="grade-excellent">92</td>
                        <td>100</td>
                        <td class="grade-excellent">ممتاز</td>
                    </tr>
                    <tr>
                        <td class="subject-name">كيمياء</td>
                        <td class="grade-very-good">88</td>
                        <td>100</td>
                        <td class="grade-very-good">جيد جداً</td>
                    </tr>
                    <tr>
                        <td class="subject-name">أحياء</td>
                        <td class="grade-very-good">85</td>
                        <td>100</td>
                        <td class="grade-very-good">جيد جداً</td>
                    </tr>
                    <tr>
                        <td class="subject-name">إسلاميات</td>
                        <td class="grade-very-good">84</td>
                        <td>100</td>
                        <td class="grade-very-good">جيد جداً</td>
                    </tr>
                    <tr>
                        <td class="subject-name">التربية البدنية</td>
                        <td class="grade-good">82</td>
                        <td>100</td>
                        <td class="grade-good">جيد</td>
                    </tr>
                    <tr>
                        <td class="subject-name">لغة عربية</td>
                        <td class="grade-good">80</td>
                        <td>100</td>
                        <td class="grade-good">جيد</td>
                    </tr>
                </tbody>
            </table>
            
            <div style="text-align: center; margin-top: 30px;">
                <button class="test-btn" onclick="showAIAnalysis()" style="background: #17a2b8; font-size: 18px; padding: 15px 30px;">
                    لتحليل درجاتك اضغط هنا
                </button>
            </div>
        </div>
        
        <!-- AI Analysis section -->
        <div class="ai-analysis-section" id="aiAnalysisSection">
            <!-- Loading overlay -->
            <div class="loading-overlay" id="loadingOverlay" style="display: none;">
                <div class="loading-text">يتم التحليل...</div>
                <div class="loading-spinner"></div>
                <div style="margin-top: 20px; color: #666; font-size: 16px;">🤖 الذكاء الاصطناعي يحلل بياناتك</div>
            </div>
            
            <!-- AI Analysis content -->
            <div class="ai-content" id="aiContent">
                <div class="ai-analysis-header">
                    <div class="ai-title">🤖 تحليل الذكاء الاصطناعي</div>
                    <div class="ai-subtitle">تحليل شامل لميولك المهني ودرجاتك الأكاديمية</div>
                </div>
                
                <div class="analysis-content" id="careerAnalysisContent" style="display: none;">
                    <div class="analysis-title">تحليل اختبار الميول المهني</div>
                    <div class="analysis-text" id="careerAnalysisText"></div>
                </div>
                
                <div class="analysis-content" id="gradesAnalysisContent">
                    <div class="analysis-title">تحليل الدرجات الأكاديمية</div>
                    <div class="analysis-text">
                        بناءً على تحليل درجاتك، نلاحظ أنك تبرع في <strong>المواد التقنية والعلمية</strong><br><br>
                        
                        <strong>📊 نقاط القوة:</strong><br>
                        <div class="strength-item">• <strong>التقنية الرقمية (98/100):</strong> تظهر موهبة استثنائية في التكنولوجيا والبرمجة</div>
                        <div class="strength-item">• <strong>الرياضيات (95/100):</strong> قدرات تحليلية ومنطقية متقدمة</div>
                        <div class="strength-item">• <strong>الفيزياء (92/100):</strong> فهم عميق للمفاهيم العلمية والتطبيقية</div><br>
                        
                        <strong>🎯 المجالات المناسبة:</strong><br>
                        <div class="field-item-with-button">
                            <div class="field-text">• هندسة الحاسب والبرمجة</div>
                            <button class="path-button" onclick="showSuggestedPaths()">المسارات المقترحة</button>
                        </div>
                        <div class="field-item-with-button">
                            <div class="field-text">• الذكاء الاصطناعي وعلوم البيانات</div>
                            <button class="path-button" onclick="showSuggestedPaths()">المسارات المقترحة</button>
                        </div>
                        <div class="field-item-with-button">
                            <div class="field-text">• الهندسة الطبية الحيوية</div>
                            <button class="path-button" onclick="showSuggestedPaths()">المسارات المقترحة</button>
                        </div>
                    </div>
                </div>
                
                <div class="coming-soon" id="combinedAnalysisContent" style="display: none;">
                    <div style="font-size: 24px; margin-bottom: 15px;">🔄 تحليل متكامل</div>
                    <div>تم دمج تحليل اختبار الميول المهني مع تحليل الدرجات الأكاديمية لإعطائك صورة شاملة عن مسارك المهني المثالي. يمكنك الآن الاطلاع على المسارات المقترحة للحصول على خطة دراسية ومهنية مفصلة.</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentQuestion = 1;
        let answers = {};
        let testCompleted = false;
        let testResults = null;
        const totalQuestions = 12;
        
        // Load saved test results on page load
        window.addEventListener('load', function() {
            const savedResults = sessionStorage.getItem('careerTestResults');
            if (savedResults) {
                testResults = JSON.parse(savedResults);
                testCompleted = true;
            }
        });
        
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('overlay');
            
            sidebar.classList.toggle('open');
            overlay.classList.toggle('show');
        }
        
        function closeSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('overlay');
            
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
        }
        
        function closeMenu() {
            closeSidebar();
        }
        
        function showProfile() {
            closeSidebar();
            hideAllSections();
            document.getElementById('profileSection').style.display = 'block';
        }
        
        function showCareerTest() {
            closeSidebar();
            hideAllSections();
            document.getElementById('careerTestSection').style.display = 'block';
            
            // If test is completed, show results instead of starting over
            if (testCompleted && testResults) {
                showSavedResults();
            } else {
                resetTest();
            }
        }
        
        function showGrades() {
            closeSidebar();
            hideAllSections();
            document.getElementById('gradesSection').style.display = 'block';
        }
        
        function showAIAnalysis() {
            closeSidebar();
            hideAllSections();
            document.getElementById('aiAnalysisSection').style.display = 'block';
            
            // Show loading overlay
            const loadingOverlay = document.getElementById('loadingOverlay');
            const aiContent = document.getElementById('aiContent');
            
            loadingOverlay.style.display = 'flex';
            aiContent.classList.add('blur');
            
            // Hide content initially
            document.getElementById('careerAnalysisContent').style.display = 'none';
            document.getElementById('combinedAnalysisContent').style.display = 'none';
            
            // Simulate AI analysis loading for 5 seconds
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
                aiContent.classList.remove('blur');
                
                // Show career analysis if test was completed
                if (testCompleted && testResults) {
                    document.getElementById('careerAnalysisContent').style.display = 'block';
                    document.getElementById('careerAnalysisText').innerHTML = generateCareerAnalysisText(testResults);
                    document.getElementById('combinedAnalysisContent').style.display = 'block';
                }
            }, 5000);
        }
        
        function showSuggestedPaths() {
            console.log('showSuggestedPaths called'); // Debug line
            closeSidebar();
            hideAllSections();
            const pathsSection = document.getElementById('suggestedPathsSection');
            if (pathsSection) {
                pathsSection.style.display = 'block';
                console.log('Suggested paths section shown'); // Debug line
            } else {
                console.error('suggestedPathsSection not found'); // Debug line
            }
        }
        
        function hideAllSections() {
            document.getElementById('welcomeMessage').style.display = 'none';
            document.getElementById('profileSection').style.display = 'none';
            document.getElementById('careerTestSection').style.display = 'none';
            document.getElementById('gradesSection').style.display = 'none';
            document.getElementById('aiAnalysisSection').style.display = 'none';
            document.getElementById('suggestedPathsSection').style.display = 'none';
        }
        
        function resetTest() {
            currentQuestion = 1;
            answers = {};
            
            // Hide all questions and show first
            for (let i = 1; i <= totalQuestions; i++) {
                document.getElementById(`question${i}`).classList.remove('active');
                clearAnswerSelection(i);
            }
            document.getElementById('question1').classList.add('active');
            
            // Reset navigation
            updateNavigation();
            updateProgress();
            
            // Hide results and show questions
            document.getElementById('resultsContainer').style.display = 'none';
            document.querySelector('.test-header').style.display = 'block';
            document.querySelector('.test-navigation').style.display = 'flex';
        }
        
        function showSavedResults() {
            // Hide questions and navigation
            for (let i = 1; i <= totalQuestions; i++) {
                document.getElementById(`question${i}`).classList.remove('active');
            }
            document.querySelector('.test-header').style.display = 'none';
            document.querySelector('.test-navigation').style.display = 'none';
            
            // Show saved results
            document.getElementById('testResults').innerHTML = testResults.html;
            document.getElementById('resultsContainer').style.display = 'block';
        }
        
        function selectAnswer(questionNum, answer, score) {
            // Store the answer
            answers[questionNum] = { answer: answer, score: score };
            
            // Update UI
            const options = document.querySelectorAll(`#question${questionNum} .answer-option`);
            options.forEach(option => option.classList.remove('selected'));
            event.target.classList.add('selected');
            
            // Enable next button
            updateNavigation();
        }
        
        function clearAnswerSelection(questionNum) {
            const options = document.querySelectorAll(`#question${questionNum} .answer-option`);
            options.forEach(option => option.classList.remove('selected'));
        }
        
        function nextQuestion() {
            if (currentQuestion < totalQuestions) {
                document.getElementById(`question${currentQuestion}`).classList.remove('active');
                currentQuestion++;
                document.getElementById(`question${currentQuestion}`).classList.add('active');
                updateNavigation();
                updateProgress();
            }
        }
        
        function previousQuestion() {
            if (currentQuestion > 1) {
                document.getElementById(`question${currentQuestion}`).classList.remove('active');
                currentQuestion--;
                document.getElementById(`question${currentQuestion}`).classList.add('active');
                updateNavigation();
                updateProgress();
            }
        }
        
        function updateNavigation() {
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            const finishBtn = document.getElementById('finishBtn');
            
            // Previous button
            prevBtn.disabled = currentQuestion === 1;
            
            // Next/Finish buttons
            const hasAnswer = answers[currentQuestion];
            
            if (currentQuestion === totalQuestions) {
                nextBtn.style.display = 'none';
                finishBtn.style.display = hasAnswer ? 'inline-block' : 'none';
            } else {
                nextBtn.style.display = 'inline-block';
                nextBtn.disabled = !hasAnswer;
                finishBtn.style.display = 'none';
            }
        }
        
        function updateProgress() {
            const progress = (currentQuestion / totalQuestions) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
            document.getElementById('progressText').textContent = `السؤال ${currentQuestion} من ${totalQuestions}`;
        }
        
        function finishTest() {
            // Calculate scores
            const scores = {
                scientific: 0,    // Questions 1,2,5,8
                social: 0,        // Questions 3,4,7,10
                creative: 0,      // Questions 6,12
                practical: 0      // Questions 2,11
            };
            
            // Scientific/Technical (1,2,5,8)
            [1,2,5,8].forEach(q => {
                if (answers[q]) scores.scientific += answers[q].score;
            });
            
            // Social/Leadership (3,4,7,10)
            [3,4,7,10].forEach(q => {
                if (answers[q]) scores.social += answers[q].score;
            });
            
            // Creative/Artistic (6,12)
            [6,12].forEach(q => {
                if (answers[q]) scores.creative += answers[q].score;
            });
            
            // Practical/Natural (2,11)
            [2,11].forEach(q => {
                if (answers[q]) scores.practical += answers[q].score;
            });
            
            // Find highest score
            const maxScore = Math.max(scores.scientific, scores.social, scores.creative, scores.practical);
            let resultCategory = '';
            
            if (scores.scientific === maxScore) {
                resultCategory = 'scientific';
            } else if (scores.social === maxScore) {
                resultCategory = 'social';
            } else if (scores.creative === maxScore) {
                resultCategory = 'creative';
            } else {
                resultCategory = 'practical';
            }
            
            // Show results and save them
            showResults(resultCategory, scores);
        }
        
        function showResults(category, scores) {
            const results = {
                scientific: {
                    title: 'الميول العلمي / التقني 🧪💻',
                    description: 'أنت شخص تحب <strong>المنطق والتجربة والاكتشاف</strong>. تستمتع بحل المشكلات وفهم كيف تعمل الأشياء. ميولك هذا يناسب مجالات مثل: <strong>الهندسة، الطب، علوم الحاسب، التكنولوجيا، والبحث العلمي</strong>. شخصيتك تميل للتفكير التحليلي وتحب المعرفة الدقيقة.'
                },
                social: {
                    title: 'الميول الاجتماعي / القيادي 🤝👨‍💼',
                    description: 'أنت شخص <strong>اجتماعي وتحب التفاعل مع الناس</strong>. عندك قدرة على التواصل والتأثير في الآخرين، وغالبًا تحب مساعدة من حولك. ميولك هذا يناسب مجالات مثل: <strong>الإدارة، التعليم، الإعلام، الخدمة الاجتماعية، والسياسة</strong>. شخصيتك قيادية وتعرف كيف تنظم وتوجه مجموعة.'
                },
                creative: {
                    title: 'الميول الإبداعي / الفني 🎨✍️🎶',
                    description: 'أنت شخص <strong>خيالك واسع وتحب التعبير عن نفسك بأسلوب مميز</strong>. عندك حس جمالي وتستمتع بالفنون أو الكتابة أو الابتكار. ميولك هذا يناسب مجالات مثل: <strong>الفن، التصميم، الإعلام الإبداعي، الأدب، المسرح، الموسيقى</strong>. شخصيتك حساسة، مبتكرة، وتحب أن تترك بصمتك الخاصة.'
                },
                practical: {
                    title: 'الميول العملي / الطبيعي 🌍🔧',
                    description: 'أنت شخص تحب <strong>العمل بيدك والتفاعل مع الطبيعة أو الأشياء الملموسة</strong>. تستمتع بالأنشطة الخارجية، ولديك صبر وتجربة عملية. ميولك يناسب مجالات مثل: <strong>الزراعة، الميكانيكا، البناء، الجغرافيا، والبيئة</strong>. شخصيتك عملية، صبورة، وتفضل الأفعال على الأقوال.'
                }
            };
            
            const result = results[category];
            const resultsHtml = `
                <div class="result-category">
                    <div class="result-title">${result.title}</div>
                    <div class="result-description">${result.description}</div>
                </div>
                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                    <strong>نتائج التفصيلية:</strong><br>
                    العلمي/التقني: ${scores.scientific} نقطة<br>
                    الاجتماعي/القيادي: ${scores.social} نقطة<br>
                    الإبداعي/الفني: ${scores.creative} نقطة<br>
                    العملي/الطبيعي: ${scores.practical} نقطة
                </div>
            `;
            
            // Save results to session storage
            testResults = {
                category: category,
                scores: scores,
                html: resultsHtml
            };
            testCompleted = true;
            sessionStorage.setItem('careerTestResults', JSON.stringify(testResults));
            
            document.getElementById('testResults').innerHTML = resultsHtml;
            document.getElementById('resultsContainer').style.display = 'block';
            document.querySelector('.test-header').style.display = 'none';
            document.querySelector('.test-navigation').style.display = 'none';
            
            // Hide all questions
            for (let i = 1; i <= totalQuestions; i++) {
                document.getElementById(`question${i}`).classList.remove('active');
            }
        }
        
        function generateCareerAnalysisText(results) {
            const categoryTexts = {
                scientific: 'تحليل الذكاء الاصطناعي يؤكد أن <strong>ميولك العلمي والتقني</strong> يتماشى بشكل مثالي مع درجاتك المتميزة في التقنية الرقمية والرياضيات والفيزياء. هذا التطابق يشير إلى مسار مهني واعد في مجالات الهندسة والتكنولوجيا.',
                social: 'تحليل الذكاء الاصطناعي يشير إلى أن <strong>ميولك الاجتماعي والقيادي</strong> يمكن أن يكون نقطة قوة في المجالات التقنية أيضاً، خاصة في إدارة المشاريع التقنية والتواصل مع الفرق.',
                creative: 'تحليل الذكاء الاصطناعي يظهر أن <strong>ميولك الإبداعي</strong> مع قدراتك التقنية القوية يفتح لك آفاقاً في مجالات التصميم التقني والإعلام الرقمي والفنون التفاعلية.',
                practical: 'تحليل الذكاء الاصطناعي يؤكد أن <strong>ميولك العملي</strong> مع تفوقك في المواد العلمية يجعلك مناسباً للهندسة التطبيقية والمجالات التقنية العملية.'
            };
            
            return categoryTexts[results.category] || 'تحليل شامل لميولك المهني بناءً على نتائج الاختبار.';
        }
        
        function restartTest() {
            // Clear saved results
            testCompleted = false;
            testResults = null;
            sessionStorage.removeItem('careerTestResults');
            
            resetTest();
        }
    </script>
</body>
</html>
'''

# Simple page template for individual pages
SIMPLE_PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: #F5F5DC;
            margin: 0;
            padding: 40px;
            min-height: 100vh;
        }
        .back-btn {
            background: #006C35;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .back-btn:hover {
            background: #005028;
        }
    </style>
</head>
<body>
    <button onclick="window.location.href='/'" class="back-btn">العودة الى الرئيسية</button>
    <h1 style="text-align: center; color: #006C35; margin-top: 100px;">{{page_name}}</h1>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(SELECTION_TEMPLATE)

@app.route('/auth')
def auth():
    return render_template_string(AUTH_TEMPLATE)

@app.route('/first')
def first_page():
    return render_template_string(SCHOOL_PAGE_TEMPLATE)

@app.route('/second')  
def second_page():
    return render_template_string(SIMPLE_PAGE_TEMPLATE, title="طلاب الجامعة", page_name="صفحة طلاب الجامعة")

@app.route('/third')
def third_page():
    return render_template_string(SIMPLE_PAGE_TEMPLATE, title="قطاع التعليم", page_name="صفحة قطاع التعليم")

@app.route('/verify_id', methods=['POST'])
def verify_id():
    data = request.get_json()
    id_number = data.get('id_number', '').strip()
    
    if not id_number or len(id_number) != 10:
        return jsonify({'success': False, 'error': 'رقم الهوية يجب أن يكون 10 أرقام'})
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT phone_number FROM users WHERE id_number = ?', (id_number,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        phone = result[0]
        # Mask phone number (show last 4 digits)
        masked_phone = '*' * (len(phone) - 4) + phone[-4:]
        return jsonify({'success': True, 'masked_phone': masked_phone})
    else:
        return jsonify({'success': False, 'error': 'رقم الهوية غير مسجل في النظام'})

@app.route('/verify_sms', methods=['POST'])
def verify_sms():
    data = request.get_json()
    id_number = data.get('id_number', '').strip()
    sms_code = data.get('sms_code', '').strip()
    
    # Validation
    if not sms_code:
        return jsonify({'success': False, 'error': 'يرجى إدخال رمز التحقق'})
    
    if len(sms_code) != 4:
        return jsonify({'success': False, 'error': 'رمز التحقق يجب أن يكون 4 أرقام'})
    
    if not sms_code.isdigit():
        return jsonify({'success': False, 'error': 'رمز التحقق يجب أن يحتوي على أرقام فقط'})
    
    if not id_number:
        return jsonify({'success': False, 'error': 'خطأ في رقم الهوية'})
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT sms_code FROM users WHERE id_number = ?', (id_number,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == sms_code:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'رمز التحقق غير صحيح'})

if __name__ == '__main__':
    # تهيئة قاعدة البيانات عند التشغيل
    init_database()
    
    # هذا الجزء ضروري جداً لكي يعمل الرابط على Render
    import os
    port = int(os.environ.get('PORT', 5000))
    
    # تشغيل التطبيق على المنفذ الصحيح والعنوان العام
    app.run(host='0.0.0.0', port=port)
