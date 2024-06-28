const translations = {
    en: {
        headerTitle: "Welcome to Doctor Portal, Your Medical Home on the Web",
        headerSubtitle: "Your one-stop solution for managing your medical records.",
        formTitleLogin: "Log into Doctor Portal",
        formTitleReset: "Reset Your Password",
        emailLabel: "Email",
        passwordLabel: "Password",
        newPasswordLabel: "New Password",
        forgotPasswordLink: "Forgot password?",
        loginButton: "LOG IN",
        resetButton: "Reset Password",
        footerText: "&copy; 2024 Lymphoma Classification, LC v1.0",
        siteMapLink: "Site Map",
        privacyPolicyLink: "Privacy Policy",
        mobileSiteLink: "Mobile Site",
        languageLabel: "Language:"
    },
    ar: {
        headerTitle: "مرحبًا بكم في بوابة الطبيب، منزلك الطبي على الويب",
        headerSubtitle: "حل شامل لإدارة سجلاتك الطبية.",
        formTitleLogin: "تسجيل الدخول إلى بوابة الطبيب",
        formTitleReset: "إعادة تعيين كلمة المرور الخاصة بك",
        emailLabel: "البريد الإلكتروني",
        passwordLabel: "كلمة المرور",
        newPasswordLabel: "كلمة المرور الجديدة",
        forgotPasswordLink: "هل نسيت كلمة المرور؟",
        loginButton: "تسجيل الدخول",
        resetButton: "إعادة تعيين كلمة المرور",
        footerText: "&copy; 2024 تصنيف اللمفوما، LC v1.0",
        siteMapLink: "خريطة الموقع",
        privacyPolicyLink: "سياسة الخصوصية",
        mobileSiteLink: "الموقع المحمول",
        languageLabel: "اللغة:"
    }
};

function changeLanguage() {
    const language = document.getElementById('language').value;
    document.getElementById('header-title').innerText = translations[language].headerTitle;
    if (document.getElementById('header-subtitle')) {
        document.getElementById('header-subtitle').innerText = translations[language].headerSubtitle;
    }
    if (document.getElementById('form-title')) {
        const formTitle = document.getElementById('form-title');
        if (formTitle.innerText.includes("Log into")) {
            formTitle.innerText = translations[language].formTitleLogin;
        } else {
            formTitle.innerText = translations[language].formTitleReset;
        }
    }
    document.getElementById('email-label').innerText = translations[language].emailLabel;
    if (document.getElementById('password-label')) {
        document.getElementById('password-label').innerText = translations[language].passwordLabel;
    }
    if (document.getElementById('new_password')) {
        document.getElementById('password-label').innerText = translations[language].newPasswordLabel;
    }
    if (document.getElementById('forgot-password-link')) {
        document.getElementById('forgot-password-link').innerText = translations[language].forgotPasswordLink;
    }
    if (document.getElementById('login-button')) {
        document.getElementById('login-button').innerText = translations[language].loginButton;
    }
    if (document.getElementById('reset-button')) {
        document.getElementById('reset-button').innerText = translations[language].resetButton;
    }
    document.getElementById('footer-text').innerHTML = translations[language].footerText;
    document.getElementById('site-map-link').innerText = translations[language].siteMapLink;
    document.getElementById('privacy-policy-link').innerText = translations[language].privacyPolicyLink;
    document.getElementById('mobile-site-link').innerText = translations[language].mobileSiteLink;
    document.getElementById('language-label').innerText = translations[language].languageLabel;
}